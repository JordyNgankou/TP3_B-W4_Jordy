from django.urls import path

from .views import (
    TaskListListView,
    TaskListDetailView,
    TaskListView,
    TaskDetailView,
)

urlpatterns = [
    path('api/tasklists/', TaskListListView.as_view()),
    path('api/tasklists/<int:id>/', TaskListDetailView.as_view()),
    path('api/tasklists/<int:tasklist_id>/tasks/', TaskListView.as_view()),
    path('api/tasklists/<int:tasklist_id>/tasks/<int:id>/', TaskDetailView.as_view()),
]

