from rest_framework.permissions import BasePermission


class BillingPermission(BasePermission):
    """Placeholder permission for Billing app."""

    def has_permission(self, request, view):
        return True
