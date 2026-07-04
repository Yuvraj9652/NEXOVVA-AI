from rest_framework.permissions import BasePermission


class CalendarPermission(BasePermission):
    """Placeholder permission for Calendar app."""

    def has_permission(self, request, view):
        return True
