from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ValidationError

from .models import Task
from .forms import TaskForm


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/create_task.html'
    success_url = reverse_lazy('task_list')

    def get_initial(self):
        initial = super().get_initial()
        parent_pk = self.kwargs.get('parent_pk')
        if parent_pk:
            initial['parent'] = Task.objects.get(pk=parent_pk)
        return initial


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/edit_task.html'
    success_url = reverse_lazy('task_list')


class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task_list')

    def get(self, request, *args, **kwargs):
        task = self.get_object()
        if not task.is_terminal:
            return HttpResponseForbidden(
                'Вы не можете удалить задачу, у которой есть подзадачи.'
            )
        return super().get(request, *args, **kwargs)


class UpdateTaskStatusView(View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        new_status = request.POST.get('status')

        # Проверяем, что новый статус допустим
        if new_status not in dict(Task.STATUS_CHOICES).keys():
            return JsonResponse({'success': False, 'message': 'Некорректный статус.'})

        try:
            # Устанавливаем новый статус и сохраняем задачу
            task.status = new_status
            task.save()

            return JsonResponse({
                'success': True,
                'message': 'Статус обновлен успешно.',
                'new_status': task.status  # Возвращаем новый статус
            })
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': str(e)})
        

class UpdateActualEffortView(View):
    def post(self, request, pk):
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
    def get(self, request, *args, **kwargs):
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
