
from django.contrib import admin
from django.urls import path, include

from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.TaskListView.as_view(), name='task_list'),  # Главная страница
    path('tasks/', include('tasks.urls')),  # Подключаем роуты из приложения tasks
]