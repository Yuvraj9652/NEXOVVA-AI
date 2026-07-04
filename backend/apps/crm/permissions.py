from rest_framework.permissions import BasePermission


class CrmPermission(BasePermission):
    """Placeholder permission for Crm app."""

    def has_permission(self, request, view):
        return True
