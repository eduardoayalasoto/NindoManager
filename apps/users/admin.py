from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class NindoUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "is_active", "is_staff"]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["username", "email", "first_name", "last_name"]
    fieldsets = UserAdmin.fieldsets + (
        ("Nindo", {"fields": ("avatar", "phone", "whatsapp_number", "whatsapp_notifications")}),
    )
