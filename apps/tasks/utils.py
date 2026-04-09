from django.utils import timezone
from .models import Task, TaskInstance, TaskChecklist, TaskChecklistItem


def generate_instances_for_date(date=None):
    """Generate TaskInstances for all recurring tasks on a given date."""
    if date is None:
        date = timezone.now().date()

    day_english = date.strftime("%A")  # "Monday", "Tuesday", etc.
    created_count = 0

    recurring_tasks = Task.objects.filter(
        is_recurring=True,
        is_active=True,
        status__in=["pendiente", "en_progreso"],
    )

    for task in recurring_tasks:
        if day_english not in (task.recurring_days or []):
            continue

        due_datetime = timezone.make_aware(
            timezone.datetime.combine(date, timezone.datetime.min.time().replace(hour=23, minute=59))
        )

        # Avoid duplicates
        if TaskInstance.objects.filter(task=task, due_date__date=date).exists():
            continue

        instance = TaskInstance.objects.create(
            task=task,
            branch=task.branch,
            assigned_to=task.assigned_to,
            due_date=due_datetime,
            status="pendiente",
        )

        # Create checklist items
        for checklist_item in task.checklist_items.all():
            TaskChecklistItem.objects.create(
                checklist=checklist_item,
                task_instance=instance,
                is_completed=False,
            )

        created_count += 1

    return created_count


def mark_overdue_instances():
    """Mark pending/in_progress instances past their due date as overdue."""
    now = timezone.now()
    updated = TaskInstance.objects.filter(
        status__in=["pendiente", "en_progreso"],
        due_date__lt=now,
    ).update(status="retrasada")
    return updated
