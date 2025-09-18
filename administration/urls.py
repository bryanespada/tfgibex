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
    
    path("surgical_areas/", views.surgical_areas, name="administration_surgical_areas"),
    path("surgical_area_add/", views.surgical_area_add, name="administration_surgical_area_add"),
    path("surgical_area_edit/<int:surgical_area_id>/", views.surgical_area_edit, name="administration_surgical_area_edit"),
    path("surgical_area_delete/<int:surgical_area_id>/", views.surgical_area_delete, name="administration_surgical_area_delete"),
    
    path("surgery_types/", views.surgery_types, name="administration_surgery_types"),
    path("surgery_type_add/", views.surgery_type_add, name="administration_surgery_type_add"),
    path("surgery_type_edit/<int:surgery_type_id>/", views.surgery_type_edit, name="administration_surgery_type_edit"),
    path("surgery_type_delete/<int:surgery_type_id>/", views.surgery_type_delete, name="administration_surgery_type_delete"),
    path("get_surgery_types_by_surgical_area/<int:surgical_area_id>/", views.get_surgery_types_by_surgical_area, name="administration_get_surgery_types_by_surgical_area"),

    path("peripheral_blocks/", views.peripheral_blocks, name="administration_peripheral_blocks"),
    path("peripheral_block_add/", views.peripheral_block_add, name="administration_peripheral_block_add"),
    path("peripheral_block_edit/<int:peripheral_block_id>/", views.peripheral_block_edit, name="administration_peripheral_block_edit"),
    path("peripheral_block_delete/<int:peripheral_block_id>/", views.peripheral_block_delete, name="administration_peripheral_block_delete"),
    path("peripheral_block_gallery/<int:peripheral_block_id>/", views.peripheral_block_gallery, name="administration_peripheral_block_gallery"),
    path("peripheral_block_image_delete/<int:image_id>/", views.peripheral_block_image_delete, name="administration_peripheral_block_image_delete"),

    path("logs/", views.logs, name="administration_logs"),
    path('get_log_details/<str:log_type>/<int:log_id>', views.get_log_details, name='administration_get_log_details'),


]