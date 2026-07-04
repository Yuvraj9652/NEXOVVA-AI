from rest_framework.permissions import BasePermission


class AccountsPermission(BasePermission):
    """Placeholder permission for Accounts app."""

    def has_permission(self, request, view):
        return True
