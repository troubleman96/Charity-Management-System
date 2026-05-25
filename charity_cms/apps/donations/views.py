"""
CharityOS — Donations Views
==============================
CRUD views for recording donations, viewing lists, and allocating funds.
"""
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from apps.core.mixins import StaffRequiredMixin, AdminRequiredMixin
from apps.core.utils import log_action
from .models import Donation, DonationReceipt, DonationAllocation
from .forms import DonationForm, AllocationForm
from .tasks import send_donation_receipt
from apps.communications.models import Notification
from django.contrib.auth.models import User


class DonationListView(StaffRequiredMixin, ListView):
    """
    Paginated list of all donations with filters.
    """
    model = Donation
    template_name = 'donations/list.html'
    context_object_name = 'donations'
    paginate_by = 20

    def get_queryset(self):
        qs = Donation.objects.select_related('donor__user')

        # Type filter
        dtype = self.request.GET.get('type', '')
        if dtype:
            qs = qs.filter(donation_type=dtype)

        # Status filter
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_type'] = self.request.GET.get('type', '')
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['type_choices'] = Donation.DONATION_TYPES
        ctx['status_choices'] = Donation.STATUS_CHOICES
        return ctx


class DonationDetailView(StaffRequiredMixin, DetailView):
    """
    Detailed view of a single donation.
    Shows receipt status and allocations.
    """
    model = Donation
    template_name = 'donations/detail.html'
    context_object_name = 'donation'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['allocations'] = self.object.allocations.select_related('beneficiary', 'assistance_request', 'allocated_by')
        # Add the allocation form if it's a cash donation and user is admin
        if self.object.donation_type == 'cash' and self.object.remaining_amount > 0:
            profile = getattr(self.request.user, 'profile', None)
            if (profile and profile.role == 'admin') or self.request.user.is_superuser:
                ctx['allocation_form'] = AllocationForm(donation=self.object)
        return ctx


class DonationCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Form view for staff to record a new donation.
    On success: creates a receipt, fires Celery email task, and notifies admins.
    """
    model = Donation
    form_class = DonationForm
    template_name = 'donations/form.html'
    success_url = reverse_lazy('donations:list')
    success_message = 'Donation recorded successfully!'

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        response = super().form_valid(form)
        donation = self.object

        # 1. Create Receipt Record
        year = donation.donation_date.year
        count = DonationReceipt.objects.count()
        receipt = DonationReceipt.objects.create(
            donation=donation,
            receipt_number=f'REC-{year}-{str(count + 1).zfill(5)}'
        )

        # 2. Queue async PDF/Email task
        send_donation_receipt.delay(donation.id)

        # 3. Log action
        log_action(
            self.request.user, 'donation.recorded', donation,
            f'Recorded {donation.get_donation_type_display()} donation: {donation.donation_ref}',
            self.request
        )

        # 4. Notify admins in-app
        admins = User.objects.filter(profile__role='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                notification_type='donation_received',
                title='New Donation Received',
                message=f'A new {donation.get_donation_type_display()} donation ({donation.donation_ref}) has been recorded.',
                link=f'/donations/{donation.pk}/'
            )

        return response


class AllocationCreateView(AdminRequiredMixin, CreateView):
    """
    Form view for admins to allocate funds from a specific donation.
    """
    model = DonationAllocation
    form_class = AllocationForm
    template_name = 'donations/allocate_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.donation = get_object_or_404(Donation, pk=self.kwargs['pk'])
        kwargs['donation'] = self.donation
        return kwargs

    def form_valid(self, form):
        form.instance.donation = self.donation
        form.instance.allocated_by = self.request.user
        response = super().form_valid(form)

        log_action(
            self.request.user, 'allocation.created', self.object,
            f'Allocated TZS {self.object.amount} from {self.donation.donation_ref}',
            self.request
        )
        messages.success(self.request, f'Successfully allocated TZS {self.object.amount:,.0f}')
        return redirect('donations:detail', pk=self.donation.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return redirect('donations:detail', pk=self.donation.pk)
