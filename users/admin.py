from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'last_login', 'is_active')  # Add fields to show in django admin screen
    
admin.site.register(CustomUser, CustomUserAdmin) # Register the app in the django admin to show it