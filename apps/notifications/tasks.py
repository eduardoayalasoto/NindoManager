from celery import shared_task
from django.utils import timezone
from django.conf import settings
import requests


def send_whatsapp_message(phone_number, message):
    """Send WhatsApp message via Meta Cloud API."""
    token = settings.WHATSAPP_API_TOKEN
    phone_id = settings.WHATSAPP_PHONE_NUMBER_ID

    if not token or not phone_id:
        return False, "WhatsApp not configured"

    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)


@shared_task(name="apps.notifications.tasks.send_daily_task_reminder")
def send_daily_task_reminder():
    """Send daily task reminders via WhatsApp at 7 AM."""
    from apps.users.models import User
    from apps.tasks.models import TaskInstance
    from .models import WhatsAppLog

    today = timezone.now().date()
    users = User.objects.filter(is_active=True, whatsapp_notifications=True).exclude(whatsapp_number="")
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
            f"Buenos días {user.first_name or user.username}! 💪\n\n"
            f"Tus tareas para hoy ({today.strftime('%d/%m/%Y')}):\n\n"
            f"{task_list}\n\n"
            f"¡A dar lo mejor en Nindo! 🥋"
        )

        success, result = send_whatsapp_message(user.whatsapp_number, message)
        log_status = "sent" if success else "failed"
        WhatsAppLog.objects.create(
            recipient=user.whatsapp_number,
            message=message,
            status=log_status,
            error_message="" if success else str(result),
            sent_at=timezone.now() if success else None,
        )
        if success:
            sent_count += 1

    return f"Daily reminders sent to {sent_count} users"


@shared_task(name="apps.notifications.tasks.send_weekly_summary")
def send_weekly_summary():
    """Send weekly summary via WhatsApp on Fridays at 5 PM."""
    from apps.users.models import User
    from apps.tasks.models import TaskInstance
    from .models import WhatsAppLog
    from datetime import timedelta

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())

    users = User.objects.filter(is_active=True, whatsapp_notifications=True).exclude(whatsapp_number="")
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
            f"Resumen semanal Nindo 📊\n\n"
            f"Semana del {week_start.strftime('%d/%m')} al {today.strftime('%d/%m/%Y')}\n\n"
            f"✅ Completadas: {completed}/{total} ({pct}%)\n"
            f"⚠️ Retrasadas: {overdue}\n\n"
            f"¡Excelente semana! 🥋"
        )

        success, result = send_whatsapp_message(user.whatsapp_number, message)
        log_status = "sent" if success else "failed"
        WhatsAppLog.objects.create(
            recipient=user.whatsapp_number,
            message=message,
            status=log_status,
            error_message="" if success else str(result),
            sent_at=timezone.now() if success else None,
        )
        if success:
            sent_count += 1

    return f"Weekly summaries sent to {sent_count} users"


@shared_task(name="apps.notifications.tasks.send_task_assignment_notification")
def send_task_assignment_notification(task_instance_id):
    """Send WhatsApp notification when a task is assigned."""
    from apps.tasks.models import TaskInstance
    from .models import WhatsAppLog

    try:
        instance = TaskInstance.objects.select_related("task", "assigned_to", "branch").get(pk=task_instance_id)
    except TaskInstance.DoesNotExist:
        return "TaskInstance not found"

    user = instance.assigned_to
    if not user or not user.whatsapp_notifications or not user.whatsapp_number:
        return "User not configured for WhatsApp"

    message = (
        f"Nueva tarea asignada 📋\n\n"
        f"*{instance.task.title}*\n"
        f"Sucursal: {instance.branch}\n"
        f"Para: {instance.due_date.strftime('%d/%m/%Y')}\n"
        f"Prioridad: {instance.task.get_priority_display()}\n\n"
        f"Ingresa a Nindo Manager para más detalles."
    )

    success, result = send_whatsapp_message(user.whatsapp_number, message)
    log_status = "sent" if success else "failed"
    WhatsAppLog.objects.create(
        recipient=user.whatsapp_number,
        message=message,
        status=log_status,
        error_message="" if success else str(result),
        sent_at=timezone.now() if success else None,
    )
    return f"Notification {'sent' if success else 'failed'} to {user}"
