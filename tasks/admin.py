from django.contrib import admin
from .models import Task, TaskRequest


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "start_time",
        "end_time",
        "location",
        "customer",
        "worker",
        "status",
    ]
    list_filter = ["status"]
    search_fields = ["title", "location"]
    ordering = ["-created_time"]
    autocomplete_fields = ["customer", "worker"]


@admin.register(TaskRequest)
class TaskRequestAdmin(admin.ModelAdmin):
    list_display = ["task", "worker", "status", "requested_time", "updated_time"]
    list_filter = ["status"]
    search_fields = ["task__title", "worker__user__username"]
    ordering = ["-requested_time"]
    autocomplete_fields = ["task", "worker"]
