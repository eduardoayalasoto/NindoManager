from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Role, UserRole
from .forms import RoleForm, UserRoleForm
from apps.common.mixins import AdminRequiredMixin
from apps.users.models import User


class RoleListView(AdminRequiredMixin, ListView):
    model = Role
    template_name = "roles/role_list.html"
    context_object_name = "roles"


class RoleCreateView(AdminRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    template_name = "roles/role_form.html"
    success_url = reverse_lazy("roles:list")

    def form_valid(self, form):
        messages.success(self.request, f"Rol '{form.instance.name}' creado.")
        return super().form_valid(form)


class RoleUpdateView(AdminRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    template_name = "roles/role_form.html"
    success_url = reverse_lazy("roles:list")

    def form_valid(self, form):
        messages.success(self.request, f"Rol '{form.instance.name}' actualizado.")
        return super().form_valid(form)


class RoleDeleteView(AdminRequiredMixin, DeleteView):
    model = Role
    template_name = "roles/role_confirm_delete.html"
    success_url = reverse_lazy("roles:list")


class UserRoleAssignView(AdminRequiredMixin, CreateView):
    model = UserRole
    form_class = UserRoleForm
    template_name = "roles/assign_role.html"

    def form_valid(self, form):
        form.instance.assigned_by = self.request.user
        messages.success(self.request, "Rol asignado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("users:detail", kwargs={"pk": self.object.user.pk})


class UserRoleRevokeView(AdminRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        user_role = get_object_or_404(UserRole, pk=pk)
        user_id = user_role.user.pk
        user_role.is_active = False
        user_role.save()
        messages.success(request, "Rol revocado.")
        return redirect("users:detail", pk=user_id)
