from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.decorators import login_required 
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from .forms import CustomUserCreationForm, CustomUserEditForm, CustomAuthenticationForm
from .models import CustomUser
from appmodels.models import GeneralConfig, Product, Subscription
from paypal.standard.forms import PayPalPaymentsForm
from utils.functions import get_client_geolocation
from django.conf import settings
import requests
from django.contrib import messages
import jwt
import os
from mimetypes import guess_extension
import uuid
from logs.views import log
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from datetime import timedelta
from utils.functions import write_in_log_file
import json
from django.db.models import Q
import stripe
import random

from utils.payment_gateway_paypal import (
    paypal_handle_event,
    paypal_handle_subscription_created,
    paypal_handle_subscription_activated,
    paypal_handle_payment_completed,
    paypal_handle_subscription_cancelled,
    paypal_handle_subscription_updated,
    paypal_handle_subscription_payment_failed
)

from utils.payment_gateway_stripe import (
    stripe_handle_event,
    stripe_handle_subscription_updated,
    stripe_handle_invoice_paid,
    stripe_handle_checkout_session_completed,
    stripe_handle_payment_failed,
    stripe_handle_subscription_deleted
)



PAYPAL_API_URL = "https://api-m.sandbox.paypal.com/"


def access(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # Check if user is already logged
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administration').exists():
            log(request, "UserLog", {"action_type":"read", "status":302, "details":"Admin already logged", "change_by_admin":False})
            return redirect('/administration/dashboard')
        else:
            log(request, "UserLog", {"action_type":"read", "status":302, "details":"Non privileged user already logged", "change_by_admin":False})
            return redirect('/app/dashboard')

    if request.method == "POST":
        # Trying signin
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username_form = form.cleaned_data.get('username')
            password_form = form.cleaned_data.get('password')
            user = authenticate(username=username_form, password=password_form)

            if user is not None:
                login(request, user)
                if user.groups.filter(name='Administration').exists():
                    log(request, "UserLog", {"action_type":"read", "status":200, "details":"Granted access as admin through credentials", "change_by_admin":False})
                    return redirect('/administration/dashboard')
                else:
                    log(request, "UserLog", {"action_type":"read", "status":200, "details":"Granted access as non privileged user through credentials", "change_by_admin":False})
                    return redirect('/app/dashboard')

            log(request, "UserLog", {"action_type":"read", "status":400, "details":"Error trying login", "change_by_admin":False})
        else:
            log(request, "UserLog", {"action_type":"read", "status":403, "details":"Invalid login form", "change_by_admin":False})
            
        context['errors'] = form.errors

        context["signin_message"] = "All fields are required."


    # No POST, new form
    form = CustomAuthenticationForm()
    form.fields['username'].widget.attrs.update({'class': 'form-control','placeholder':'Email','type':'email'})
    form.fields['password'].widget.attrs.update({'class': 'form-control','placeholder':'Password','type':'password'})
    context["form"] = form

    log(request, "UserLog", {"action_type":"read", "status":200, "details":"Load access page", "change_by_admin":False})

    return render(request, "users/unlogged/access.html", context=context)


def register(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)

    # Check if user is already logged
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Administration').exists():
            log(request, "UserLog", {"action_type":"create", "status":302, "details":"Admin already logged", "change_by_admin":False})
            return redirect('/administration/dashboard')
        else:
            log(request, "UserLog", {"action_type":"create", "status":302, "details":"Non privileged user already logged", "change_by_admin":False})
            return redirect('/app/dashboard')

    if request.method == "POST":
        # Trying signup
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()  # Save registered user
            log(request, "UserLog", {"action_type":"create", "status":200, "details":"Create user through credentials", "change_by_admin":False, "new_user":new_user})
            return redirect('/')
        else:
            log(request, "UserLog", {"action_type":"create", "status":400, "details":"Create user", "change_by_admin":False})
            context["signup_message"] = "All fields are required."
            context["errors"] = form.errors
    
        context['errors'] = form.errors

    form = CustomUserCreationForm()
    form.fields['username'].widget.attrs.update({'class': 'form-control','placeholder':'Email','type':'email'})
    form.fields['password1'].widget.attrs.update({'class': 'form-control','placeholder':'Password','type':'password'})
    form.fields['password2'].widget.attrs.update({'class': 'form-control','placeholder':'Retype password','type':'password'})
    form.fields['first_name'].widget.attrs.update({'class': 'form-control','placeholder':'Name','type':'text'})
    context['form'] = form

    log(request, "UserLog", {"action_type":"read", "status":200, "details":"Load register", "change_by_admin":False})
    return render(request, "users/unlogged/register.html", context=context)
    

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/unlogged/password_reset.html'
    email_template_name = 'users/unlogged/password_reset_email.html'
    subject_template_name = 'users/unlogged/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('access')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = get_object_or_404(GeneralConfig, id=1)
        return context


def exit(request):
    logout(request)
    return redirect('/')


@login_required(login_url="/users/access")
def profile(request):
    custom_user = get_object_or_404(CustomUser, id=request.user.id)
    context = {}
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, request.FILES, instance=custom_user)
        if form.is_valid():
            custom_user.save()
            log(request, "UserLog", {"action_type":"update", "status":200, "details":"Updated profile", "change_by_admin":False})
            messages.success(request, f"User profile successfully updated")
            return redirect('/users/profile')
        else:
            log(request, "UserLog", {"action_type":"update", "status":400, "details":"Error updating profile", "change_by_admin":False})
            context['errors'] = form.errors

    form = CustomUserEditForm(instance=custom_user)
    form.fields['pic'].widget.attrs.update({'class': 'form-control'})
    form.fields['username'].widget.attrs.update({'class': 'form-control','placeholder':'Email','type':'email'})
    form.fields['first_name'].widget.attrs.update({'class': 'form-control','placeholder':'Name','type':'text'})
    form.fields['last_name'].widget.attrs.update({'class': 'form-control','placeholder':'Name','type':'text'})
    
    context['form'] = form
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "UserLog", {"action_type":"read", "status":200, "details":"Load profile", "change_by_admin":False})
    return render (request, "users/logged/profile.html", context)


