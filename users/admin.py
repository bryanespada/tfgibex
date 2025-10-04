from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import CustomUser
from appmodels.models import Subscription

class CustomUserAdmin(UserAdmin):

    def is_premium(self, obj):
        """Check if user has active subscription"""
        today = timezone.now().date()
        return Subscription.objects.filter(
            user=obj,
            due_date__gte=today
        ).exists()
    is_premium.boolean = True  # Shows as checkbox icon
    is_premium.short_description = 'Premium'

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_premium', 'is_staff', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # Using standard UserAdmin fieldsets to avoid password field issues
    filter_horizontal = ('groups', 'user_permissions')

admin.site.register(CustomUser, CustomUserAdmin)