from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Role(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    can_manage_users = models.BooleanField(default=False)
    can_manage_branches = models.BooleanField(default=False)
    can_manage_tasks = models.BooleanField(default=False)
    can_view_all_branches = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_view_activities = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserRole(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Usuario",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Rol",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="Sucursal",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_roles",
        verbose_name="Asignado por",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Rol de usuario"
        verbose_name_plural = "Roles de usuarios"
        unique_together = ["user", "role", "branch"]

    def __str__(self):
        return f"{self.user} - {self.role} ({self.branch})"
