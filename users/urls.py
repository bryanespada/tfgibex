from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path
from . import views
from .views import ResetPasswordView

urlpatterns = [
    # Path to non logged users
    path("", lambda request: redirect("access/"), name="principal_redirection"), # Redirect from main url ("/") to ("/access/")
    path("access/", views.access, name="access"),
    path("register/", views.register, name="register"),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('passwordreset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/unlogged/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/unlogged/password_reset_complete.html'), name='password_reset_complete'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'), # Endpoint to Google Auth

    # Paths to logged users
    path("exit/", views.exit, name="exit"),
    path("profile/", views.profile, name="profile"),
    path("subscription/", views.subscription, name="user_subscription"),

    # Paths of Payments use
    path("stripe_webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("cancel_subscription/<str:payment_subscription_id>/", views.cancel_subscription, name="cancel_subscription"),
    path("paypal/", views.paypal, name="paypal"),
    path("successful/", views.successful, name="paypal_successful"),
    path("cancelled/", views.cancelled, name="paypal_cancelled"),
    path("stripe_checkout/<str:product_id>/", views.stripe_checkout, name="stripe_checkout"),
]