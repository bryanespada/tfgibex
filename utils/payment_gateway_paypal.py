from django.http import JsonResponse
from logs.views import log
from appmodels.models import Product, Subscription
from users.models import CustomUser
import json
from django.utils import timezone

from utils.functions import write_in_log_file

payment_gateway = "Paypal"

def paypal_handle_event(request, event_actions):
    payload = json.loads(request.body)
    event_type = payload['event_type']

    if event_type in event_actions:
        event_handler = event_actions[event_type]
        response, details = event_handler(request, payload)
        return JsonResponse({'message': details}, status=response)
    else:
        response, details = 500, f"The event {event_type} is not being processed."
        log_event_paypal("not processed", 409, request, payload, details, subscription_id)
        return JsonResponse({'message': 'Error'}, status=500)

# PayPal Event Handlers
def paypal_handle_subscription_created(request, payload):
    # Handling PayPal subscription creation
    subscription_id = payload['resource']['id'] # Subscription Paypal id
    plan_id = payload['resource']['plan_id'] # Save plan id to match with product
    user_id = payload['resource']['custom_id'] # Django user id to match subscription with them 

    try: 
        user = CustomUser.objects.get(id=user_id)
    except:
        response, details= 500, f"Paypal user #{user_id} does not exist in the application"
        log_event_paypal("create", 409, request, payload, details, subscription_id)

    product = Product.objects.get(paypal_subscription_id=plan_id) # Get selected product
    start_date, _ = product.get_period


    try:
        subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
        response, details = 500, f"Subscription #{subscription.id} already exists"
        log_event_paypal("create", 409, request, payload, details, subscription_id)

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
        log_event_paypal("create", 201, request, payload, details, subscription_id)
    
    except Subscription.MultipleObjectsReturned:
        response, details= 500, f"Multiple subscriptions with id #{subscription.id}"
        log_event_paypal("create", 409, request, payload, details, subscription_id)

    return response, details

def paypal_handle_subscription_activated(request, payload):
    # Handling PayPal subscription activate
    subscription_id = payload['resource']['id'] # Subscription Paypal id
    payment_subscription_id = payload['resource']['plan_id'] # Save plan id to match with product

    product= Product.objects.get(paypal_subscription_id=payment_subscription_id) # Get the produt to obtain the due date
    _, due_date= product.get_period
    
    subscription= Subscription.objects.get(payment_subscription_id=subscription_id)
    subscription.status = 'ACTIVE' # Set subscription as Active
    subscription.due_date = due_date  # Update due date
    subscription.save()

    response, details= 200, f"The subscription #{subscription.id} is been activated"
    log_event_paypal("activate", 200, request, payload, details, subscription_id)
    
    return response, details

def paypal_handle_payment_completed(request, payload):
    # Handling PayPal payment complete
    subscription_id = payload['resource']['billing_agreement_id'] # Subscription Paypal id
    amount = payload['resource']['amount']['total'] # Total price paid
    
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
    subscription.amount = amount
    if subscription.status == 'HIDDEN': # Change only in case of being started but not confirmed
        subscription.status= 'PENDING'
    else:
        subscription.status= 'ACTIVE'
        subscription.save()
    
    response, details= 200, f"The payment for the subscription #{subscription.id} has been completed"
    log_event_paypal("payment", 200, request, payload, details, subscription_id)
    
    return response, details

def paypal_handle_subscription_cancelled(request, payload):
    # Handling PayPal subscription cancel
    subscription_id = payload['resource']['id'] # Subscription Paypal id
              
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
    subscription.status = 'CANCELED'
    subscription.save()

    response, details= 200, f"The subscription #{subscription.id} has been canceled"
    log_event_paypal("cancel", 200, request, payload, details, subscription_id)

    return response, details

def paypal_handle_subscription_updated(request, payload):
    #  Handling PayPal subscription update
    subscription_id= payload['resource']['id'] # Subscription Paypal id
        
    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
    plan_id= subscription.paypal_subscription_id
        
    product= Product.objects.get(paypal_subscription_id=plan_id)
    _, due_date= product.get_period

    subscription.status = 'ACTIVE'
    subscription.due_date = due_date
    subscription.save()
    
    response, details= 200, f"The the subscription #{subscription.id} has been renewed"
    log_event_paypal("renew", 200, request, payload, details, subscription_id)

    return response, details

def paypal_handle_subscription_payment_failed(request, payload):
    subscription_id= payload['resource']['id'] # Subscription Paypal id

    subscription = Subscription.objects.get(payment_subscription_id=subscription_id)
    subscription.status = 'PAYMENT ERROR'
    subscription.save()

    response, details= 200, f"The the subscription #{subscription.id} has been renewed"
    log_event_paypal("payment error", 200, request, payload, details, subscription_id)
    return response, details

def log_event_paypal(action, status, request, payload, details, subscription_payment_id):
    event_type = payload['event_type']
    payload = json.dumps(payload, indent=4)

    user= None
    user_id= None
    subscription= None
    product= None

    if subscription_payment_id: 
        subscription = Subscription.objects.get(payment_subscription_id=subscription_payment_id)
        plan_id= subscription.payment_product_id

        if subscription.user:
            user_id= subscription.user.id
            user = CustomUser.objects.get(id=user_id)

        if subscription.payment_subscription_id:
            subscription_payment_id= subscription.payment_subscription_id

    if plan_id: 
        product= Product.objects.get(id=plan_id)

    write_in_log_file(f"Event {event_type}")
    write_in_log_file(f"Subcription payment id: {subscription_payment_id}")
    write_in_log_file(f"Plan id: {plan_id}")

    payment_gateway_details={
        "paypal_event_type": event_type,
        "paypal_subscription_id": subscription_payment_id,
        "paypal_plan_id": plan_id
    }
    
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
    write_in_log_file(f"Finished: {plan_id}\n\n")
    

    