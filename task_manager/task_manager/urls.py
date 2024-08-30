from django.contrib import admin
from django.urls import path
from tasks import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='create_task'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='edit_task'),
    path('tasks/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete_task'),
]