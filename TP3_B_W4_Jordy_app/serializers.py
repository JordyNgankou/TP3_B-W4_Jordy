from rest_framework.serializers import ModelSerializer
from .models import TaskList, Task


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'important', 'completed']


class TaskListSerializer(ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = TaskList
        fields = ['id', 'name', 'tasks']
