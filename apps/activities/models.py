from django.db import models
from django.conf import settings


class Activity(models.Model):
    ACTION_CHOICES = [
        ("crear", "Crear"),
        ("actualizar", "Actualizar"),
        ("completar", "Completar"),
        ("eliminar", "Eliminar"),
        ("asignar", "Asignar"),
        ("iniciar", "Iniciar"),
        ("login", "Login"),
        ("logout", "Logout"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activities",
        verbose_name="Usuario",
    )
    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="activities",
        verbose_name="Sucursal",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Acción")
    content_type = models.CharField(max_length=50, verbose_name="Tipo de contenido")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del objeto")
    description = models.TextField(verbose_name="Descripción")
    old_values = models.JSONField(null=True, blank=True, verbose_name="Valores anteriores")
    new_values = models.JSONField(null=True, blank=True, verbose_name="Valores nuevos")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.action} {self.content_type} - {self.timestamp}"

    @classmethod
    def log(cls, user, action, content_type, description, object_id=None,
            branch=None, old_values=None, new_values=None, request=None):
        ip = None
        if request:
            ip = request.META.get("REMOTE_ADDR")
        return cls.objects.create(
            user=user,
            branch=branch,
            action=action,
            content_type=content_type,
            object_id=object_id,
            description=description,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip,
        )
