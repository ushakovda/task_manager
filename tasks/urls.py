# tasks/urls.py
from django.urls import path
from .views import TaskCreateView, TaskListView, TaskUpdateView, TaskDeleteView

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='create_task'),
    path('<int:pk>/edit/', TaskUpdateView.as_view(), name='edit_task'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='delete_task'),
    path('<int:parent_pk>/create_subtask/', TaskCreateView.as_view(), name='create_subtask'),
]