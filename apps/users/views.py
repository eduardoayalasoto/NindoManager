from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, ListView, DetailView, CreateView
from django.contrib import messages
from django.shortcuts import redirect

from .models import User
from .forms import NindoLoginForm, UserCreateForm, UserUpdateForm
from apps.common.mixins import AdminRequiredMixin
from apps.roles.models import UserRole, Role
from apps.branches.models import Branch


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
            qs = qs.filter(
                username__icontains=q
            ) | qs.filter(
                first_name__icontains=q
            ) | qs.filter(
                last_name__icontains=q
            )
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


class UserToggleActiveView(AdminRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        user.is_active = not user.is_active
        user.save()
        status = "activado" if user.is_active else "desactivado"
        messages.success(request, f"Usuario {user} {status}.")
        return redirect("users:list")
