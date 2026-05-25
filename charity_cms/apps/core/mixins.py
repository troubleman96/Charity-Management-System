"""
CharityOS — RBAC Mixins
========================
Role-Based Access Control mixins for class-based views.
These enforce that only users with the correct role can access a view.

Usage in views:
    class MyView(AdminRequiredMixin, TemplateView):
        template_name = 'my_template.html'

Role hierarchy:
    - AdminRequiredMixin:  Only 'admin' role
    - StaffRequiredMixin:  'admin' or 'staff' roles
    - DonorRequiredMixin:  Only 'donor' role
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Base mixin that restricts view access to specific user roles.
    Subclasses must define `allowed_roles` as a list of role strings.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        # First check if user is authenticated (handled by LoginRequiredMixin)
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Check if user has a profile with an allowed role
        user_profile = getattr(request.user, 'profile', None)
        if user_profile and user_profile.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        # Superusers always have access
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied('You do not have permission to access this page.')


class AdminRequiredMixin(RoleRequiredMixin):
    """Only users with 'admin' role can access."""
    allowed_roles = ['admin']


class StaffRequiredMixin(RoleRequiredMixin):
    """Users with 'admin' or 'staff' role can access."""
    allowed_roles = ['admin', 'staff']


class DonorRequiredMixin(RoleRequiredMixin):
    """Only users with 'donor' role can access."""
    allowed_roles = ['donor']
