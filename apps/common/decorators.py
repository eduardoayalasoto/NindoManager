from functools import wraps
from django.core.exceptions import PermissionDenied
from .permissions import user_has_role


def role_required(*roles):
    """Decorator to restrict views by role."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect("users:login")
            if not user_has_role(request.user, *roles):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
