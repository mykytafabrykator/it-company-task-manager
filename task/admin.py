from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from task.models import TaskType, Position, Worker, Team, Project, Task


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position",)
    fieldsets = UserAdmin.fieldsets + (
        (("Additional info", {"fields": ("position",)}),)
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "position",
                    )
                },
            ),
        )
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ("name", )
    list_filter = ("assignees", "task_type", "priority")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ("name", )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ("name", )


admin.site.register(TaskType)
admin.site.register(Position)
admin.site.unregister(Group)
