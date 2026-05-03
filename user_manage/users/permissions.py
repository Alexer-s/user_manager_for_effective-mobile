from rest_framework.permissions import BasePermission

from .models import AccessRoleRule


class BusinessElementPermission(BasePermission):
    """
    Кастомное разрешение для проверки доступа к бизнес-элементам на основе ролей и правил доступа.
    Во вьюхе ддолжен быть аттрибут business_element_name.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        element_name = getattr(view, "business_element_name", None)
        if not element_name:
            return True

        role = request.user.role
        if not role:
            return False

        try:
            rule = AccessRoleRule.objects.get(role=role, element__name=element_name)
        except AccessRoleRule.DoesNotExist:
            return False

        method = request.method.upper()

        if method == "GET":
            return rule.can_read_own or rule.can_read_all
        elif method == "POST":
            return rule.can_create
        elif method in ["PUT", "PATCH"]:
            return rule.can_update_own or rule.can_update_all
        elif method == "DELETE":
            return rule.can_delete_own or rule.can_delete_all
        return False

    def has_object_permission(self, request, view, obj):
        """Проверка прав доступа на уровне объекта."""

        element_name = getattr(view, "business_element_name", None)
        if not element_name:
            return True

        role = request.user.role
        if not role:
            return False

        try:
            rule = AccessRoleRule.objects.get(role=role, element__name=element_name)
        except AccessRoleRule.DoesNotExist:
            return False

        method = request.method.upper()

        if method == "GET" and rule.can_read_all:
            return True
        if method in ["PUT", "PATCH"] and rule.can_update_all:
            return True
        if method == "DELETE" and rule.can_delete_all:
            return True

        owner_id = getattr(obj, "owner_id", None)
        if owner_id is None:
            return False

        is_owner = owner_id == request.user.id

        if method == "GET" and rule.can_read_own and is_owner:
            return True
        if method in ["PUT", "PATCH"] and rule.can_update_own and is_owner:
            return True
        if method == "DELETE" and rule.can_delete_own and is_owner:
            return True

        return False


class IsAdminUser(BasePermission):
    """
    Разрешение для доступа только администраторам.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role
            and request.user.role.name == "admin"
        )
