from django.db import models
from django.utils import timezone
from users.models import CustomUser
from django.core.exceptions import ValidationError
from datetime import timedelta
from uuid import uuid4
import uuid
import os


class GeneralConfig(models.Model):

    PAYMENT_CURRENCY = (
        ('USD', 'USD'),
        ('EUR', 'EUR'),
    )

    # GENERAL
    app_name = models.CharField(max_length=100, blank=False, null=False, default="Easy Regional Block")
    app_syncopation = models.CharField(max_length=10, blank=False, null=False, default="ERB")
    app_logs = models.CharField(max_length=1, blank=False, null=False, default="1")
    app_url = models.CharField(max_length=100, blank=False, null=False, default="https://app.tfgibex.com/")

    # NOTIFICATIONS
    smtp_email_account = models.CharField(max_length=100, blank=False, null=False, default="no-reply@tfgibex.com")
    smtp_password = models.CharField(max_length=100, blank=False, null=False, default="app2024ERB/")
    smtp_server = models.CharField(max_length=100, blank=False, null=False, default="smtp.servidor-correo.net")
    smtp_port = models.IntegerField(null=False, default=587)
    
    # BRANDING
    app_primary = models.CharField(max_length=9, blank=False, null=False, default="#2A3F54")
    app_color_1 = models.CharField(max_length=9, blank=False, null=False, default="#03586A")
    app_color_2 = models.CharField(max_length=9, blank=False, null=False, default="#1F6B7B")
    app_color_3 = models.CharField(max_length=9, blank=False, null=False, default="#3B7D8B")
    app_color_4 = models.CharField(max_length=9, blank=False, null=False, default="#57909C")
    app_color_5 = models.CharField(max_length=9, blank=False, null=False, default="#73A2AC")
    app_color_6 = models.CharField(max_length=9, blank=False, null=False, default="#8FB5BD")
    app_color_7 = models.CharField(max_length=9, blank=False, null=False, default="#ABC7CD")
    app_color_8 = models.CharField(max_length=9, blank=False, null=False, default="#C7DADE")
    app_success = models.CharField(max_length=9, blank=False, null=False, default="#41A91A")
    app_danger = models.CharField(max_length=9, blank=False, null=False, default="#A91A1A")
    app_icon = models.CharField(max_length=100, blank=False, null=False, default="fa-solid fa-angles-right")
    app_transparency_factor = models.CharField(max_length=2, blank=False, null=False, default="61")

    # PAYPAL
    currency = models.CharField(max_length=3, choices=PAYMENT_CURRENCY, default='USD')
    paypal_client_id = models.CharField(max_length=100, blank=False, null=False, default="")
    paypal_secret_key = models.CharField(max_length=100, blank=False, null=False, default="")
    paypal_account_email = models.CharField(max_length=100, blank=False, null=False, default="")
    stripe_public_key = models.CharField(max_length=200, blank=False, null=False, default="")
    stripe_secret_key = models.CharField(max_length=200, blank=False, null=False, default="")
    
    # GOOGLE OAUTH
    google_oauth_client_id = models.CharField(max_length=100, blank=True, null=True)
    google_oauth_client_secret = models.CharField(max_length=100, blank=True, null=True)
    google_analytics_tag_id = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        # Check if there is a previous object of GeneralConfig
        if GeneralConfig.objects.exists() and self.id is None:
            raise ValidationError("There can be only one element of type GeneralConfig.")

    def __str__(self):
        return str(self.pk)



class SurgicalArea(models.Model):
    title = models.CharField(max_length=200, blank=False, null=False, default='')
    description = models.CharField(max_length=6000, blank=True, null=True, default='')

    def __str__(self):
        return self.title



class SurgeryType(models.Model):
    title = models.CharField(max_length=200, blank=False, null=False, default='')
    description = models.CharField(max_length=6000, blank=True, null=True, default='')
    surgical_area = models.ForeignKey(SurgicalArea, on_delete=models.CASCADE)

    def __str__(self):
        return self.title



class PeripheralBlock(models.Model):
    title = models.CharField(max_length=200, blank=False, null=False, default='')
    description = models.CharField(max_length=10000, blank=True, null=True, default='')
    video_link = models.CharField(max_length=2000, blank=True, null=True, default='')
    public = models.BooleanField(default=False)
    surgery_type = models.ForeignKey(SurgeryType, on_delete=models.CASCADE)

    def __str__(self):
        return self.title





