from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse

from .models import Task, TaskInstance, TaskChecklist, TaskChecklistItem
from .forms import TaskForm, TaskInstanceUpdateForm, TaskChecklistItemForm
from apps.common.mixins import ManagerRequiredMixin, BranchFilterMixin
from apps.activities.models import Activity


class TaskListView(LoginRequiredMixin, BranchFilterMixin, ListView):
    model = Task
    template_name = "tasks/task_list.html"
    context_object_name = "tasks"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().filter(is_active=True).select_related("module", "branch", "assigned_to")
        branch_id = self.request.GET.get("branch")
        module_id = self.request.GET.get("module")
        priority = self.request.GET.get("priority")
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        if module_id:
            qs = qs.filter(module_id=module_id)
        if priority:
            qs = qs.filter(priority=priority)
        return qs


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["checklist_items"] = self.object.checklist_items.all()
        ctx["recent_instances"] = self.object.instances.order_by("-due_date")[:5]
        return ctx


class TaskCreateView(ManagerRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        Activity.log(
            user=self.request.user,
            action="crear",
            content_type="Task",
            object_id=self.object.pk,
            description=f"Tarea '{self.object.title}' creada en {self.object.branch}",
            branch=self.object.branch,
            request=self.request,
        )
        messages.success(self.request, f"Tarea '{form.instance.title}' creada.")
        return response

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})


class TaskUpdateView(ManagerRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        Activity.log(
            user=self.request.user,
            action="actualizar",
            content_type="Task",
            object_id=self.object.pk,
            description=f"Tarea '{self.object.title}' actualizada",
            branch=self.object.branch,
            request=self.request,
        )
        messages.success(self.request, "Tarea actualizada.")
        return response

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})


class TaskDeleteView(ManagerRequiredMixin, DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:list")

    def form_valid(self, form):
        Activity.log(
            user=self.request.user,
            action="eliminar",
            content_type="Task",
            object_id=self.object.pk,
            description=f"Tarea '{self.object.title}' eliminada",
            branch=self.object.branch,
            request=self.request,
        )
        return super().form_valid(form)


class DailyTasksView(LoginRequiredMixin, ListView):
    template_name = "tasks/daily_tasks.html"
    context_object_name = "instances"

    def get_queryset(self):
        date_str = self.request.GET.get("date")
        if date_str:
            try:
                from datetime import date
                today = date.fromisoformat(date_str)
            except ValueError:
                today = timezone.now().date()
        else:
            today = timezone.now().date()

        self.selected_date = today
        qs = TaskInstance.objects.filter(
            due_date__date=today
        ).select_related("task", "branch", "assigned_to")

        user = self.request.user
        from apps.common.permissions import user_has_role, ROLE_GERENTE
        if not (user.is_superuser or user_has_role(user, ROLE_GERENTE)):
            accessible_branches = user.get_accessible_branches()
            qs = qs.filter(branch__in=accessible_branches)

        branch_id = self.request.GET.get("branch")
        if branch_id:
            qs = qs.filter(branch_id=branch_id)

        return qs.order_by("status", "task__priority", "due_date")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["selected_date"] = self.selected_date
        ctx["branches"] = self.request.user.get_accessible_branches()
        qs = self.object_list
        ctx["stats"] = {
            "total": qs.count(),
            "completada": qs.filter(status="completada").count(),
            "pendiente": qs.filter(status="pendiente").count(),
            "en_progreso": qs.filter(status="en_progreso").count(),
            "retrasada": qs.filter(status="retrasada").count(),
        }
        return ctx


class TaskInstanceDetailView(LoginRequiredMixin, DetailView):
    model = TaskInstance
    template_name = "tasks/task_instance_detail.html"
    context_object_name = "instance"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["checklist_items"] = self.object.checklist_items.select_related("checklist").all()
        return ctx


class TaskInstanceStartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        instance = get_object_or_404(TaskInstance, pk=pk)
        if instance.status == "pendiente":
            instance.status = "en_progreso"
            instance.started_at = timezone.now()
            instance.save()
            Activity.log(
                user=request.user,
                action="iniciar",
                content_type="TaskInstance",
                object_id=instance.pk,
                description=f"Tarea '{instance.task.title}' iniciada",
                branch=instance.branch,
                request=request,
            )
        return redirect("tasks:instance_detail", pk=pk)


class TaskInstanceCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        instance = get_object_or_404(TaskInstance, pk=pk)
        if instance.status in ("pendiente", "en_progreso", "retrasada"):
            instance.status = "completada"
            instance.completed_at = timezone.now()
            notes = request.POST.get("notes", "")
            if notes:
                instance.notes = notes
            instance.save()
            Activity.log(
                user=request.user,
                action="completar",
                content_type="TaskInstance",
                object_id=instance.pk,
                description=f"Tarea '{instance.task.title}' completada",
                branch=instance.branch,
                request=request,
            )
            messages.success(request, "Tarea completada.")
        return redirect("tasks:daily")


class ChecklistItemToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(TaskChecklistItem, pk=pk)
        item.is_completed = not item.is_completed
        if item.is_completed:
            item.completed_by = request.user
            item.completed_at = timezone.now()
        else:
            item.completed_by = None
            item.completed_at = None
        item.save()
        return JsonResponse({"is_completed": item.is_completed, "pk": item.pk})


class ChecklistItemCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        import json
        item = get_object_or_404(TaskChecklistItem, pk=pk)
        try:
            data = json.loads(request.body)
            comment = data.get("comment", "")
        except (json.JSONDecodeError, AttributeError):
            comment = request.POST.get("comment", "")
        item.comment = comment
        item.save(update_fields=["comment"])
        return JsonResponse({"ok": True, "comment": item.comment})


class GenerateTodayInstancesView(ManagerRequiredMixin, View):
    def post(self, request):
        from .utils import generate_instances_for_date
        count = generate_instances_for_date()
        messages.success(request, f"{count} instancias generadas para hoy.")
        return redirect("tasks:daily")
