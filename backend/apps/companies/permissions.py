from rest_framework.permissions import BasePermission


class CompaniesPermission(BasePermission):
    """Placeholder permission for Companies app."""

    def has_permission(self, request, view):
        return True
