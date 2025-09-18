from django.http import JsonResponse
from logs.views import log
from appmodels.models import Product, Subscription
from users.models import CustomUser
import json
from django.utils import timezone
payment_gateway = "Stripe"

def stripe_handle_event(request, event_actions):
    payload = json.loads(request.body)
    event_type = payload['type']

    if event_type in event_actions:
        response, details = event_actions[event_type](request, payload)
        return JsonResponse({'message': details}, status=response)
    else:
        response, details = 200, f"The event {event_type} is not being processed."
        log_event_stripe("not processed", 409, request, payload, details, None, None, None)
        return JsonResponse({'message': 'Error'}, status=200)

def stripe_handle_subscription_updated(request, payload):
    subscription_id = payload['data']['object']['id']
    stripe_subscription_id = payload['data']['object']['items']['data'][0]['plan']['id']
    invoice_id = payload['data']['object']['latest_invoice']
    
    product = Product.objects.get(stripe_subscription_id=stripe_subscription_id)
    plan_id= product.id
    start_date, _ = product.get_period

    user= None

    try:
        subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
        response, details = 500, f"Subscription #{subscription.id} already exists"
        log_event_stripe("create", 409, request, payload, details, subscription_id, plan_id, invoice_id)
    except Subscription.DoesNotExist:
        subscription = Subscription.objects.create(
            user=user, 
            payment_datetime=timezone.now(),
            payment_method=payment_gateway,
            payment_product_id=product.id,
            payment_subscription_id=subscription_id,
            start_date=start_date,
            due_date=start_date,
            status='HIDDEN'
        )
        response, details= 200, f"Subscription #{subscription.id} created"
        log_event_stripe("create", 201, request, payload, details, subscription_id, plan_id, invoice_id)

    except Subscription.MultipleObjectsReturned:
        response, details= 500, f"Multiple subscriptions with id #{subscription.id}"
        log_event_stripe("create", 409, request, payload, details, subscription_id, plan_id, invoice_id)
        
    return response, details


def stripe_handle_invoice_paid(request, payload):

    subscription_id= payload['data']['object']['subscription']
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
    amount_str = payload['data']['object']['lines']['data'][0]['plan']['amount']
    amount = (float(amount_str)) /100

    subscription.amount= amount
    subscription.save()

    plan_id= subscription.payment_product_id

    response, details= 200, f"The payment for the subscription #{subscription.id} has been completed"
    log_event_stripe("payment", 200, request, payload, details, subscription_id, plan_id, None)

    return response, details


def stripe_handle_checkout_session_completed(request, payload):

    subscription_id= payload['data']['object']['subscription']
    stripe_subscription_id= payload['data']['object']['metadata']['plan_id']
    user_id= int(payload['data']['object']['metadata']['user_id'])

    invoice_id= None

    subscription= Subscription.objects.get(payment_subscription_id=subscription_id)
    product= Product.objects.get(stripe_subscription_id=stripe_subscription_id)
    plan_id= product.id

    user= CustomUser.objects.get(id=user_id)

    _, due_date= product.get_period
    
    subscription.status= 'ACTIVE' # Set subscription as Active
    subscription.due_date= due_date
    subscription.user= user

    subscription.save() # Update subscription object

    response, details= 500, f"The subscription #{subscription.id} is been activated"
    log_event_stripe("activate", 200, request, payload, details, subscription_id, plan_id, invoice_id)

    return response, details

def stripe_handle_payment_failed(request, payload):
    subscription_id = payload['data']['object']['subscription']
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
    subscription.status = 'PAYMENT ERROR'
    subscription.save()

    plan_id = subscription.paypal_subscription_id
    invoice_id= None

    response, details= 200, f"The subscription #{subscription.id} has encountered a payment error"
    log_event_stripe("payment error", 200, request, payload, details, subscription_id, plan_id, invoice_id)

    return response, details


def stripe_handle_subscription_deleted(request, payload):
    subscription_id= payload['data']['object']['id']
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
    subscription.status = 'CANCELED'
    subscription.save()

    plan_id = subscription.paypal_subscription_id
    invoice_id= None

    response, details= 200, f"The subscription #{subscription.id} has been canceled",
    log_event_stripe("cancel", 200, request, payload, details, subscription_id, plan_id, invoice_id)

    return response, details

def log_event_stripe(action, status, request, payload, details, subscription_id, plan_id, invoice_id):
    event_type= payload['type']

    user= None
    user_id= None
    subscription= None
    product= None
    subscription_payment_id= None
    

    if subscription_id: 
        subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
        
        if subscription.user:
            user_id= subscription.user.id
            user = CustomUser.objects.get(id=user_id)

        if subscription.payment_subscription_id:
            subscription_payment_id= subscription.payment_subscription_id

    if plan_id: 
        product= Product.objects.get(id=plan_id)

    payment_gateway_details= {
        "stripe_event_type": event_type,
        "stripe_plan_id": subscription_payment_id,
        "stripe_subscription_id": subscription_id,
        "stripe_invoice_id": invoice_id,
    }
    payment_gateway_details= json.dumps(payment_gateway_details, indent=4)

    log(request, "SubscriptionLog", {
        "action_type": action, 
        "status": status, 
        "details": details, 
        "payment_gateway": payment_gateway, 
        "product": product, 
        "receptor": user, 
        "subscription": subscription,
        "payment_gateway_details": payment_gateway_details,
        "payload": payload
    })