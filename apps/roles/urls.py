from django.urls import path
from . import views

app_name = "roles"

urlpatterns = [
    path("", views.RoleListView.as_view(), name="list"),
    path("nuevo/", views.RoleCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.RoleUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", views.RoleDeleteView.as_view(), name="delete"),
    path("asignar/", views.UserRoleAssignView.as_view(), name="assign"),
    path("<int:pk>/revocar/", views.UserRoleRevokeView.as_view(), name="revoke"),
]
