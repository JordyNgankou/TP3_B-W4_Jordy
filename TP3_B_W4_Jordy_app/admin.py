from django.contrib import admin
from .models import TaskList, Task


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'important', 'completed', 'task_list']
    list_filter = ['important', 'completed', 'task_list']
    search_fields = ['name']
