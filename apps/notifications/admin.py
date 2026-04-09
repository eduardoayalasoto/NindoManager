from django.contrib import admin
from .models import Notification, EmailLog, WhatsAppLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "notification_type", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read"]
    search_fields = ["user__username", "title"]


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ["recipient", "subject", "status", "sent_at"]
    list_filter = ["status"]
    readonly_fields = ["recipient", "subject", "body", "status", "error_message", "sent_at", "created_at"]


@admin.register(WhatsAppLog)
class WhatsAppLogAdmin(admin.ModelAdmin):
    list_display = ["recipient", "status", "sent_at"]
    list_filter = ["status"]
