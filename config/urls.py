from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.dashboard.urls")),
    path("usuarios/", include("apps.users.urls")),
    path("sucursales/", include("apps.branches.urls")),
    path("roles/", include("apps.roles.urls")),
    path("tareas/", include("apps.tasks.urls")),
    path("actividades/", include("apps.activities.urls")),
    path("notificaciones/", include("apps.notifications.urls")),
    path("api/", include("apps.dashboard.api_urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
