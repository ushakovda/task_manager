from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'performers', 'status', 'planned_effort', 'actual_effort', 'parent']
        widgets = {
            'parent': forms.Select(choices=[(None, 'Нет родительской задачи')] + [(task.id, task.name) for task in Task.objects.all()])
        }

        labels = {
            'name': 'Имя задачи',
            'description': 'Описание задачи',
            'performers': 'Исполнители',
            'status': 'Статус',
            'planned_effort': 'Плановая трудоемкость',
            'actual_effort': 'Фактическое время выполнения',
            'parent': 'Родительская задача'
        }