from rest_framework.permissions import BasePermission


class CommunicationsPermission(BasePermission):
    """Placeholder permission for Communications app."""

    def has_permission(self, request, view):
        return True
