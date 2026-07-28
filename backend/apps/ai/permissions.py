from rest_framework.permissions import BasePermission


class AiPermission(BasePermission):
    """Placeholder permission for Ai app."""

    def has_permission(self, request, view):
        return True


class IsSessionOwner(BasePermission):
    """Enforces that the user is the owner of the chat session."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

