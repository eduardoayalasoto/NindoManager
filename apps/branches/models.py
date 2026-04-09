from django.db import models
from apps.common.models import TimeStampedModel


class Branch(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    code = models.CharField(max_length=10, unique=True, verbose_name="Código")
    address = models.TextField(blank=True, verbose_name="Dirección")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_task_stats_today(self):
        from django.utils import timezone
        from apps.tasks.models import TaskInstance
        today = timezone.now().date()
        instances = TaskInstance.objects.filter(branch=self, due_date__date=today)
        return {
            "total": instances.count(),
            "completed": instances.filter(status="completada").count(),
            "pending": instances.filter(status="pendiente").count(),
            "in_progress": instances.filter(status="en_progreso").count(),
            "overdue": instances.filter(status="retrasada").count(),
        }
