from rest_framework.permissions import BasePermission


class AnalyticsPermission(BasePermission):
    """Placeholder permission for Analytics app."""

    def has_permission(self, request, view):
        return True
