from rest_framework.permissions import BasePermission
from .models import Role


class IsRequester(BasePermission):
    """Allow access to users with Requester role or higher."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            Role.REQUESTER, Role.APPROVER, Role.ADMIN
        ]


class IsApprover(BasePermission):
    """Allow access to Sports Directors and Admins only."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            Role.APPROVER, Role.ADMIN
        ]


class IsAdmin(BasePermission):
    """Allow access to Administrators only."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.ADMIN
