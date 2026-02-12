from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TaskList, Task
from .serializers import TaskListSerializer, TaskSerializer


class TaskListListView(APIView):
    http_method_names = ['get', 'post']
    
    def get(self, request):
        tasklists = TaskList.objects.all().order_by('name')
        serializer = TaskListSerializer(tasklists, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskListSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskListDetailView(APIView):
    http_method_names = ['get', 'put', 'delete']

    def get(self, request, id):
        tasklist = get_object_or_404(TaskList, id=id)
        serializer = TaskListSerializer(tasklist, context={'request': request})
        return Response(serializer.data)

    def put(self, request, id):
        tasklist = get_object_or_404(TaskList, id=id)
        serializer = TaskListSerializer(tasklist, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        tasklist = get_object_or_404(TaskList, id=id)
        tasklist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListView(APIView):
    http_method_names = ['get', 'post']
    
    def get(self, request, tasklist_id):
        tasks = Task.objects.filter(task_list_id=tasklist_id).order_by('name')
        serializer = TaskSerializer(tasks, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, tasklist_id):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(task_list_id=tasklist_id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    http_method_names = ['get', 'put', 'delete']

    def get(self, request, tasklist_id, id):
        task = get_object_or_404(Task, id=id, task_list_id=tasklist_id)
        serializer = TaskSerializer(task, context={'request': request})
        return Response(serializer.data)

    def put(self, request, tasklist_id, id):
        task = get_object_or_404(Task, id=id, task_list_id=tasklist_id)
        serializer = TaskSerializer(task, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, tasklist_id, id):
        task = get_object_or_404(Task, id=id, task_list_id=tasklist_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

