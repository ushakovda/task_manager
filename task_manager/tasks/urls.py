from django.urls import path
from .views import TaskCreateView, TaskListView, TaskUpdateView, TaskDeleteView

urlpatterns = [
    path('', TaskListView.as_view(), name='task_list'),
    path('create/', TaskCreateView.as_view(), name='create_task'),
    path('<int:pk>/edit/', TaskUpdateView.as_view(), name='edit_task'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='delete_task'),
]