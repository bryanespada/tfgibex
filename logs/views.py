from django.shortcuts import render, get_object_or_404
from utils.functions import get_client_geolocation
from django.contrib.auth.models import AnonymousUser
from logs.models import UserLog, AdminsLog, SubscriptionLog, TrackingLog
from appmodels.models import CustomUser

# Create your views here.
def log(request, log_type, log_data):

    geolocation_data = get_client_geolocation(request) # Get request origin
    if isinstance(request.user, AnonymousUser):
        user = None
    else:
        user = request.user


    if log_type == 'AdminsLog': # Store log
        AdminsLog.objects.create(
            user = user,
            action_type = log_data['action_type'],
            status = log_data['status'],
            details = log_data['details'],
            ip = geolocation_data['ip'],
            continent = geolocation_data['continent'],
            country = geolocation_data['country'],
            region = geolocation_data['region'],
            city = geolocation_data['city'],
            postal = geolocation_data['postal'],
            lat = geolocation_data['lat'],
            lng = geolocation_data['lng'],
            item = log_data['item']
        )

    elif log_type == 'UserLog':
        # Just in case of register, save the recently created user
        if log_data['action_type'] == "create" and log_data['status'] == 200:
            user = get_object_or_404(CustomUser, id=log_data['new_user'].id)

        UserLog.objects.create(
            user = user,
            action_type = log_data['action_type'],
            status = log_data['status'],
            details = log_data['details'],
            ip = geolocation_data['ip'],
            continent = geolocation_data['continent'],
            country = geolocation_data['country'],
            region = geolocation_data['region'],
            city = geolocation_data['city'],
            postal = geolocation_data['postal'],
            lat = geolocation_data['lat'],
            lng = geolocation_data['lng'],
            change_by_admin = log_data['change_by_admin']
        )

    elif log_type == 'SubscriptionLog':
        SubscriptionLog.objects.create(
            user = user,
            action_type = log_data['action_type'],
            status = log_data['status'],
            details = log_data['details'],
            ip = geolocation_data['ip'],
            continent = geolocation_data['continent'],
            country = geolocation_data['country'],
            region = geolocation_data['region'],
            city = geolocation_data['city'],
            postal = geolocation_data['postal'],
            lat = geolocation_data['lat'],
            lng = geolocation_data['lng'],
            payment_gateway = log_data['payment_gateway'],
            product = log_data['product'],
            receptor = log_data['receptor'],
            subscription = log_data['subscription'] if "subscription" in log_data else None,
            payment_gateway_details = log_data['payment_gateway_details'] if "payment_gateway_details" in log_data else None,       
            payload = log_data['payload'] if "payload" in log_data else None,   
        )

    elif log_type == 'TrackingLog':
        TrackingLog.objects.create(
            user = user,
            action_type = log_data['action_type'],
            status = log_data['status'],
            details = log_data['details'],
            ip = geolocation_data['ip'],
            continent = geolocation_data['continent'],
            country = geolocation_data['country'],
            region = geolocation_data['region'],
            city = geolocation_data['city'],
            postal = geolocation_data['postal'],
            lat = geolocation_data['lat'],
            lng = geolocation_data['lng'],
            has_active_subscription = log_data['has_active_subscription'],
            surgical_area = log_data['surgical_area'],
            surgery_type = log_data['surgery_type'],
            peripheral_block = log_data['peripheral_block']
        )

    else:
        print("ERROR EN LOGS")