from django.contrib import admin
from .models import UserLog, AdminsLog, SubscriptionLog, TrackingLog

class UserLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'action_type', 'ip', 'status', 'continent', 'country', 'city', 'change_by_admin',) # Fields to show in admin table
admin.site.register(UserLog, UserLogAdmin)

class AdminsLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'action_type', 'ip', 'status', 'continent', 'country', 'city', 'item',) # Fields to show in admin table
admin.site.register(AdminsLog, AdminsLogAdmin)

class SubscriptionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'action_type', 'ip', 'status', 'continent', 'country', 'city', 'payment_gateway', 'receptor') # Fields to show in admin table
admin.site.register(SubscriptionLog, SubscriptionLogAdmin)

class TrackingLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'action_type', 'ip', 'status', 'continent', 'country', 'city', 'has_active_subscription',) # Fields to show in admin table
admin.site.register(TrackingLog, TrackingLogAdmin)