from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .permissions import user_has_role, ADMIN_ROLES, MANAGER_ROLES


class RoleRequiredMixin(LoginRequiredMixin):
    """Mixin that checks if user has one of the required roles."""
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.required_roles and not user_has_role(request.user, *self.required_roles):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    required_roles = ADMIN_ROLES


class ManagerRequiredMixin(RoleRequiredMixin):
    required_roles = MANAGER_ROLES


class BranchFilterMixin:
    """Mixin that filters queryset by user's accessible branches."""

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user_has_role(user, "Gerente General"):
            return qs
        accessible_branches = user.user_roles.filter(
            is_active=True
        ).values_list("branch", flat=True)
        return qs.filter(branch__in=accessible_branches)
