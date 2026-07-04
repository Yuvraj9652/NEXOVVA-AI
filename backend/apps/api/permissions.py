from rest_framework.permissions import BasePermission


class ApiPermission(BasePermission):
    """Placeholder permission for Api app."""

    def has_permission(self, request, view):
        return True
