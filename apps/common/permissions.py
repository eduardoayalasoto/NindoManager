ROLE_SUPERADMIN = "Superadmin"
ROLE_GERENTE = "Gerente General"
ROLE_JEFA_OPS = "Jefa de Operaciones"
ROLE_ENTRENADOR = "Entrenador"

ADMIN_ROLES = [ROLE_SUPERADMIN, ROLE_GERENTE]
MANAGER_ROLES = [ROLE_SUPERADMIN, ROLE_GERENTE, ROLE_JEFA_OPS]
ALL_ROLES = [ROLE_SUPERADMIN, ROLE_GERENTE, ROLE_JEFA_OPS, ROLE_ENTRENADOR]


def get_user_roles(user):
    """Returns list of role names for a user."""
    return list(
        user.user_roles.filter(is_active=True).values_list("role__name", flat=True)
    )


def user_has_role(user, *roles):
    """Check if user has any of the given roles."""
    if user.is_superuser:
        return True
    user_roles = get_user_roles(user)
    return any(role in user_roles for role in roles)


def user_has_branch_access(user, branch):
    """Check if user has access to a specific branch."""
    if user.is_superuser or user_has_role(user, ROLE_GERENTE):
        return True
    return user.user_roles.filter(
        branch=branch, is_active=True
    ).exists()
