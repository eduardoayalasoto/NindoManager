from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Branch
from .forms import BranchForm
from apps.common.mixins import AdminRequiredMixin, BranchFilterMixin


class BranchListView(LoginRequiredMixin, ListView):
    model = Branch
    template_name = "branches/branch_list.html"
    context_object_name = "branches"

    def get_queryset(self):
        return self.request.user.get_accessible_branches()


class BranchDetailView(LoginRequiredMixin, DetailView):
    model = Branch
    template_name = "branches/branch_detail.html"
    context_object_name = "branch"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stats"] = self.object.get_task_stats_today()
        ctx["staff"] = self.object.user_roles.select_related("user", "role").filter(is_active=True)
        return ctx


class BranchCreateView(AdminRequiredMixin, CreateView):
    model = Branch
    form_class = BranchForm
    template_name = "branches/branch_form.html"
    success_url = reverse_lazy("branches:list")

    def form_valid(self, form):
        messages.success(self.request, f"Sucursal {form.instance.name} creada.")
        return super().form_valid(form)


class BranchUpdateView(AdminRequiredMixin, UpdateView):
    model = Branch
    form_class = BranchForm
    template_name = "branches/branch_form.html"
    success_url = reverse_lazy("branches:list")

    def form_valid(self, form):
        messages.success(self.request, f"Sucursal {form.instance.name} actualizada.")
        return super().form_valid(form)


class BranchDeleteView(AdminRequiredMixin, DeleteView):
    model = Branch
    template_name = "branches/branch_confirm_delete.html"
    success_url = reverse_lazy("branches:list")
