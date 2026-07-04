from rest_framework.permissions import BasePermission


class AutomationPermission(BasePermission):
    """Placeholder permission for Automation app."""

    def has_permission(self, request, view):
        return True
