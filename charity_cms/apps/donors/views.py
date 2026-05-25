"""
CharityOS — Donors Views
============================
Donor portal views: dashboard, donation history, and sponsored beneficiaries.
All views require 'donor' role access.
"""
from django.views.generic import TemplateView, ListView
from apps.core.mixins import DonorRequiredMixin


class DonorDashboardView(DonorRequiredMixin, TemplateView):
    """
    Donor dashboard showing:
    - Total donation summary
    - Sponsored beneficiaries with progress updates
    - Recent donation history
    """
    template_name = 'donor_portal/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # Get the donor profile
        donor = getattr(user, 'donor_profile', None)

        if donor:
            from apps.beneficiaries.models import DonorBeneficiaryLink, BeneficiaryUpdate

            # Donation stats
            ctx['total_donated'] = donor.total_donated
            ctx['donation_count'] = donor.donation_count

            # Recent donations
            ctx['recent_donations'] = donor.donations.order_by('-created_at')[:5]

            # Sponsored beneficiaries
            ctx['sponsored_links'] = (
                DonorBeneficiaryLink.objects
                .filter(donor=donor, is_active=True)
                .select_related('beneficiary')
            )

            # Recent updates for sponsored beneficiaries
            sponsored_ids = ctx['sponsored_links'].values_list('beneficiary_id', flat=True)
            ctx['recent_updates'] = (
                BeneficiaryUpdate.objects
                .filter(beneficiary_id__in=sponsored_ids)
                .select_related('beneficiary')
                .order_by('-created_at')[:5]
            )

        return ctx


class DonationHistoryView(DonorRequiredMixin, ListView):
    """
    Full paginated donation history for the logged-in donor.
    """
    template_name = 'donor_portal/donation_history.html'
    context_object_name = 'donations'
    paginate_by = 20

    def get_queryset(self):
        donor = getattr(self.request.user, 'donor_profile', None)
        if donor:
            return donor.donations.order_by('-donation_date')
        return []
