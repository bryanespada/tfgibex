from django.db import models
from users.models import CustomUser
from appmodels.models import Subscription, SurgicalArea, SurgeryType, PeripheralBlock, Product

class GeneralLog(models.Model):
    """
    Abstract class to define the general schema of each log 
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="%(class)s_logs", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    action_type = models.CharField(max_length=100, null=False, blank=False, default='')
    status = models.CharField(max_length=100, null=False, blank=False, default='')
    details = models.TextField(blank=True) # Extra information
    ip = models.CharField(max_length=20, null=False, blank=False, default='')
    continent = models.CharField(max_length=100, null=False, blank=False, default='')
    country = models.CharField(max_length=100, null=False, blank=False, default='')
    region = models.CharField(max_length=200, null=False, blank=False, default='')
    city = models.CharField(max_length=200, null=False, blank=False, default='')
    postal = models.CharField(max_length=20, null=False, blank=False, default='')
    lat = models.CharField(max_length=20, null=False, blank=False, default='') 
    lng = models.CharField(max_length=20, null=False, blank=False, default='') 

    class Meta:
        abstract = True


class UserLog(GeneralLog):
    """
    Class to register user events
    Action options: register, login, logout, recovery password, etc
    """
    change_by_admin = models.BooleanField(default=False)

class AdminsLog(GeneralLog):
    """
    Class to register admin events
    Action options: create, read, list, update, delete
    """
    item = models.CharField(max_length=100) # Options: SurgicalArea, SurgeryType, PeripheralBlock, Parameters, Subscription, Product
    
class SubscriptionLog(GeneralLog):
    """
    Class to register subscription events
    Action options: create, read, update, delete
    """
    payment_gateway = models.CharField(max_length=100, null=True, blank=True, default='') # i.e. Paypal, Stripe, Other which comes from subscription object choices
    receptor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, default=None) # User who receives the subscription
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, default=None) # Product object reference
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True, default=None) # subscription object reference
    payment_gateway_details = models.TextField(blank=True, null= True) # Payment gateway important information about subscription (cus_ in_ ...)
    payload = models.TextField(blank=True, null= True) # Payload from Payment gateway event
    
class TrackingLog(GeneralLog):
    """
    Class to register users tracking events
    Action options: create, read, update, delete
    """
    has_active_subscription = models.BooleanField(default=False)
    surgical_area = models.ForeignKey(SurgicalArea, on_delete=models.CASCADE, null=True, blank=True, default=None)
    surgery_type = models.ForeignKey(SurgeryType, on_delete=models.CASCADE, null=True, blank=True, default=None)
    peripheral_block = models.ForeignKey(PeripheralBlock, on_delete=models.CASCADE, null=True, blank=True, default=None)