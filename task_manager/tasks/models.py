from django.db import models
from django.forms import ValidationError
from django.utils import timezone


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
        )  # Вычисление суммарного планового время выполнения всех подзадач
        subtask_actual_effort = sum(
            subtask.actual_effort for subtask in self.subtasks.all()
        )  # Вычисление суммарного фактического времени выполнения всех подзадач
        return {
            "planned_effort": self.planned_effort + subtask_planned_effort,
            "actual_effort": self.actual_effort + subtask_actual_effort,
        }

    def save(self, *args, **kwargs):  # Сохрание/обновление статуса задачи 
        if self.status == "completed" and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != "completed":
            self.completed_at = None
        super().save(*args, **kwargs)
        for subtask in self.subtasks.all():
            if self.status == "completed":
                subtask.status = "completed"
                subtask.save()
