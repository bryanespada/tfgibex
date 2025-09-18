from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.dashboard, name="user_dashboard"),
    path("dashboard/", views.dashboard, name="user_dashboard"),
    path("surgical-areas/", views.surgical_areas, name="user_surgical_areas"),
    path("surgery-types/", views.surgery_types, name="user_surgery_types"),
    path("surgery-types/<int:surgical_area_id>/", views.surgery_types, name="user_surgery_types"),
    path("peripheral-blocks/", views.peripheral_blocks, name="user_peripheral_blocks"),
    path("peripheral-blocks/<int:surgery_type_id>/", views.peripheral_blocks, name="user_peripheral_blocks"),
    path("peripheral-block/<int:peripheral_block_id>/", views.peripheral_block, name="user_peripheral_block"),
]