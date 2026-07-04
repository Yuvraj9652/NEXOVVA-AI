from rest_framework.permissions import BasePermission


class LeadsPermission(BasePermission):
    """Placeholder permission for Leads app."""

    def has_permission(self, request, view):
        return True
