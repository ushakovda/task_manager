from typing import Dict, Optional
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

    name: str = models.CharField(max_length=255)  # Название
    description: str = models.TextField(blank=True)  # Описание
    performers: str = models.CharField(max_length=255, blank=True)  # Список исполнителей в виде строки
    created_at: timezone.datetime = models.DateTimeField(default=timezone.now)  # Дата и время создания
    status: str = models.CharField(max_length=50, choices=STATUS_CHOICES, default="assigned")  # Статус 
    planned_effort: float = models.FloatField(default=0.0)  # Плановое время выполнения
    actual_effort: float = models.FloatField(default=0.0)  # Фактическое время
    completed_at: Optional[timezone.datetime] = models.DateTimeField(null=True, blank=True)  # Дата завершения (опционально)

    parent: Optional["Task"] = models.ForeignKey(
        "self", related_name="subtasks", on_delete=models.CASCADE, null=True, blank=True
    )  # Ссылка на родительскую задачу, если это подзадача

    def __str__(self) -> str:
        return self.name

    def calculate_efforts(self) -> Dict[str, float]:
        """
        Вычисляет плановое и фактическое время для задачи и ее подзадач.
        
        Returns:
            dict: Словарь с плановыми и фактическими временами для задачи и подзадач.
        """
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
    def task_planned_effort(self) -> float:
        return self.calculate_efforts()['task_planned_effort']

    @property
    def subtask_planned_effort(self) -> float:
        return self.calculate_efforts()['subtask_planned_effort']

    @property
    def task_actual_effort(self) -> float:
        return self.calculate_efforts()['task_actual_effort']

    @property
    def subtask_actual_effort(self) -> float:
        return self.calculate_efforts()['subtask_actual_effort']

    @property
    def total_planned_effort(self) -> float:
        return self.calculate_efforts()['total_planned_effort']

    @property
    def total_actual_effort(self) -> float:
        return self.calculate_efforts()['total_actual_effort']
    
    @total_actual_effort.setter
    def total_actual_effort(self, value: float):
        self._actual_effort = value

    def save(self, *args, **kwargs) -> None:
        """
        Переопределенный метод сохранения для проверки допустимости переходов статусов 
        и обеспечения целостности данных для задачи и подзадач.
        """
        with transaction.atomic():
            if self.pk:
                old_task = Task.objects.get(pk=self.pk)
                
                if old_task.status != 'completed' and self.status == 'completed':
                    if self.subtasks.filter(status__in=['in_progress', 'assigned']).exists():
                        raise ValidationError("Есть незавершенные подзадачи.")
            
                # Проверяем допустимость перехода в новый статус
                if not self.can_transition_to(self.status, old_task.status):
                    if old_task.status in ["completed", "paused", "deleted"]:
                        raise ValidationError("Невозможно выполнить переход в указанный статус.")
                    if self.status == 'completed':
                        raise ValidationError("Проверьте статус текущей задачи и подзадач, они должны выполняться")
                    elif self.status == 'paused':
                        raise ValidationError("Задача ещё не выполняется")

                if self.status == 'completed':
                    # Сначала завершаем все подзадачи
                    for subtask in self.subtasks.all():
                        if subtask.status != 'completed':
                            subtask.status = 'completed'
                            subtask.save()
                    
                    # Повторная проверка на завершение всех подзадач
                    if self.subtasks.filter(status__in=['in_progress', 'assigned', 'paused']).exists():
                        raise ValidationError("Есть незавершенные подзадачи.")
                    
                    # Устанавливаем дату завершения
                    if not self.completed_at:
                        self.completed_at = timezone.now()
                        
            # Сначала сохраняем основную задачу
            super().save(*args, **kwargs)


    def can_transition_to(self, new_status: str, old_status: str) -> bool:
        """
        Проверяет, возможен ли переход задачи в новый статус.

        Args:
            new_status (str): Новый статус задачи.
            old_status (str): Старый статус задачи.

        Returns:
            bool: True, если переход возможен, иначе False.
        """
        if new_status == "completed":
            if old_status in ["paused", "assigned"]:
                return False  # Нельзя завершить задачу из статусов "Приостановлена" или "Назначена"
            return old_status == "in_progress"
        elif new_status == "paused":
            return old_status == "in_progress"
        elif new_status == "deleted":
            return self.is_terminal()
        return True  # Допустимые переходы для других статусов

    def is_terminal(self) -> bool:
        """
        Проверяет, является ли задача терминальной (т.е. не имеет подзадач).

        Returns:
            bool: True, если задача терминальная, иначе False.
        """
        return not self.subtasks.exists()
