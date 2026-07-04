from rest_framework.permissions import BasePermission


class SettingsAppPermission(BasePermission):
    """Placeholder permission for Settings App app."""

    def has_permission(self, request, view):
        return True
