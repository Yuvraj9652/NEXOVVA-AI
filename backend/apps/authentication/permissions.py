from rest_framework.permissions import BasePermission
from apps.accounts.models import UserProfile


class IsOrganizationMember(BasePermission):
    """Enforces that the user belongs to the active organization tenant."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.organization is not None
        )

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "organization"):
            return True
        return obj.organization == request.organization


class IsAdminUserRole(BasePermission):
    """Allows access only to Admin users of the organization."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.userprofile
            and request.user.userprofile.role == UserProfile.Roles.ADMIN
        )


class IsManagerUserRole(BasePermission):
    """Allows access only to Managers and Admins of the organization."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.userprofile
            and request.user.userprofile.role in [UserProfile.Roles.ADMIN, UserProfile.Roles.MANAGER]
        )
