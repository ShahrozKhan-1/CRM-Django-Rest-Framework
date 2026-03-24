from rest_framework.permissions import BasePermission
from .models import Role, Permission


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



class HasPermissions(BasePermission):

    ACTION_MAP = {
        "list": "read",
        "retrieve": "read",
        "create": "create",
        "update": "update",
        "partial_update": "update",
        "destroy": "delete",
        "get": "read",
        "head": "read",
        "options": "read",
        "post": "create",
        "put": "update",
        "patch": "update",
        "delete": "delete",
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        view_action = getattr(view, "action", None)
        if view_action is None:
            view_action = request.method.lower()

        view_action = str(view_action).strip().lower()
        action = self.ACTION_MAP.get(view_action)
        http_method = request.method.lower()
        permission_name = getattr(view, "permission_name", None)

        if not permission_name:
            return True
        
        if not action:
            return False

        role = Role.objects.filter(name__iexact=str(user.roles).strip()).first()
        if not role:
            return False

        permission = Permission.objects.filter(
            role=role,
            name__iexact=str(permission_name).strip(),
        ).first()

        if not permission:
            return False

        allowed_actions = {
            str(item).strip().lower()
            for item in (permission.actions or [])
            if item is not None
        }
        return action in allowed_actions or http_method in allowed_actions
