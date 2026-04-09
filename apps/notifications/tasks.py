from celery import shared_task
from django.utils import timezone

from .whatsapp import send_whatsapp


def _log_whatsapp(recipient, message, success, error=""):
    from .models import WhatsAppLog
    WhatsAppLog.objects.create(
        recipient=recipient,
        message=message,
        status="sent" if success else "failed",
        error_message=error,
        sent_at=timezone.now() if success else None,
    )


@shared_task(name="apps.notifications.tasks.send_daily_task_reminder")
def send_daily_task_reminder():
    """Send daily task reminders via WhatsApp at 7 AM."""
    from apps.users.models import User
    from apps.tasks.models import TaskInstance

    today = timezone.now().date()
    users = User.objects.filter(
        is_active=True, whatsapp_notifications=True
    ).exclude(whatsapp_number="")
    sent_count = 0

    for user in users:
        instances = TaskInstance.objects.filter(
            assigned_to=user,
            due_date__date=today,
            status__in=["pendiente", "en_progreso"],
        ).select_related("task")

        if not instances.exists():
            continue

        task_list = "\n".join([f"• {i.task.title}" for i in instances[:10]])
        message = (
            f"Buenos días {user.first_name or user.username}!\n\n"
            f"Tus tareas para hoy ({today.strftime('%d/%m/%Y')}):\n\n"
            f"{task_list}\n\n"
            f"A dar lo mejor en Nindo."
        )

        success, result = send_whatsapp(user.whatsapp_number, message)
        _log_whatsapp(user.whatsapp_number, message, success, "" if success else result)
        if success:
            sent_count += 1

    return f"Daily reminders sent to {sent_count} users"


@shared_task(name="apps.notifications.tasks.send_weekly_summary")
def send_weekly_summary():
    """Send weekly summary via WhatsApp on Fridays at 5 PM."""
    from apps.users.models import User
    from apps.tasks.models import TaskInstance
    from datetime import timedelta

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())

    users = User.objects.filter(
        is_active=True, whatsapp_notifications=True
    ).exclude(whatsapp_number="")
    sent_count = 0

    for user in users:
        instances = TaskInstance.objects.filter(
            assigned_to=user,
            due_date__date__gte=week_start,
            due_date__date__lte=today,
        )
        total = instances.count()
        completed = instances.filter(status="completada").count()
        overdue = instances.filter(status="retrasada").count()
        pct = int((completed / total * 100) if total > 0 else 0)

        message = (
            f"Resumen semanal Nindo\n\n"
            f"Semana del {week_start.strftime('%d/%m')} al {today.strftime('%d/%m/%Y')}\n\n"
            f"Completadas: {completed}/{total} ({pct}%)\n"
            f"Retrasadas: {overdue}\n\n"
            f"Excelente semana."
        )

        success, result = send_whatsapp(user.whatsapp_number, message)
        _log_whatsapp(user.whatsapp_number, message, success, "" if success else result)
        if success:
            sent_count += 1

    return f"Weekly summaries sent to {sent_count} users"


@shared_task(name="apps.notifications.tasks.send_task_assignment_notification")
def send_task_assignment_notification(task_instance_id):
    """Send WhatsApp notification when a task instance is assigned."""
    from apps.tasks.models import TaskInstance

    try:
        instance = TaskInstance.objects.select_related(
            "task", "assigned_to", "branch"
        ).get(pk=task_instance_id)
    except TaskInstance.DoesNotExist:
        return "TaskInstance not found"

    user = instance.assigned_to
    if not user or not user.whatsapp_notifications or not user.whatsapp_number:
        return "User not configured for WhatsApp"

    message = (
        f"Nueva tarea asignada\n\n"
        f"{instance.task.title}\n"
        f"Sucursal: {instance.branch}\n"
        f"Para: {instance.due_date.strftime('%d/%m/%Y')}\n"
        f"Prioridad: {instance.task.get_priority_display()}\n\n"
        f"Ingresa a Nindo Manager para ver el detalle."
    )

    success, result = send_whatsapp(user.whatsapp_number, message)
    _log_whatsapp(
        user.whatsapp_number, message, success, "" if success else result
    )
    return f"Notification {'sent' if success else 'failed'} to {user}"
