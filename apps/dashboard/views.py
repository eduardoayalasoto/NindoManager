from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from apps.tasks.models import TaskInstance, Task
from apps.activities.models import Activity
from apps.branches.models import Branch
from apps.common.permissions import user_has_role, ROLE_GERENTE


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()

        branches = user.get_accessible_branches()
        instances_today = TaskInstance.objects.filter(
            due_date__date=today, branch__in=branches
        )

        ctx["today"] = today
        ctx["branches"] = branches
        ctx["stats"] = {
            "total": instances_today.count(),
            "completada": instances_today.filter(status="completada").count(),
            "pendiente": instances_today.filter(status="pendiente").count(),
            "en_progreso": instances_today.filter(status="en_progreso").count(),
            "retrasada": instances_today.filter(status="retrasada").count(),
        }
        ctx["recent_instances"] = instances_today.select_related(
            "task", "branch", "assigned_to"
        ).order_by("status", "task__priority")[:10]
        ctx["recent_activities"] = Activity.objects.filter(
            branch__in=branches
        ).select_related("user", "branch").order_by("-timestamp")[:8]

        return ctx


class DashboardDataView(LoginRequiredMixin, TemplateView):
    """JSON endpoint for Vue.js dashboard components."""

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        branches = user.get_accessible_branches()

        # Stats for last 7 days
        weekly_data = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            instances = TaskInstance.objects.filter(due_date__date=day, branch__in=branches)
            weekly_data.append({
                "date": day.strftime("%d/%m"),
                "total": instances.count(),
                "completed": instances.filter(status="completada").count(),
                "overdue": instances.filter(status="retrasada").count(),
            })

        today_instances = TaskInstance.objects.filter(
            due_date__date=today, branch__in=branches
        ).select_related("task", "branch", "assigned_to")

        instances_data = [
            {
                "id": i.pk,
                "title": i.task.title,
                "branch": i.branch.name,
                "status": i.status,
                "priority": i.task.priority,
                "assigned_to": str(i.assigned_to) if i.assigned_to else None,
            }
            for i in today_instances[:20]
        ]

        return JsonResponse({
            "weekly_data": weekly_data,
            "today_instances": instances_data,
            "stats": {
                "total": today_instances.count(),
                "completed": today_instances.filter(status="completada").count(),
                "pending": today_instances.filter(status="pendiente").count(),
                "in_progress": today_instances.filter(status="en_progreso").count(),
                "overdue": today_instances.filter(status="retrasada").count(),
            },
        })


class RedirectToDashboard(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        from django.shortcuts import redirect
        return redirect("dashboard:index")
