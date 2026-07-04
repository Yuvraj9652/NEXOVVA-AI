from rest_framework.permissions import BasePermission


class AiPermission(BasePermission):
    """Placeholder permission for Ai app."""

    def has_permission(self, request, view):
        return True
