from django.contrib import admin
from .models import Role, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "can_manage_users", "can_manage_tasks", "can_view_all_branches"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "branch", "is_active", "assigned_at"]
    list_filter = ["role", "branch", "is_active"]
    search_fields = ["user__username", "user__email"]