def upload_to_periphera_block_pics(instance, filename):
    """
    Generate a filename based on a UUID.
    """
    peripheral_block_id = instance.peripheral_block.id
    directory = f'peripheral_block_pics/{peripheral_block_id}'
    if not os.path.exists(directory): # Create, if not exists, the directory where the images are being saved
        os.makedirs(directory)

    ext = filename.split('.')[-1] # Get file extension
    filename = f"{uuid4().hex}.{ext}" # Generate unique file name using UUID
    return f"peripheral_block_pics/{peripheral_block_id}/{filename}" # Return file path with name


class Image(models.Model):

    image = models.ImageField(upload_to=upload_to_periphera_block_pics)
    title = models.CharField(max_length=200, blank=False, null=False, default='')
    description = models.CharField(max_length=6000, blank=True, null=True, default='')
    peripheral_block = models.ForeignKey(PeripheralBlock, related_name='images', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title


        


class Subscription(models.Model):

    PAYMENT_METHODS = (
        ('Free', 'Free'),
        ('Paypal', 'Paypal'),
        ('Cash', 'Cash'),
        ('Bank transfer', 'Bank transfer'),
        ('Other', 'Other'),
    )

    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),                   # When the subcription is right and usable
        ('PENDING', 'Pending'),                 # When is paid but not activated by the gateway
        ('HIDDEN', 'Hidden'),                   # When is precreated but not paid
        ('PAYMENT ERROR', 'Payment error'),     # When the payment method has been refused
        ('CANCELLING', 'Cancelling'),               # When the subscription is over
        ('CANCELED', 'Canceled'),               # When the subscription is over
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True) # Associated user
    payment_datetime = models.DateTimeField(default=timezone.now) # Datetime where the payment was done
    amount = models.FloatField(blank=False, null=False, default=0) # Amount paid
    currency = models.CharField(max_length=3, blank=False, null=False, default='USD') # Payment currency
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Free') # Payment method
    payment_product_id = models.IntegerField(null=False, default=1) # Payment gateway reference ID (i.e. Paypal product ID)
    payment_subscription_id = models.CharField(max_length=255, blank=True, null=True, unique=True) # Payment gateway reference ID (i.e. Paypal product ID)
    start_date = models.DateField(null=False, blank=False, default=timezone.now) # Datetime where the subscription starts
    due_date = models.DateField(null=False, blank=False, default=timezone.now) # Datetime where the subscription finishes
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='INACTIVE')  # Status of the subscription


    def __str__(self):
        return f"# {self.pk}"
    




class Product(models.Model):
    
    INTERVAL_UNITS = (
        ('Y', 'Year'),
        ('M', 'Month'),
        ('W', 'Week'),
    )

    title = models.CharField(max_length=200, blank=False, null=False, default='')
    description = models.CharField(max_length=2000, blank=True, null=True, default='')
    price = models.FloatField(default=0, null=False)
    interval_count = models.IntegerField(null=False, default=1)
    interval_unit = models.CharField(max_length=3, choices=INTERVAL_UNITS, default='M')
    discount = models.IntegerField(null=False, default=0)
    public = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, null=True, default='')
    paypal_subscription_id = models.CharField(max_length=100, blank=True, null=True, default='')

    def __str__(self):
        return self.title
    
    def get_interval_display(self):
        interval_unit_display = dict(self.INTERVAL_UNITS).get(self.interval_unit, '')
        unit_display = interval_unit_display if self.interval_count == 1 else f"{interval_unit_display}s"
        return f"{self.interval_count} {unit_display}" if interval_unit_display else ''

    @property
    def final_price(self):
        return self.price * (100 - self.discount) / 100
    
    @property
    def get_period(self):
        subscription_days = 0
        if self.interval_unit == 'W':
            subscription_days = self.interval_count * 7
        elif self.interval_unit == 'M':
            subscription_days = self.interval_count * 30
        elif self.interval_unit == 'Y':
            subscription_days = self.interval_count * 365

        start_date = timezone.now() - timedelta(days=1)
        due_date = start_date + timedelta(days=subscription_days) 
        return start_date, due_date



def upload_to_blog_pics(instance, filename):
    """
    Generate a filename based on a UUID.
    """
    ext = filename.split('.')[-1] # Get file extension
    filename = f"{uuid4().hex}.{ext}" # Generate unique file name using UUID
    return f"blog_pics/{filename}" # Return file path with name



class Blog(models.Model):

    title = models.CharField(max_length=200, blank=False, null=False, default='')
    description = models.CharField(max_length=10000, blank=True, null=True, default='')
    datetime = models.DateTimeField(default=timezone.now)
    pic = models.ImageField(upload_to=upload_to_blog_pics, null=True, blank=True)
    url = models.CharField(max_length=300, blank=True, null=True, default='')
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.title