@login_required(login_url="/users/access")
def subscription(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    context['products'] = Product.objects.filter(public=True).order_by('price')
    context['subscriptions'] = Subscription.objects.filter(user=request.user).exclude(status='HIDDEN').order_by('-payment_datetime')
    context['today'] = timezone.now() 

    # Check if current user has an active subscription
    today = timezone.now().date()
    active_subscription = Subscription.objects.filter(user=request.user, due_date__gt=today).first()
    if active_subscription:        
        context['active_subscription'] = active_subscription
    else:
        context['active_subscription'] = None

    return render(request, "users/logged/subscription.html", context)


@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, google_auth_requests.Request(), os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        )
    except ValueError:
        return HttpResponse(status=403)

    
    guser_email = user_data['email']
    guser_first_name = user_data['given_name']
    guser_last_name = user_data['family_name']
    guser_pic = user_data['picture']

    
    if CustomUser.objects.filter(username=guser_email).exists(): # If user exists exists in our system, login
        existing_user = get_object_or_404(CustomUser, username=guser_email)
        login(request, existing_user)  # Login with current user
        log(request, "UserLog", {"action_type":"read", "status":200, "details":"Login by Google", "change_by_admin":False})
        return redirect('/users/access')

    else: # If not, register
        new_user = CustomUser.objects.create_user(username=guser_email, email=guser_email, first_name=guser_first_name, last_name=guser_last_name)

        response = requests.get(guser_pic) # Download Google profile image
        if response.status_code == 200:

            # Guess the picture extension because Google url doesn't have it
            extension = guess_extension(requests.head(guser_pic).headers['Content-Type']) or '.jpg'
            unique_id = uuid.uuid4().hex

            # Create a temporary file to take it for save
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(response.content)

            # Assign temporal file to ImageField
            new_user.pic.save(f"{unique_id}.{extension}", ContentFile(response.content), save=True)
        
        new_user.save()
        login(request, new_user)
        log(request, "UserLog", {"action_type":"create", "status":200, "details":"Registered by Google", "change_by_admin":False})
        return redirect('/users/access')


