from rest_framework.permissions import BasePermission


class NotificationsPermission(BasePermission):
    """Placeholder permission for Notifications app."""

    def has_permission(self, request, view):
        return True
