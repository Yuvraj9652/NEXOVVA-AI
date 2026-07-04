from rest_framework.permissions import BasePermission


class TasksPermission(BasePermission):
    """Placeholder permission for Tasks app."""

    def has_permission(self, request, view):
        return True