@login_required(login_url="/users/access")
def successful(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    # TODO: Cambiar producto por None
    log(request, "SubscriptionLog", {"action_type":"create", "status":200, "details":"Subscription process", "payment_gateway":"PayPal", "receptor":request.user, "product": None})
    return render(request, "paypal/success.html", context)


@login_required(login_url="/users/access")
def cancelled(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    log(request, "SubscriptionLog", {"action_type":"create", "status":400, "details":"Subscription process", "payment_gateway":"PayPal", "receptor":request.user})
    return render(request, "paypal/cancelled.html", context)


@login_required(login_url="/users/access")
def cancel_subscription(request, payment_subscription_id):
    config = get_object_or_404(GeneralConfig, id=1)
    
    # Cancel specific subscription
    subscription_to_cancel = get_object_or_404(Subscription, payment_subscription_id=payment_subscription_id)
    subscription_to_cancel.status = "CANCELING"
    subscription_to_cancel.save()
        
    # In case of Paypal
    if subscription_to_cancel.payment_method == "Paypal":
        
        bearer_token = get_paypal_bearer_token()
        url= f'https://api.sandbox.paypal.com/v1/billing/subscriptions/{subscription_to_cancel.payment_subscription_id}/cancel'
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {bearer_token}',
        }
        data = '{ "reason": "Not satisfied with the service" }'
        response = requests.post(url, headers=headers, data=data)
        # Call subscription_states_machine to cancel subscrription
        
    # In case of Stripe
    elif subscription_to_cancel.payment_method == "Stripe":
        stripe.api_key = config.stripe_secret_key
        stripe.Subscription.cancel(subscription_to_cancel.payment_subscription_id)

    return redirect('/users/subscription')


def get_paypal_bearer_token():
    config = get_object_or_404(GeneralConfig, id=1)
    d = {"grant_type" : "client_credentials"}
    h = {"Accept": "application/json"}
    access_token = requests.post(f'{PAYPAL_API_URL}v1/oauth2/token', auth=(config.paypal_client_id, config.paypal_secret_key), headers=h, data=d).json()
    return access_token['access_token']

def stripe_checkout(request, product_id):
    config = get_object_or_404(GeneralConfig, id=1)
        
    stripe.api_key = config.stripe_secret_key
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        success_url=f'{config.app_url}users/successful',
        cancel_url=f'{config.app_url}users/cancel',
        line_items=[{"price": product_id, "quantity": 1}],
        mode="subscription",
        allow_promotion_codes=True,
        metadata={ "user_id":f"{request.user.id}", "plan_id": f"{product_id}"},
    )

    return redirect(checkout_session.url)

@csrf_exempt
def paypal(request):
    """
    Paypal webhook using adapter pattern
    """
    event_actions = {
        'BILLING.SUBSCRIPTION.CREATED': paypal_handle_subscription_created,
        'BILLING.SUBSCRIPTION.ACTIVATED': paypal_handle_subscription_activated,
        'PAYMENT.SALE.COMPLETED': paypal_handle_payment_completed,
        'BILLING.SUBSCRIPTION.CANCELLED': paypal_handle_subscription_cancelled,
        'BILLING.SUBSCRIPTION.UPDATED': paypal_handle_subscription_updated,
        'BILLING.SUBSCRIPTION.PAYMENT.FAILED': paypal_handle_subscription_payment_failed
    }

    return paypal_handle_event(request, event_actions)

@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook using adapter pattern
    """

    event_actions = {
        'customer.subscription.updated': stripe_handle_subscription_updated,
        'invoice.paid': stripe_handle_invoice_paid,
        'invoice.finalized':  stripe_handle_invoice_paid,
        'checkout.session.completed':  stripe_handle_checkout_session_completed,
        'invoice.payment_failed': stripe_handle_payment_failed,
        'payment_intent.payment_failed': stripe_handle_payment_failed,
        'customer.subscription.deleted': stripe_handle_subscription_deleted
    }

    return stripe_handle_event(request, event_actions)