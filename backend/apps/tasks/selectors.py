from django.db import models
from apps.tasks.models import Task


class TasksSelector:
    @staticmethod
    def list_tasks(organization, completed=None, assigned_to_id=None):
        queryset = Task.objects.filter(organization=organization).select_related(
            "assigned_to", "contact", "deal", "lead"
        )
        if completed is not None:
            queryset = queryset.filter(completed=completed)
        if assigned_to_id:
            queryset = queryset.filter(assigned_to_id=assigned_to_id)
        return queryset

    @staticmethod
    def get_task_by_id(organization, task_id):
        return Task.objects.select_related("assigned_to", "contact", "deal", "lead").get(
            organization=organization, id=task_id
        )
