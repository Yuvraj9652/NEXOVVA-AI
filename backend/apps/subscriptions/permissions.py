from rest_framework.permissions import BasePermission


class SubscriptionsPermission(BasePermission):
    """Placeholder permission for Subscriptions app."""

    def has_permission(self, request, view):
        return True
