from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles == 'Admin'


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles == 'Manager'


class IsSales(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles == 'Sales'


class IsSupport(BasePermission):
    def has_permission(self, request, view):
        return request.user.roles == 'Support'