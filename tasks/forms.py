from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'performers', 'status', 'planned_effort', 'actual_effort', 'parent', 'created_at']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'performers': 'Исполнители',
            'status': 'Статус',
            'planned_effort': 'Плановая трудоёмкость задачи',
            'actual_effort': 'Фактическое время выполнения',
            'parent': 'Родительская задача',
            'created_at': 'Дата и время создания',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].widget = forms.Select(
            choices=[(None, 'Нет родительской задачи')] + [(task.id, task.name) for task in Task.objects.all()]
        )
        self.fields['created_at'].disabled = True