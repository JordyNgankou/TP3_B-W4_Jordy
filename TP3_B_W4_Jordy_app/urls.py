from django.urls import path

from .views import (
    TaskListListView,
    TaskListDetailView,
    TaskListView,
    TaskDetailView,
)

urlpatterns = [
    path('api/tasklists/', TaskListListView.as_view()),
    path('api/tasklists/<uuid:id>/', TaskListDetailView.as_view()),
    path('api/tasklists/<uuid:tasklist_id>/tasks/', TaskListView.as_view()),
    path('api/tasklists/<uuid:tasklist_id>/tasks/<uuid:id>/', TaskDetailView.as_view()),
]

