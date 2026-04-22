from django.urls import path
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from . import views
from .forms import NindoSetPasswordForm

app_name = "users"

urlpatterns = [
    path("login/", views.NindoLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("perfil/", views.ProfileUpdateView.as_view(), name="profile"),
    path(
        "cambiar-contrasena/",
        PasswordChangeView.as_view(template_name="users/password_change.html"),
        name="password_change",
    ),
    path(
        "cambiar-contrasena/listo/",
        PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
    # Password reset — handled by custom Resend-powered view
    path("recuperar/", views.NindoPasswordResetView.as_view(), name="password_reset"),
    path(
        "recuperar/listo/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "recuperar/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            form_class=NindoSetPasswordForm,
            success_url="/usuarios/recuperar/completo/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "recuperar/completo/",
        PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # Admin user management
    path("lista/", views.UserListView.as_view(), name="list"),
    path("nuevo/", views.UserCreateView.as_view(), name="create"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.UserAdminUpdateView.as_view(), name="admin_edit"),
    path("<int:pk>/toggle/", views.UserToggleActiveView.as_view(), name="toggle_active"),
]
