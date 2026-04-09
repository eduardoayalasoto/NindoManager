from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class TaskModule(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Ícono")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    class Meta:
        verbose_name = "Módulo de tareas"
        verbose_name_plural = "Módulos de tareas"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Task(TimeStampedModel):
    PRIORITY_CHOICES = [
        ("alta", "Alta"),
        ("media", "Media"),
        ("baja", "Baja"),
    ]
    STATUS_CHOICES = [
        ("pendiente", "Pendiente"),
        ("en_progreso", "En progreso"),
        ("completada", "Completada"),
        ("cancelada", "Cancelada"),
    ]
    DAYS_OF_WEEK = [
        ("Monday", "Lunes"),
        ("Tuesday", "Martes"),
        ("Wednesday", "Miércoles"),
        ("Thursday", "Jueves"),
        ("Friday", "Viernes"),
        ("Saturday", "Sábado"),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    module = models.ForeignKey(
        TaskModule,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="tasks",
        verbose_name="Módulo",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Sucursal",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
        verbose_name="Creado por",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_tasks",
        verbose_name="Asignado a",
    )
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="media", verbose_name="Prioridad"
    )
    estimated_duration = models.PositiveIntegerField(
        default=30, verbose_name="Duración estimada (min)"
    )
    is_recurring = models.BooleanField(default=False, verbose_name="Es recurrente")
    recurring_days = models.JSONField(
        default=list, blank=True,
        verbose_name="Días de recurrencia",
        help_text='Ej: ["Monday", "Wednesday", "Friday"]'
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pendiente", verbose_name="Estado"
    )
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Fecha límite")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completada en")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.branch})"

    def get_recurring_days_display(self):
        day_map = dict(self.DAYS_OF_WEEK)
        return [day_map.get(d, d) for d in self.recurring_days]


class TaskChecklist(TimeStampedModel):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="checklist_items", verbose_name="Tarea"
    )
    item = models.CharField(max_length=300, verbose_name="Ítem")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    class Meta:
        verbose_name = "Ítem de checklist"
        verbose_name_plural = "Ítems de checklist"
        ordering = ["order"]

    def __str__(self):
        return f"{self.task.title} - {self.item}"


class TaskInstance(TimeStampedModel):
    STATUS_CHOICES = [
        ("pendiente", "Pendiente"),
        ("en_progreso", "En progreso"),
        ("completada", "Completada"),
        ("retrasada", "Retrasada"),
    ]

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="instances", verbose_name="Tarea"
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="task_instances",
        verbose_name="Sucursal",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="task_instances",
        verbose_name="Asignado a",
    )
    due_date = models.DateTimeField(verbose_name="Fecha límite")
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="pendiente", verbose_name="Estado"
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Iniciada en")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completada en")
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Instancia de tarea"
        verbose_name_plural = "Instancias de tareas"
        ordering = ["due_date", "status"]

    def __str__(self):
        return f"{self.task.title} - {self.due_date.date()}"

    def is_overdue(self):
        from django.utils import timezone
        return (
            self.status not in ("completada",)
            and self.due_date < timezone.now()
        )


class TaskChecklistItem(TimeStampedModel):
    checklist = models.ForeignKey(
        TaskChecklist,
        on_delete=models.CASCADE,
        related_name="instance_items",
        verbose_name="Ítem de checklist",
    )
    task_instance = models.ForeignKey(
        TaskInstance,
        on_delete=models.CASCADE,
        related_name="checklist_items",
        verbose_name="Instancia de tarea",
    )
    is_completed = models.BooleanField(default=False, verbose_name="Completado")
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="completed_checklist_items",
        verbose_name="Completado por",
    )
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completado en")

    class Meta:
        verbose_name = "Ítem de checklist (instancia)"
        verbose_name_plural = "Ítems de checklist (instancias)"
        unique_together = ["checklist", "task_instance"]

    def __str__(self):
        return f"{self.checklist.item} - {'✓' if self.is_completed else '○'}"
