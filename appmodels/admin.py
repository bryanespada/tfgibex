from django.contrib import admin
from .models import GeneralConfig, Mercado, Bolsa, Empresa, Subscription, Product, Blog, Image, Noticia

class GeneralConfigAdmin(admin.ModelAdmin):
    list_display = ('app_name', 'app_syncopation', 'app_url',)  # Campos a mostrar en la lista
admin.site.register(GeneralConfig, GeneralConfigAdmin)

class MercadoAdmin(admin.ModelAdmin):
    list_display = ('title',)
admin.site.register(Mercado, MercadoAdmin)

class BolsaAdmin(admin.ModelAdmin):
    list_display = ('title',)
admin.site.register(Bolsa, BolsaAdmin)

class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('title', 'public')
admin.site.register(Empresa, EmpresaAdmin)

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

class NoticiaAdmin(admin.ModelAdmin):
    list_display = ('title', 'empresa', 'published_date', 'is_premium', 'public')
    list_filter = ('is_premium', 'public', 'published_date', 'empresa__mercado', 'empresa__bolsas')
    search_fields = ('title', 'summary', 'content', 'empresa__title', 'tags')
    date_hierarchy = 'published_date'
    ordering = ('-published_date',)

    fieldsets = (
        ('Información básica', {
            'fields': ('title', 'summary', 'content')
        }),
        ('Clasificación', {
            'fields': ('empresa', 'tags')
        }),
        ('Multimedia', {
            'fields': ('image', 'video_link')
        }),
        ('Metadatos', {
            'fields': ('published_date', 'author', 'source', 'source_url')
        }),
        ('Control de acceso', {
            'fields': ('is_premium', 'public')
        }),
        ('API', {
            'fields': ('api_id', 'api_source'),
            'classes': ('collapse',)
        }),
    )
admin.site.register(Noticia, NoticiaAdmin)