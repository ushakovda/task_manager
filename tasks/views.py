from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

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
            return HttpResponseForbidden("Вы не можете удалить задачу, у которой есть подзадачи.")
        return super().get(request, *args, **kwargs)