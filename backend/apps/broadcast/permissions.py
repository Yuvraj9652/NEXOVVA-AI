from rest_framework.permissions import BasePermission


class IsOrganizationMember(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "organization", None) == request.organization


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(request.user, "role", None)
        return role in ["ADMIN", "MANAGER", "SUPERADMIN"]
