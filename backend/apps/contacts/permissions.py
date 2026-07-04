from rest_framework.permissions import BasePermission


class ContactsPermission(BasePermission):
    """Placeholder permission for Contacts app."""

    def has_permission(self, request, view):
        return True
