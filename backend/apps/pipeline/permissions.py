from rest_framework.permissions import BasePermission


class PipelinePermission(BasePermission):
    """Placeholder permission for Pipeline app."""

    def has_permission(self, request, view):
        return True
