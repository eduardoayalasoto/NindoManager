from django.contrib import admin
from .models import Task, TaskInstance, TaskModule, TaskChecklist, TaskChecklistItem


@admin.register(TaskModule)
class TaskModuleAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]
    ordering = ["order"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "branch", "module", "priority", "is_recurring", "status", "assigned_to"]
    list_filter = ["branch", "module", "priority", "is_recurring", "status"]
    search_fields = ["title"]
    filter_horizontal = []


@admin.register(TaskInstance)
class TaskInstanceAdmin(admin.ModelAdmin):
    list_display = ["task", "branch", "due_date", "status", "assigned_to"]
    list_filter = ["branch", "status", "due_date"]
    search_fields = ["task__title"]
    date_hierarchy = "due_date"


@admin.register(TaskChecklist)
class TaskChecklistAdmin(admin.ModelAdmin):
    list_display = ["task", "item", "order"]
    list_filter = ["task__branch"]
