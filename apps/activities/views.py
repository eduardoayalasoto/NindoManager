from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.http import HttpResponse
import csv

from .models import Activity
from apps.common.mixins import BranchFilterMixin
from apps.common.permissions import user_has_role, ROLE_GERENTE


class ActivityListView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = "activities/activity_list.html"
    context_object_name = "activities"
    paginate_by = 30

    def get_queryset(self):
        qs = Activity.objects.select_related("user", "branch")
        user = self.request.user

        if not (user.is_superuser or user_has_role(user, ROLE_GERENTE)):
            accessible_branches = user.get_accessible_branches()
            qs = qs.filter(branch__in=accessible_branches)

        action = self.request.GET.get("action")
        content_type = self.request.GET.get("content_type")
        branch_id = self.request.GET.get("branch")

        if action:
            qs = qs.filter(action=action)
        if content_type:
            qs = qs.filter(content_type=content_type)
        if branch_id:
            qs = qs.filter(branch_id=branch_id)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["branches"] = self.request.user.get_accessible_branches()
        ctx["action_choices"] = Activity.ACTION_CHOICES
        return ctx


class ActivityDetailView(LoginRequiredMixin, DetailView):
    model = Activity
    template_name = "activities/activity_detail.html"
    context_object_name = "activity"


class ActivityExportView(LoginRequiredMixin, ListView):
    model = Activity

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="actividades.csv"'
        writer = csv.writer(response)
        writer.writerow(["Fecha", "Usuario", "Acción", "Tipo", "Descripción", "Sucursal", "IP"])
        qs = Activity.objects.select_related("user", "branch")
        for a in qs[:1000]:
            writer.writerow([
                a.timestamp.strftime("%Y-%m-%d %H:%M"),
                str(a.user),
                a.get_action_display(),
                a.content_type,
                a.description,
                str(a.branch) if a.branch else "",
                a.ip_address or "",
            ])
        return response
