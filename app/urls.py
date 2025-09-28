from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.dashboard, name="user_dashboard"),
    path("dashboard/", views.dashboard, name="user_dashboard"),
    path("mercados/", views.mercados, name="user_mercados"),
    path("bolsas/", views.bolsas, name="user_bolsas"),
    path("bolsas/<int:mercado_id>/", views.bolsas, name="user_bolsas"),
    path("peripheral-blocks/", views.peripheral_blocks, name="user_peripheral_blocks"),
    path("peripheral-blocks/<int:bolsa_id>/", views.peripheral_blocks, name="user_peripheral_blocks"),
    path("peripheral-block/<int:peripheral_block_id>/", views.peripheral_block, name="user_peripheral_block"),
]