"""
CharityOS — Decorators
========================
Function-based view decorators for role-based access control.

Usage:
    @login_required
    @role_required('admin', 'staff')
    def my_view(request):
        ...
"""
from functools import wraps
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """
    Decorator that restricts a function-based view to specific roles.

    Args:
        *roles: One or more role strings (e.g., 'admin', 'staff', 'donor')

    Example:
        @login_required
        @role_required('admin')
        def admin_only_view(request):
            return render(request, 'admin_page.html')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Superusers bypass role checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check user's profile role
            profile = getattr(request.user, 'profile', None)
            if profile and profile.role in roles:
                return view_func(request, *args, **kwargs)

            raise PermissionDenied('You do not have permission to access this page.')
        return wrapper
    return decorator
