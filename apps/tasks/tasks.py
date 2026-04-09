from celery import shared_task
from django.utils import timezone


@shared_task(name="apps.tasks.tasks.generate_daily_task_instances")
def generate_daily_task_instances():
    """Generate task instances for today."""
    from .utils import generate_instances_for_date
    today = timezone.now().date()
    count = generate_instances_for_date(today)
    return f"Generated {count} task instances for {today}"


@shared_task(name="apps.tasks.tasks.mark_overdue_tasks")
def mark_overdue_tasks():
    """Mark tasks that are past due as overdue."""
    from .utils import mark_overdue_instances
    count = mark_overdue_instances()
    return f"Marked {count} instances as overdue"
