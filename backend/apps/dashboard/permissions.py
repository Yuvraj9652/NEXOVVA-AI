from rest_framework.permissions import BasePermission


class DashboardPermission(BasePermission):
    """Placeholder permission for Dashboard app."""

    def has_permission(self, request, view):
        return True
