from rest_framework.permissions import BasePermission


class CommonPermission(BasePermission):
    """Placeholder permission for Common app."""

    def has_permission(self, request, view):
        return True
