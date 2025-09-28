from django.urls import path
from . import views

urlpatterns = [

    path("dashboard/", views.dashboard, name="administration_dashboard"),
    path("parameters/", views.parameters, name="administration_parameters"),
    
    path("products/", views.products, name="administration_products"),
    path("product_add/", views.product_add, name="administration_product_add"),
    path("product_edit/<int:product_id>/", views.product_edit, name="administration_product_edit"),
    path("product_delete/<int:product_id>/", views.product_delete, name="administration_product_delete"),
    
    path("posts/", views.blogs, name="administration_blogs"),
    path("post-add/", views.blog_add, name="administration_blog_add"),
    path("post-edit/<int:blog_id>/", views.blog_edit, name="administration_blog_edit"),
    path("post-delete/<int:blog_id>/", views.blog_delete, name="administration_blog_delete"),
    
    path("subscriptions/", views.subscriptions, name="administration_subscriptions"),
    path("subscription_add/", views.subscription_add, name="administration_subscription_add"),
    path("subscription_edit/<int:subscription_id>/", views.subscription_edit, name="administration_subscription_edit"),
    path("subscription_delete/<int:subscription_id>/", views.subscription_delete, name="administration_subscription_delete"),
    path("assign_product/", views.assign_product, name="administration_assign_product"),

    path("users/", views.users, name="administration_users"),
    path("user_add/", views.user_add, name="administration_user_add"),
    path("user_edit/<int:custom_user_id>/", views.user_edit, name="administration_user_edit"),
    path("user_delete/<int:custom_user_id>/", views.user_delete, name="administration_user_delete"),
    path("user_make_admin/<int:custom_user_id>/", views.user_make_admin, name="administration_user_make_admin"),
    path("user_deactivate_account/<int:custom_user_id>/", views.user_deactivate_account, name="administration_user_deactivate_account"),
    
    path("mercados/", views.mercados, name="administration_mercados"),
    path("mercado_add/", views.mercado_add, name="administration_mercado_add"),
    path("mercado_edit/<int:mercado_id>/", views.mercado_edit, name="administration_mercado_edit"),
    path("mercado_delete/<int:mercado_id>/", views.mercado_delete, name="administration_mercado_delete"),
    
    path("bolsas/", views.bolsas, name="administration_bolsas"),
    path("bolsa_add/", views.bolsa_add, name="administration_bolsa_add"),
    path("bolsa_edit/<int:bolsa_id>/", views.bolsa_edit, name="administration_bolsa_edit"),
    path("bolsa_delete/<int:bolsa_id>/", views.bolsa_delete, name="administration_bolsa_delete"),
    path("get_bolsas_by_mercado/<int:mercado_id>/", views.get_bolsas_by_mercado, name="administration_get_bolsas_by_mercado"),

    path("empresas/", views.empresas, name="administration_empresas"),
    path("empresa_add/", views.empresa_add, name="administration_empresa_add"),
    path("empresa_edit/<int:empresa_id>/", views.empresa_edit, name="administration_empresa_edit"),
    path("empresa_delete/<int:empresa_id>/", views.empresa_delete, name="administration_empresa_delete"),
    path("empresa_gallery/<int:empresa_id>/", views.empresa_gallery, name="administration_empresa_gallery"),
    path("empresa_image_delete/<int:image_id>/", views.empresa_image_delete, name="administration_empresa_image_delete"),

    path("logs/", views.logs, name="administration_logs"),
    path('get_log_details/<str:log_type>/<int:log_id>', views.get_log_details, name='administration_get_log_details'),


]