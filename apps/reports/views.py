from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from datetime import date, timedelta

from apps.tasks.models import TaskInstance


STATUS_EMOJI = {
    "completada": "✅",
    "en_progreso": "🔄",
    "pendiente": "⏳",
    "retrasada": "🔴",
}


def _format_instance(inst):
    emoji = STATUS_EMOJI.get(inst.status, "❓")
    checklist_done = inst.checklist_items.filter(is_completed=True).count()
    checklist_total = inst.checklist_items.count()
    checklist_str = f" ({checklist_done}/{checklist_total})" if checklist_total else ""

    notes_parts = []
    if inst.notes:
        notes_parts.append(inst.notes)
    for ci in inst.checklist_items.filter(comment__gt="").select_related("checklist"):
        notes_parts.append(f"• {ci.checklist.item}: {ci.comment}")

    detail = ""
    if notes_parts:
        detail = "\n  " + "\n  ".join(notes_parts)

    return f"{emoji} *{inst.task.title}*{checklist_str}{detail}"


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "reports/reports.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["branches"] = self.request.user.get_accessible_branches()
        return ctx


class GenerateReportView(LoginRequiredMixin, View):
    def get(self, request):
        report_type = request.GET.get("type", "day")
        branch_id = request.GET.get("branch")
        date_str = request.GET.get("date")
        week_str = request.GET.get("week")

        user = request.user
        from apps.common.permissions import user_has_role, ROLE_GERENTE
        base_qs = TaskInstance.objects.select_related(
            "task", "branch", "assigned_to"
        ).prefetch_related("checklist_items__checklist")

        if not (user.is_superuser or user_has_role(user, ROLE_GERENTE)):
            base_qs = base_qs.filter(branch__in=user.get_accessible_branches())

        if branch_id:
            base_qs = base_qs.filter(branch_id=branch_id)

        if report_type == "day":
            try:
                target = date.fromisoformat(date_str) if date_str else date.today()
            except (ValueError, TypeError):
                target = date.today()

            instances = base_qs.filter(due_date__date=target)
            text = _build_day_report(target, instances, branch_id, request)

        else:  # week
            try:
                if week_str:
                    iso_year, iso_week = week_str.split("-W")
                    week_start = date.fromisocalendar(int(iso_year), int(iso_week), 1)
                else:
                    today = date.today()
                    week_start = today - timedelta(days=today.weekday())
            except (ValueError, TypeError, AttributeError):
                today = date.today()
                week_start = today - timedelta(days=today.weekday())

            week_end = week_start + timedelta(days=6)
            instances = base_qs.filter(due_date__date__range=[week_start, week_end])
            text = _build_week_report(week_start, week_end, instances, branch_id, request)

        return JsonResponse({"report": text})


def _branch_label(branch_id, request):
    if not branch_id:
        return "Todas las sucursales"
    from apps.branches.models import Branch
    try:
        return Branch.objects.get(pk=branch_id).name
    except Branch.DoesNotExist:
        return "Sucursal"


def _build_day_report(target, instances, branch_id, request):
    from django.utils.formats import date_format
    branch_name = _branch_label(branch_id, request)
    day_str = target.strftime("%d/%m/%Y")

    completed = [i for i in instances if i.status == "completada"]
    pending = [i for i in instances if i.status == "pendiente"]
    in_progress = [i for i in instances if i.status == "en_progreso"]
    delayed = [i for i in instances if i.status == "retrasada"]

    lines = [
        f"📋 *Reporte del día — {day_str}*",
        f"🏢 Sucursal: {branch_name}",
        f"",
        f"📊 *Resumen:* {len(list(instances))} tareas totales | ✅ {len(completed)} completadas | ⏳ {len(pending)} pendientes | 🔄 {len(in_progress)} en progreso | 🔴 {len(delayed)} retrasadas",
    ]

    if completed:
        lines.append(f"\n✅ *Completadas ({len(completed)}):*")
        for inst in completed:
            lines.append(_format_instance(inst))

    if in_progress:
        lines.append(f"\n🔄 *En progreso ({len(in_progress)}):*")
        for inst in in_progress:
            lines.append(_format_instance(inst))

    if delayed:
        lines.append(f"\n🔴 *Retrasadas ({len(delayed)}):*")
        for inst in delayed:
            lines.append(_format_instance(inst))

    if pending:
        lines.append(f"\n⏳ *Pendientes ({len(pending)}):*")
        for inst in pending:
            lines.append(_format_instance(inst))

    return "\n".join(lines)


def _build_week_report(week_start, week_end, instances, branch_id, request):
    branch_name = _branch_label(branch_id, request)
    start_str = week_start.strftime("%d/%m/%Y")
    end_str = week_end.strftime("%d/%m/%Y")

    all_instances = list(instances)
    completed = [i for i in all_instances if i.status == "completada"]
    delayed = [i for i in all_instances if i.status == "retrasada"]
    pending = [i for i in all_instances if i.status == "pendiente"]
    in_progress = [i for i in all_instances if i.status == "en_progreso"]

    pct = round(len(completed) / len(all_instances) * 100) if all_instances else 0

    lines = [
        f"📅 *Reporte semanal — {start_str} al {end_str}*",
        f"🏢 Sucursal: {branch_name}",
        f"",
        f"📊 *Resumen:* {len(all_instances)} tareas | ✅ {len(completed)} completadas ({pct}%) | 🔴 {len(delayed)} retrasadas | ⏳ {len(pending)} pendientes",
    ]

    # Group by day
    from collections import defaultdict
    by_day = defaultdict(list)
    for inst in all_instances:
        by_day[inst.due_date.date()].append(inst)

    for d in sorted(by_day.keys()):
        day_instances = by_day[d]
        day_completed = sum(1 for i in day_instances if i.status == "completada")
        lines.append(f"\n📆 *{d.strftime('%A %d/%m')}* — {day_completed}/{len(day_instances)} completadas")
        for inst in day_instances:
            lines.append(_format_instance(inst))

    return "\n".join(lines)
