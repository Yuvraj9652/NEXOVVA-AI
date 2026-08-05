from rest_framework.permissions import BasePermission


class IsOrganizationMember(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.organization is not None

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "organization"):
            return True
        return obj.organization == request.organization


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.userprofile
            and request.user.userprofile.role in ["ADMIN", "MANAGER"]
        )
