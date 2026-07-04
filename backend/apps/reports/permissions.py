from rest_framework.permissions import BasePermission


class ReportsPermission(BasePermission):
    """Placeholder permission for Reports app."""

    def has_permission(self, request, view):
        return True
