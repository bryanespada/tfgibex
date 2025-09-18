from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone
from uuid import uuid4
import uuid



def custom_upload_to(instance, filename):
    """
    Generate a filename based on a UUID.
    """
    ext = filename.split('.')[-1] # Get file extension
    filename = f"{uuid4().hex}.{ext}" # Generate unique file name using UUID
    return f"profile_pics/{filename}" # Return file path with name



    

class CustomUser(AbstractUser):
    
    pic = models.ImageField(upload_to=custom_upload_to, null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_user_permissions')


    def is_premium(self):
        return user_is_premium(self.pk)