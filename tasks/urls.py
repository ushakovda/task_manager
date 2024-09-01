# tasks/urls.py
from django.urls import path
from .views import TaskCreateView, TaskUpdateView, TaskDeleteView, UpdateActualEffortView, UpdateTaskStatusView

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='create_task'),
    path('<int:pk>/edit/', TaskUpdateView.as_view(), name='edit_task'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='delete_task'),
    path('<int:parent_pk>/create_subtask/', TaskCreateView.as_view(), name='create_subtask'),
    path('tasks/<int:pk>/update_status/', UpdateTaskStatusView.as_view(), name='update_task_status'),
    path('tasks/<int:pk>/update_actual_effort/', UpdateActualEffortView.as_view(), name='update_actual_effort'),
]