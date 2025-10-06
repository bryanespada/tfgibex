from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordResetView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
from app.views import user_is_premium
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
    

class ResetPasswordView(PasswordResetView):
    template_name = 'users/unlogged/password_reset.html'
    email_template_name = 'users/unlogged/password_reset_email.html'
    subject_template_name = 'users/unlogged/password_reset_subject'
    success_url = reverse_lazy('password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = get_object_or_404(GeneralConfig, id=1)
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email',
            'type': 'email',
            'autofocus': True
        })
        return form

    def form_valid(self, form):
        # Log para debug
        email = form.cleaned_data.get('email')
        print(f"[DEBUG] Intentando enviar email de recuperación a: {email}")

        # Verificar si el usuario existe
        from users.models import CustomUser
        user_exists = CustomUser.objects.filter(username=email).exists()
        print(f"[DEBUG] ¿Usuario existe con email {email}?: {user_exists}")

        # Verificar configuración SMTP
        from django.conf import settings
        print(f"[DEBUG] Configuración SMTP:")
        print(f"  - HOST: {settings.EMAIL_HOST}")
        print(f"  - PORT: {settings.EMAIL_PORT}")
        print(f"  - USER: {settings.EMAIL_HOST_USER}")
        print(f"  - USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"  - FROM: {settings.DEFAULT_FROM_EMAIL}")

        # Intentar enviar email de prueba directamente
        from django.core.mail import send_mail
        try:
            test_result = send_mail(
                'Test directo de SMTP',
                f'Si recibes esto, SMTP funciona. Intentando recuperar contraseña para: {email}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],  # Enviamos a nosotros mismos
                fail_silently=False,
            )
            print(f"[DEBUG] Email de prueba enviado: {test_result}")
        except Exception as e:
            print(f"[ERROR] Error enviando email de prueba: {str(e)}")
            import traceback
            traceback.print_exc()

        # Verificar que Django realmente envíe el email
        print(f"[DEBUG] Llamando a super().form_valid()...")

        # Interceptar el envío real
        from django.contrib.auth.forms import PasswordResetForm
        form_instance = form

        # Ver qué usuarios encuentra Django
        users = form_instance.get_users(email)
        user_count = len(list(users))
        print(f"[DEBUG] Django encontró {user_count} usuarios con ese email")

        # Reintentar para obtener usuarios (get_users es un generador)
        for user in form_instance.get_users(email):
            print(f"[DEBUG] Usuario encontrado: {user.username}, email: {user.email}, is_active: {user.is_active}")
            print(f"[DEBUG] Email field vacío?: '{user.email}' == ''")

        # Verificar directamente en la BD
        from users.models import CustomUser
        user_direct = CustomUser.objects.filter(username=email).first()
        if user_direct:
            print(f"[DEBUG] Verificación directa - username: {user_direct.username}, email field: '{user_direct.email}'")
            if not user_direct.email:
                print(f"[PROBLEMA] El campo email está vacío! Django NO enviará el email de recuperación")
                print(f"[SOLUCION] Actualizando el campo email...")
                user_direct.email = user_direct.username
                user_direct.save()
                print(f"[DEBUG] Campo email actualizado a: {user_direct.email}")

        try:
            result = super().form_valid(form)
            print(f"[DEBUG] form_valid completado - Django debería haber enviado el email de recuperación")
            return result
        except Exception as e:
            print(f"[ERROR] Error en form_valid: {str(e)}")
            import traceback
            traceback.print_exc()
            return super().form_valid(form)


def password_reset_done(request):
    context = {}
    context['config'] = get_object_or_404(GeneralConfig, id=1)
    return render(request, 'users/unlogged/password_reset_done.html', context)


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
    active_subscription = Subscription.objects.filter(
        user=request.user,
        due_date__gt=today,
        status='ACTIVE'
    ).first()
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
    # Temporarily disable log to fix KeyError
    # log(request, "SubscriptionLog", {"action_type":"create", "status":400, "details":"Subscription process", "payment_gateway":"PayPal", "receptor":request.user})
    return render(request, "paypal/cancelled.html", context)


@login_required(login_url="/users/access")
def paypal_redirect(request, product_id):
    """Create PayPal subscription via API and redirect"""
    import requests
    import json

    try:
        # Check if user already has an active subscription
        if user_is_premium(request.user):
            messages.error(request, "Ya tienes una suscripción activa. No puedes crear otra suscripción.")
            return redirect('user_subscription')

        product = get_object_or_404(Product, id=product_id)
        config = get_object_or_404(GeneralConfig, id=1)

        if not product.paypal_subscription_id:
            messages.error(request, "Este producto no tiene configurado PayPal")
            return redirect('user_subscription')

        # Step 1: Get PayPal Access Token
        token_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
        token_headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        token_data = 'grant_type=client_credentials'

        token_response = requests.post(
            token_url,
            headers=token_headers,
            data=token_data,
            auth=(config.paypal_client_id, config.paypal_secret_key)
        )

        if token_response.status_code != 200:
            print(f"=== TOKEN ERROR ===")
            print(f"Token Status: {token_response.status_code}")
            print(f"Token Error: {token_response.text}")
            messages.error(request, "Error de autenticación con PayPal")
            return redirect('user_subscription')

        access_token = token_response.json()['access_token']
        print(f"✅ Token obtenido exitosamente: {access_token[:20]}...")

        # Step 1.5: Verify Plan exists
        plan_check_url = f"https://api.sandbox.paypal.com/v1/billing/plans/{product.paypal_subscription_id}"
        plan_check_headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        plan_check_response = requests.get(plan_check_url, headers=plan_check_headers)
        print(f"=== PLAN CHECK ===")
        print(f"Plan Check Status: {plan_check_response.status_code}")
        print(f"Plan Details: {plan_check_response.text}")

        if plan_check_response.status_code != 200:
            messages.error(request, f"El Plan {product.paypal_subscription_id} no existe o no está activo")
            return redirect('user_subscription')

        # Step 2: Create Subscription
        subscription_url = "https://api.sandbox.paypal.com/v1/billing/subscriptions"
        subscription_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        return_url = request.build_absolute_uri(reverse('paypal_successful'))
        cancel_url = request.build_absolute_uri(reverse('paypal_cancelled'))

        subscription_data = {
            "plan_id": product.paypal_subscription_id,
            "custom_id": str(request.user.id),
            "application_context": {
                "brand_name": "TFG IBEX",
                "locale": "es-ES",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "payment_method": {
                    "payer_selected": "PAYPAL",
                    "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                },
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }

        subscription_response = requests.post(
            subscription_url,
            headers=subscription_headers,
            data=json.dumps(subscription_data)
        )

        if subscription_response.status_code != 201:
            error_detail = subscription_response.text
            print(f"=== PAYPAL ERROR DEBUG ===")
            print(f"Status Code: {subscription_response.status_code}")
            print(f"Plan ID usado: {product.paypal_subscription_id}")
            print(f"Client ID: {config.paypal_client_id[:20]}...")
            print(f"Error completo: {error_detail}")
            print(f"Headers enviados: {subscription_headers}")
            print(f"Data enviada: {json.dumps(subscription_data, indent=2)}")
            messages.error(request, f"Error creando suscripción. Plan ID: {product.paypal_subscription_id}")
            return redirect('user_subscription')

        subscription_result = subscription_response.json()

        # Get approval URL
        approval_url = None
        for link in subscription_result.get('links', []):
            if link.get('rel') == 'approve':
                approval_url = link.get('href')
                break

        if approval_url:
            return redirect(approval_url)
        else:
            messages.error(request, "No se pudo obtener URL de aprobación")
            return redirect('user_subscription')

    except Exception as e:
        messages.error(request, f"Error al procesar PayPal: {str(e)}")
        return redirect('user_subscription')


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
    # Check if user already has an active subscription
    if user_is_premium(request.user):
        messages.error(request, "Ya tienes una suscripción activa. No puedes crear otra suscripción.")
        return redirect('user_subscription')

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


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Vista personalizada para cambio de contraseña que incluye el objeto config
    Validaciones incluidas:
    - Usuario debe estar autenticado (LoginRequiredMixin)
    - Contraseña actual debe ser correcta
    - Nueva contraseña debe cumplir validadores de Django (mín 8 caracteres, no común, etc)
    - Las dos contraseñas nuevas deben coincidir
    """
    template_name = 'users/logged/password_change.html'
    success_url = '/users/password-change-done/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = GeneralConfig.objects.all().first()
        return context

    def form_valid(self, form):
        """
        Llamado cuando el formulario es válido
        La contraseña ya fue validada por Django
        """
        # Log the password change
        log(self.request, 'Change', 'Contraseña cambiada exitosamente')
        messages.success(self.request, 'Tu contraseña ha sido actualizada exitosamente.')
        return super().form_valid(form)


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """
    Vista personalizada para confirmación de cambio de contraseña
    """
    template_name = 'users/logged/password_change_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['config'] = GeneralConfig.objects.all().first()
        return context