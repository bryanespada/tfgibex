from django.contrib import admin
from .models import GeneralConfig, SurgicalArea, SurgeryType, PeripheralBlock, Subscription, Product, Blog, Image

class GeneralConfigAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'app_syncopation', 'app_url',)  # Campos a mostrar en la lista
admin.site.register(GeneralConfig, GeneralConfigAdmin)

class SurgicalAreaAdmin(admin.ModelAdmin):
    list_display = ('title',)
admin.site.register(SurgicalArea, SurgicalAreaAdmin)

class SurgeryTypeAdmin(admin.ModelAdmin):
    list_display = ('title',)
admin.site.register(SurgeryType, SurgeryTypeAdmin)

class PeripheralBlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'public')
admin.site.register(PeripheralBlock, PeripheralBlockAdmin)

class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
admin.site.register(Image, ImageAdmin)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_date', 'due_date')
admin.site.register(Subscription, SubscriptionAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'interval_count', 'interval_unit', 'public',)  # Campos a mostrar en la lista
admin.site.register(Product, ProductAdmin)

class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'datetime', 'url')
admin.site.register(Blog, BlogAdmin)