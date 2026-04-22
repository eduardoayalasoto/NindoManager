import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import UpdateView, ListView, DetailView, CreateView

from .models import User
from .forms import (
    NindoLoginForm, UserCreateForm, UserUpdateForm,
    AdminUserUpdateForm, PasswordResetEmailForm, NindoSetPasswordForm,
)
from apps.common.mixins import AdminRequiredMixin
from apps.roles.models import UserRole, Role
from apps.branches.models import Branch

logger = logging.getLogger(__name__)


class NindoLoginView(LoginView):
    template_name = "users/login.html"
    form_class = NindoLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("dashboard:index")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado correctamente.")
        return super().form_valid(form)


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.prefetch_related("user_roles__role", "user_roles__branch")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(username__icontains=q) | qs.filter(
                first_name__icontains=q
            ) | qs.filter(last_name__icontains=q)
        return qs.order_by("first_name", "last_name")


class UserDetailView(AdminRequiredMixin, DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["user_roles"] = self.object.user_roles.select_related("role", "branch").filter(is_active=True)
        ctx["roles"] = Role.objects.all()
        ctx["branches"] = Branch.objects.filter(is_active=True)
        return ctx


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "users/user_form.html"

    def get_success_url(self):
        return reverse_lazy("users:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f"Usuario {form.instance.username} creado correctamente.")
        return super().form_valid(form)


class UserAdminUpdateView(AdminRequiredMixin, View):
    template_name = "users/user_edit.html"

    def get(self, request, pk):
        profile_user = get_object_or_404(User, pk=pk)
        form = AdminUserUpdateForm(instance=profile_user)
        return render(request, self.template_name, {"form": form, "profile_user": profile_user})

    def post(self, request, pk):
        profile_user = get_object_or_404(User, pk=pk)
        form = AdminUserUpdateForm(request.POST, request.FILES, instance=profile_user)
        if form.is_valid():
            form.save()
            self._sync_roles(
                profile_user,
                form.cleaned_data.get("roles", []),
                form.cleaned_data.get("branches", []),
            )
            messages.success(request, f"Usuario {profile_user} actualizado correctamente.")
            return redirect("users:list")
        return render(request, self.template_name, {"form": form, "profile_user": profile_user})

    def _sync_roles(self, user, selected_roles, selected_branches):
        current_combos = set(
            user.user_roles.filter(is_active=True).values_list("role_id", "branch_id")
        )
        desired_combos = {(r.pk, b.pk) for r in selected_roles for b in selected_branches}

        for role_id, branch_id in current_combos - desired_combos:
            user.user_roles.filter(role_id=role_id, branch_id=branch_id).update(is_active=False)

        for role_id, branch_id in desired_combos - current_combos:
            obj, created = UserRole.objects.get_or_create(
                user=user, role_id=role_id, branch_id=branch_id,
                defaults={"is_active": True, "assigned_by": self.request.user},
            )
            if not created:
                obj.is_active = True
                obj.assigned_by = self.request.user
                obj.save()


class UserToggleActiveView(AdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_active = not user.is_active
        user.save()
        status = "activado" if user.is_active else "desactivado"
        messages.success(request, f"Usuario {user} {status}.")
        return redirect("users:list")


class NindoPasswordResetView(View):
    template_name = "users/password_reset.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PasswordResetEmailForm()})

    def post(self, request):
        form = PasswordResetEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email, is_active=True)
                self._send_reset_email(request, user)
            except User.DoesNotExist:
                pass  # Don't reveal whether the email exists
            return redirect("users:password_reset_done")
        return render(request, self.template_name, {"form": form})

    def _send_reset_email(self, request, user):
        import resend
        from django.conf import settings

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
            reverse("users:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        )
        resend.api_key = settings.RESEND_API_KEY
        try:
            resend.Emails.send({
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": user.email,
                "subject": "Recuperar contraseña - Nindo Manager",
                "html": _build_reset_email_html(user, reset_url),
            })
        except Exception as exc:
            logger.error("Error sending password reset email to %s: %s", user.email, exc)


def _build_reset_email_html(user, reset_url):
    name = user.get_full_name() or user.username
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#fff;">
      <h1 style="font-weight:900;letter-spacing:.15em;font-size:2rem;text-transform:uppercase;margin:0 0 4px;">NIND&#332;</h1>
      <div style="height:4px;width:40px;background:#CC0000;margin-bottom:28px;"></div>
      <h2 style="font-size:1.1rem;font-weight:700;color:#000;margin:0 0 8px;">Recuperar contraseña</h2>
      <p style="color:#555;font-size:.9rem;margin:0 0 24px;">Hola <strong>{name}</strong>, recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
      <a href="{reset_url}"
         style="display:inline-block;padding:12px 28px;background:#000;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;font-size:.9rem;">
        Restablecer contraseña
      </a>
      <p style="color:#999;font-size:.8rem;margin-top:24px;line-height:1.5;">
        Este enlace expira en 24 horas.<br>
        Si no solicitaste este cambio, puedes ignorar este mensaje.
      </p>
    </div>
    """
