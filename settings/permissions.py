from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import RoleType


class HasAnyRole(BasePermission):
    """Allow authenticated users only when they have an application role."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role.filter(name__in=RoleType.values).exists()
        )


class IsAdminRole(BasePermission):
    """Restrict management endpoints to users with the admin role."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role.filter(name=RoleType.ADMIN).exists()
        )


class IsAdminRoleOrReadOnly(BasePermission):
    """Keep reads public; require the admin role for writes."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsAdminRole().has_permission(request, view)
