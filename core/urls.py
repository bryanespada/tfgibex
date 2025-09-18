from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Default path to index
    path("", views.index, name="app_index"),

    # Delegate paths to each subapplication
    path("administration/", include("administration.urls")),
    path("app/", include("app.urls")),
    path("users/", include("users.urls")),
    path("logs/", include("logs.urls")),

    # Django admin path
    path('admin/', admin.site.urls),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = 'core.views.custom_403'
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'