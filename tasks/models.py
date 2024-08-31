from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from django.db import transaction


class Task(models.Model):
    STATUS_CHOICES = [
        ("assigned", "Назначена"),
        ("in_progress", "Выполняется"),
        ("paused", "Приостановлена"),
        ("completed", "Завершена"),
    ]

    name = models.CharField(max_length=255)  # Название
    description = models.TextField(blank=True)  # Описание
    performers = models.CharField(max_length=255, blank=True)  # Список исполнителей в виде строки
    created_at = models.DateTimeField(default=timezone.now)  # Дата и время создания
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="assigned")  # Статус 
    planned_effort = models.FloatField(default=0.0)  # Плановое время выполнения
    actual_effort = models.FloatField(default=0.0)  # Фактическое время
    completed_at = models.DateTimeField(null=True, blank=True)

    parent = models.ForeignKey(
        "self", related_name="subtasks", on_delete=models.CASCADE, null=True, blank=True
    )  # Ссылка на родительскую задачу, если это подзадача

    def __str__(self):
        return self.name

    def calculate_efforts(self) -> dict:
        subtask_planned_effort = sum(
            subtask.planned_effort for subtask in self.subtasks.all()
        )
        subtask_actual_effort = sum(
            subtask.actual_effort for subtask in self.subtasks.all()
        )
        return {
            "task_planned_effort": self.planned_effort,
            "subtask_planned_effort": subtask_planned_effort,
            "task_actual_effort": self.actual_effort,
            "subtask_actual_effort": subtask_actual_effort,
            "total_planned_effort": self.planned_effort + subtask_planned_effort,
            "total_actual_effort": self.actual_effort + subtask_actual_effort,
        }

    @property
    def task_planned_effort(self):
        return self.calculate_efforts()['task_planned_effort']

    @property
    def subtask_planned_effort(self):
        return self.calculate_efforts()['subtask_planned_effort']

    @property
    def task_actual_effort(self):
        return self.calculate_efforts()['task_actual_effort']

    @property
    def subtask_actual_effort(self):
        return self.calculate_efforts()['subtask_actual_effort']

    @property
    def total_planned_effort(self):
        return self.calculate_efforts()['total_planned_effort']

    @property
    def total_actual_effort(self):
        return self.calculate_efforts()['total_actual_effort']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                old_task = Task.objects.get(pk=self.pk)

                # Проверяем допустимость перехода в новый статус
                if not self.can_transition_to(self.status, old_task.status):
                    if old_task.status in ["completed", "paused", "deleted"]:
                        raise ValidationError("Невозможно выполнить переход в указанный статус.")
                    if self.status == 'completed':
                        raise ValidationError("Сначала приступите к выполнению")
                    elif self.status == 'paused':
                        raise ValidationError("Задача ещё не выполняется")

                if self.status == 'completed':
                    # Проверяем, что все подзадачи могут быть завершены
                    if self.subtasks.exists():
                        for subtask in self.subtasks.all():
                            if not subtask.can_transition_to('completed', subtask.status):
                                raise ValidationError("Есть незавершенные подзадачи.")
            
            # Сначала сохраняем основную задачу
            super().save(*args, **kwargs)
            
            if self.status == 'completed':
                # Завершаем все подзадачи
                for subtask in self.subtasks.all():
                    if subtask.status != 'completed':
                        subtask.status = 'completed'
                        subtask.save()

    def can_transition_to(self, new_status, old_status):
        if new_status == "completed":
            if old_status in ["paused", "assigned"]:
                return False  # Не можно завершить задачу из статусов "Приостановлена" или "Назначена"
            return old_status == "in_progress"
        elif new_status == "paused":
            return old_status == "in_progress"
        elif new_status == "deleted":
            return self.is_terminal()
        return True  # Допустимые переходы для других статусов

    def is_terminal(self):
        """Проверяет, является ли задача терминальной (т.е. не имеет подзадач)."""
        return not self.subtasks.exists()