from rest_framework.permissions import BasePermission


class DocumentsPermission(BasePermission):
    """Placeholder permission for Documents app."""

    def has_permission(self, request, view):
        return True
