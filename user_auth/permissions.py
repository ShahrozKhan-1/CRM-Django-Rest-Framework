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
    

class AttachmentObjectPermission(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.roles == 'Admin':
            return True

        parent = obj.content_object  # Customer / Lead / Deal

        if user.roles == 'Sales':
            return hasattr(parent, "assigned_to") and parent.assigned_to == user

        if user.roles == 'Manager':
            return (
                hasattr(parent, "assigned_to") and
                parent.assigned_to and
                parent.assigned_to.manager == user
            )

        return False
