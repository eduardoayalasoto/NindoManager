from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "content_type", "branch", "timestamp"]
    list_filter = ["action", "content_type", "branch"]
    search_fields = ["user__username", "description"]
    readonly_fields = ["user", "action", "content_type", "object_id", "description", "old_values", "new_values", "ip_address", "timestamp"]
    date_hierarchy = "timestamp"
