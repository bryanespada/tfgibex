from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.dashboard, name="user_dashboard"),
    path("dashboard/", views.dashboard, name="user_dashboard"),
    path("mercados/", views.mercados, name="user_mercados"),
    path("bolsas/", views.bolsas, name="user_bolsas"),
    path("bolsas/<int:mercado_id>/", views.bolsas, name="user_bolsas"),
    path("empresas/", views.empresas, name="user_empresas"),
    path("empresas/<int:bolsa_id>/", views.empresas, name="user_empresas"),
    path("empresa/<int:empresa_id>/", views.empresa, name="user_empresa"),
    path("noticias/", views.noticias, name="user_noticias"),
    path("noticia/<int:noticia_id>/", views.noticia, name="user_noticia"),
]