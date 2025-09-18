from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from utils.functions import is_admin
from appmodels.models import GeneralConfig

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        is_admin_result = is_admin(request.user)
        if "/administration" in request.path and not is_admin_result:
            config = get_object_or_404(GeneralConfig, id=1)
            context ={ 'config': config }
            return redirect('/users/access')

        return None