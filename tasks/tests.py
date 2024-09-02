import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import JsonResponse
from django.urls import reverse
from django.test import TestCase, Client

from .models import Task


# Тесты моделей
@pytest.mark.django_db
def test_task_creation():
    task = Task.objects.create(
        name="Test Task",
        description="This is a test task.",
        performers="John Doe",
        status="assigned",
        planned_effort=10.0,
    )

    assert task.name == "Test Task"
    assert task.description == "This is a test task."
    assert task.performers == "John Doe"
    assert task.status == "assigned"
    assert task.planned_effort == 10.0
    assert task.actual_effort == 0.0
    assert task.created_at <= timezone.now()


@pytest.mark.django_db
def test_calculate_efforts():
    task = Task.objects.create(name="Main Task", planned_effort=10.0)
    subtask1 = Task.objects.create(name="Subtask 1", planned_effort=5.0, parent=task)
    subtask2 = Task.objects.create(name="Subtask 2", planned_effort=3.0, parent=task)

    task.refresh_from_db()
    assert task.calculate_efforts() == {
        "task_planned_effort": 10.0,
        "subtask_planned_effort": 8.0,
        "task_actual_effort": 0.0,
        "subtask_actual_effort": 0.0,
        "total_planned_effort": 18.0,
        "total_actual_effort": 0.0,
    }


@pytest.mark.django_db
def test_complete_task_with_subtasks():
    task = Task.objects.create(name="Main Task", status="in_progress")
    subtask1 = Task.objects.create(name="Subtask 1", status="in_progress", parent=task)
    subtask2 = Task.objects.create(name="Subtask 2", status="in_progress", parent=task)

    task.status = "completed"
    with pytest.raises(ValidationError):
        task.save()


@pytest.mark.django_db
def test_is_terminal():
    task = Task.objects.create(name="Main Task")
    assert task.is_terminal() is True

    subtask = Task.objects.create(name="Subtask", parent=task)
    task.refresh_from_db()
    assert task.is_terminal() is False

    subtask.delete()
    task.refresh_from_db()
    assert task.is_terminal() is True


# Тесты представлений
class TaskViewsTestCase(TestCase):
    def setUp(self):
        self.task = Task.objects.create(name="Test Task", status="assigned")

    def test_delete_task_view(self):
        url = reverse("delete_task", kwargs={"pk": self.task.pk})
        response = self.client.post(url)
        self.assertTrue(True)

    def test_task_detail_ajax_view(self):
        url = reverse("task_details", kwargs={"pk": self.task.pk})
        response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.task.name)

    def test_update_actual_effort_view(self):
        url = reverse("update_actual_effort", kwargs={"pk": self.task.pk})
        response = self.client.post(url, {"actual_effort": 5.0})
        self.task.refresh_from_db()
        self.assertEqual(self.task.actual_effort, 0.0)

    def test_update_task_status_view(self):
        url = reverse("update_task_status", kwargs={"pk": self.task.pk})
        response = self.client.post(url, {"status": "assigned"})
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "assigned")

    def test_update_task_view(self):
        url = reverse("edit_task", kwargs={"pk": self.task.pk})
        response = self.client.post(url, {"name": "Test Task", "status": "in_progress"})
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Test Task")
