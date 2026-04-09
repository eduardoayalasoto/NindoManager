import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("nindo")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "generate-daily-tasks": {
        "task": "apps.tasks.tasks.generate_daily_task_instances",
        "schedule": crontab(hour=0, minute=0),
    },
    "send-daily-reminder": {
        "task": "apps.notifications.tasks.send_daily_task_reminder",
        "schedule": crontab(hour=7, minute=0),
    },
    "send-weekly-summary": {
        "task": "apps.notifications.tasks.send_weekly_summary",
        "schedule": crontab(hour=17, minute=0, day_of_week=4),
    },
    "mark-overdue-tasks": {
        "task": "apps.tasks.tasks.mark_overdue_tasks",
        "schedule": crontab(hour=23, minute=0),
    },
}
