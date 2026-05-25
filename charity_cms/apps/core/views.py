"""
CharityOS — Core Views
========================
Landing page (public) and role-based dashboard redirect.
"""
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


class LandingPageView(TemplateView):
    """
    Public landing page visible to all visitors.
    Showcases the organization's mission, impact stats, and donor signup CTA.
    """
    template_name = 'landing/index.html'


@login_required
def dashboard_redirect(request):
    """
    Redirect authenticated users to their role-specific dashboard.
    - Admins   → /admin-panel/dashboard/
    - Staff    → /staff/dashboard/
    - Donors   → /donor/dashboard/
    """
    profile = getattr(request.user, 'profile', None)

    if profile:
        if profile.role == 'admin':
            return redirect('admin_panel:dashboard')
        elif profile.role == 'staff':
            return redirect('staff_panel:dashboard')
        elif profile.role == 'donor':
            return redirect('donors:dashboard')

    # Superusers without a profile go to admin panel
    if request.user.is_superuser:
        return redirect('admin_panel:dashboard')

    # Fallback — shouldn't happen with proper setup
    return redirect('landing')
