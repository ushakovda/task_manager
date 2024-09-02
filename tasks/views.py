from typing import Dict, Any
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import Task
from .forms import TaskForm


class TaskCreateView(CreateView):
    """
    Представление для создания новой задачи.
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('task_list')

    def get_initial(self) -> Dict[str, Any]:
        """
        Возвращает начальные данные для формы. Если в URL есть параметр parent_pk,
        добавляет его в начальные данные формы.
        """
        initial = super().get_initial()
        parent_pk = self.kwargs.get('parent_pk')
        if parent_pk:
            initial['parent'] = Task.objects.get(pk=parent_pk)
        return initial


class TaskListView(ListView):
    """
    Представление для отображения списка задач.
    """
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Возвращает контекст для шаблона.
        """
        context = super().get_context_data(**kwargs)
        return context


class TaskUpdateView(UpdateView):
    """
    Представление для редактирования существующей задачи.
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/edit_task.html'
    success_url = reverse_lazy('task_list')


class TaskDeleteView(DeleteView):
    """
    Представление для удаления задачи. Запрещает удаление задач, у которых есть подзадачи.
    """
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

    def get(self, request, *args, **kwargs) -> Any:
        """
        Проверяет, можно ли удалить задачу. Если нет, возвращает ответ с ошибкой.
        """
        task = self.get_object()
        if not task.is_terminal:
            return HttpResponseForbidden(
                'Вы не можете удалить задачу, у которой есть подзадачи.'
            )
        return super().get(request, *args, **kwargs)


class UpdateTaskStatusView(View):
    """
    Представление для обновления статуса задачи через AJAX.
    """
    def post(self, request, pk: int) -> JsonResponse:
        """
        Обрабатывает POST запрос для обновления статуса задачи.
        """
        task = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get('status')

        if new_status not in dict(Task.STATUS_CHOICES).keys():
            return JsonResponse({'success': False, 'message': 'Некорректный статус.'})

        try:
            task.status = new_status
            task.save()
            return JsonResponse({
                'success': True,
                'message': 'Статус обновлен успешно.',
                'new_status': task.status
            })
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})


class UpdateActualEffortView(View):
    """
    Представление для обновления фактического времени затраченного на задачу через AJAX.
    """
    def post(self, request, pk: int) -> JsonResponse:
        """
        Обрабатывает POST запрос для обновления фактического времени задачи.
        """
        task = get_object_or_404(Task, pk=pk)
        actual_effort = request.POST.get('actual_effort')

        if not actual_effort:
            return JsonResponse({'success': False, 'message': 'Необходимо указать фактическое время.'})

        try:
            task.total_actual_effort = actual_effort
            task.save()
            return JsonResponse({'success': True, 'message': 'Фактическое время обновлено.'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})


class TaskDetailAjaxView(View):
    """
    Представление для получения деталей задачи через AJAX.
    """
    def get(self, request, *args, **kwargs) -> JsonResponse:
        """
        Обрабатывает GET запрос для получения деталей задачи.
        """
        task_id = self.kwargs.get('pk')
        task = get_object_or_404(Task, pk=task_id)

        data = {
            'name': task.name,
            'description': task.description,
            'performers': task.performers,
            'status': task.get_status_display(),
            'planned_effort': task.planned_effort,
            'actual_effort': task.actual_effort,
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'completed_at': task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else '',
            'is_terminal': task.is_terminal()
        }
        return JsonResponse(data)
