from rest_framework.permissions import BasePermission


class IntegrationsPermission(BasePermission):
    """Placeholder permission for Integrations app."""

    def has_permission(self, request, view):
        return True
