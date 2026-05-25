"""
CharityOS — Reports Views
============================
Views to generate PDF reports for administrators.
"""
from django.views.generic import TemplateView
from django.db.models import Sum
from django.utils import timezone
from apps.core.mixins import AdminRequiredMixin
from apps.core.utils import log_action
from apps.donations.models import Donation, DonationAllocation
from apps.beneficiaries.models import Beneficiary
from apps.donors.models import Donor
from .utils import generate_pdf_response


class ReportIndexView(AdminRequiredMixin, TemplateView):
    """
    Landing page for reports, showing available downloads.
    """
    template_name = 'reports/report_list.html'


class MonthlySummaryReportView(AdminRequiredMixin, TemplateView):
    """
    Generate a PDF summary of operations for the current month.
    """
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Gather data
        donations = Donation.objects.filter(donation_date__gte=start_of_month)
        cash_total = donations.filter(donation_type='cash').aggregate(t=Sum('amount'))['t'] or 0
        allocations = DonationAllocation.objects.filter(allocated_at__gte=start_of_month)
        alloc_total = allocations.aggregate(t=Sum('amount'))['t'] or 0

        context = {
            'month_name': now.strftime('%B %Y'),
            'generated_at': now,
            'cash_total': cash_total,
            'alloc_total': alloc_total,
            'donation_count': donations.count(),
            'new_beneficiaries': Beneficiary.objects.filter(date_enrolled__gte=start_of_month).count(),
            'donations': donations.order_by('-donation_date')[:50]  # Show recent
        }

        log_action(request.user, 'report.generated', description='Generated Monthly Summary Report', request=request)
        return generate_pdf_response('reports/pdf/monthly_summary.html', context, f'monthly_summary_{now.strftime("%Y_%m")}.pdf')


class DonorReportView(AdminRequiredMixin, TemplateView):
    """
    Generate a PDF report of all donors and their total contributions.
    """
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        donors = Donor.objects.all().prefetch_related('donations')

        donor_data = []
        for donor in donors:
            donor_data.append({
                'name': donor.display_name,
                'email': donor.user.email,
                'total_donated': donor.total_donated,
                'count': donor.donation_count,
            })
        
        # Sort by total donated descending
        donor_data.sort(key=lambda x: x['total_donated'], reverse=True)

        context = {
            'generated_at': now,
            'donor_data': donor_data,
        }

        log_action(request.user, 'report.generated', description='Generated Donor Report', request=request)
        return generate_pdf_response('reports/pdf/donor_report.html', context, 'donor_report.pdf')
