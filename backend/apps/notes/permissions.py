from rest_framework.permissions import BasePermission


class NotesPermission(BasePermission):
    """Placeholder permission for Notes app."""

    def has_permission(self, request, view):
        return True
