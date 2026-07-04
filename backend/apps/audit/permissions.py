from rest_framework.permissions import BasePermission


class AuditPermission(BasePermission):
    """Placeholder permission for Audit app."""

    def has_permission(self, request, view):
        return True
