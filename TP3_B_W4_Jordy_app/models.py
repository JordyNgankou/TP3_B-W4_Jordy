from django.db import models
import uuid

class TaskList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    important = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE, related_name='tasks')
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
