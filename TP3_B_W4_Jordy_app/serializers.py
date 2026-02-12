from rest_framework import serializers
from .models import TaskList, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'important', 'completed']


class TaskListSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = TaskList
        fields = ['id', 'name', 'tasks']
