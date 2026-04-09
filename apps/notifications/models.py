from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel


class Notification(TimeStampedModel):
    TYPE_CHOICES = [
        ("task", "Tarea"),
        ("alert", "Alerta"),
        ("system", "Sistema"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Usuario",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    notification_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default="task", verbose_name="Tipo"
    )
    related_task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="notifications",
        verbose_name="Tarea relacionada",
    )
    is_read = models.BooleanField(default=False, verbose_name="Leída")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.title}"


class EmailLog(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("sent", "Enviado"),
        ("failed", "Fallido"),
    ]

    recipient = models.EmailField(verbose_name="Destinatario")
    subject = models.CharField(max_length=300, verbose_name="Asunto")
    body = models.TextField(verbose_name="Cuerpo")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Estado"
    )
    error_message = models.TextField(blank=True, verbose_name="Error")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Enviado en")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de email"
        verbose_name_plural = "Logs de emails"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.subject} ({self.status})"


class WhatsAppLog(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("sent", "Enviado"),
        ("failed", "Fallido"),
    ]

    recipient = models.CharField(max_length=20, verbose_name="Destinatario")
    message = models.TextField(verbose_name="Mensaje")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Estado"
    )
    error_message = models.TextField(blank=True, verbose_name="Error")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Enviado en")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de WhatsApp"
        verbose_name_plural = "Logs de WhatsApp"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.status}"
