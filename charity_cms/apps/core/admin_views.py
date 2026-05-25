"""
CharityOS — Admin Dashboard Views
====================================
Views for the administrative dashboard with KPI cards, charts, and activity feeds.
These views aggregate data from all modules to give admins a full system overview.
"""
import json
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .mixins import AdminRequiredMixin


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """
    Main admin dashboard view.
    Displays:
        - KPI cards (total donations, available funds, beneficiary count, donor count)
        - Monthly donation trend chart (Chart.js data)
        - Donation type breakdown (cash vs in-kind)
        - Recent donations table
        - Pending assistance requests
    """
    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Lazy imports to avoid circular dependencies
        from apps.donations.models import Donation, DonationAllocation
        from apps.beneficiaries.models import Beneficiary, AssistanceRequest
        from apps.donors.models import Donor

        # --- KPI Card Data ---
        total_cash = Donation.objects.filter(
            donation_type='cash'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_allocated = DonationAllocation.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0

        ctx.update({
            # KPI values
            'total_donations': total_cash,
            'available_funds': total_cash - total_allocated,
            'active_beneficiaries': Beneficiary.objects.filter(status='active').count(),
            'total_donors': Donor.objects.count(),
            'pending_requests_count': AssistanceRequest.objects.filter(status='pending').count(),

            # Recent activity tables
            'recent_donations': (
                Donation.objects
                .select_related('donor__user')
                .order_by('-created_at')[:5]
            ),
            'pending_requests': (
                AssistanceRequest.objects
                .filter(status='pending')
                .select_related('beneficiary', 'requested_by')
                .order_by('-created_at')[:5]
            ),

            # Chart.js data (serialized as JSON for JavaScript)
            'monthly_chart_data': json.dumps(self._get_monthly_donations()),
            'donation_type_data': json.dumps(self._get_donation_type_split()),
            'allocation_by_category': json.dumps(self._get_allocation_by_category()),
        })
        return ctx

    def _get_monthly_donations(self):
        """
        Aggregate cash donations by month for the line chart.
        Returns dict with 'labels' (month names) and 'values' (totals).
        """
        from apps.donations.models import Donation

        data = (
            Donation.objects
            .filter(donation_type='cash')
            .annotate(month=TruncMonth('donation_date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )
        return {
            'labels': [d['month'].strftime('%b %Y') for d in data],
            'values': [float(d['total'] or 0) for d in data],
        }

    def _get_donation_type_split(self):
        """
        Calculate total cash vs in-kind donation values for the pie chart.
        """
        from apps.donations.models import Donation

        cash = Donation.objects.filter(
            donation_type='cash'
        ).aggregate(total=Sum('amount'))['total'] or 0

        inkind = Donation.objects.filter(
            donation_type='in_kind'
        ).aggregate(total=Sum('in_kind_estimated_value'))['total'] or 0

        return {
            'cash': float(cash),
            'inkind': float(inkind),
        }

    def _get_allocation_by_category(self):
        """
        Aggregate fund allocations by category (education, food, medical, etc.)
        for the horizontal bar chart.
        """
        from apps.donations.models import DonationAllocation

        data = (
            DonationAllocation.objects
            .values('allocation_type')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        return {
            'labels': [d['allocation_type'].title() for d in data],
            'values': [float(d['total'] or 0) for d in data],
        }
