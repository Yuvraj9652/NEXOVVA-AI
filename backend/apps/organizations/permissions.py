from rest_framework.permissions import BasePermission


class OrganizationsPermission(BasePermission):
    """Placeholder permission for Organizations app."""

    def has_permission(self, request, view):
        return True
