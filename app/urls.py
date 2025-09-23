from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.dashboard, name="user_dashboard"),
    path("dashboard/", views.dashboard, name="user_dashboard"),
    path("mercados/", views.mercados, name="user_mercados"),
    path("surgery-types/", views.surgery_types, name="user_surgery_types"),
    path("surgery-types/<int:mercado_id>/", views.surgery_types, name="user_surgery_types"),
    path("peripheral-blocks/", views.peripheral_blocks, name="user_peripheral_blocks"),
    path("peripheral-blocks/<int:surgery_type_id>/", views.peripheral_blocks, name="user_peripheral_blocks"),
    path("peripheral-block/<int:peripheral_block_id>/", views.peripheral_block, name="user_peripheral_block"),
]