"""
CharityOS — Staff Dashboard Views
====================================
Views for the staff dashboard showing beneficiary management tasks.
"""
from django.views.generic import TemplateView
from django.db.models import Count
from .mixins import StaffRequiredMixin


class StaffDashboardView(StaffRequiredMixin, TemplateView):
    """
    Staff dashboard view.
    Shows beneficiary overview, recent assistance requests, and quick actions.
    """
    template_name = 'staff_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        from apps.beneficiaries.models import Beneficiary, AssistanceRequest
        from apps.donations.models import Donation

        ctx.update({
            'active_beneficiaries': Beneficiary.objects.filter(status='active').count(),
            'total_beneficiaries': Beneficiary.objects.count(),
            'pending_requests': (
                AssistanceRequest.objects
                .filter(status='pending')
                .select_related('beneficiary')
                .order_by('-created_at')[:5]
            ),
            'my_requests': (
                AssistanceRequest.objects
                .filter(requested_by=self.request.user)
                .select_related('beneficiary')
                .order_by('-created_at')[:5]
            ),
            'recent_donations': (
                Donation.objects
                .select_related('donor__user')
                .order_by('-created_at')[:5]
            ),
        })
        return ctx
