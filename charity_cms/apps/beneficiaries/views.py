"""
CharityOS — Beneficiaries Views
==================================
CRUD views for beneficiary management, assistance requests, and progress updates.
Staff/Admin access required for most views.
"""
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from apps.core.mixins import StaffRequiredMixin, AdminRequiredMixin
from apps.core.utils import log_action
from .models import Beneficiary, AssistanceRequest, BeneficiaryUpdate
from .forms import BeneficiaryForm, AssistanceRequestForm, AssistanceReviewForm, BeneficiaryUpdateForm


class BeneficiaryListView(StaffRequiredMixin, ListView):
    """
    Paginated list of all beneficiaries with search and filter support.
    Staff and admin can view; supports filtering by status, region.
    """
    model = Beneficiary
    template_name = 'beneficiaries/list.html'
    context_object_name = 'beneficiaries'
    paginate_by = 20

    def get_queryset(self):
        qs = Beneficiary.objects.all()

        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(beneficiary_code__icontains=search)
            )

        # Status filter
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        # Region filter
        region = self.request.GET.get('region', '')
        if region:
            qs = qs.filter(location_region__icontains=region)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search'] = self.request.GET.get('search', '')
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_region'] = self.request.GET.get('region', '')
        ctx['status_choices'] = Beneficiary.STATUS_CHOICES
        return ctx


class BeneficiaryDetailView(StaffRequiredMixin, DetailView):
    """
    Detailed view of a single beneficiary's profile.
    Shows full profile, assistance history, donor links, and updates.
    """
    model = Beneficiary
    template_name = 'beneficiaries/detail.html'
    context_object_name = 'beneficiary'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        beneficiary = self.object
        ctx['assistance_requests'] = beneficiary.assistance_requests.order_by('-created_at')[:10]
        ctx['donor_links'] = beneficiary.donor_links.filter(is_active=True).select_related('donor__user')
        ctx['updates'] = beneficiary.updates.order_by('-created_at')[:5]
        return ctx


class BeneficiaryCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Form view to register a new beneficiary.
    Sets registered_by to the current user automatically.
    """
    model = Beneficiary
    form_class = BeneficiaryForm
    template_name = 'beneficiaries/form.html'
    success_url = reverse_lazy('beneficiaries:list')
    success_message = 'Beneficiary "%(first_name)s %(last_name)s" registered successfully!'

    def form_valid(self, form):
        form.instance.registered_by = self.request.user
        response = super().form_valid(form)
        log_action(
            self.request.user, 'beneficiary.created', self.object,
            f'Registered beneficiary {self.object.get_full_name()}',
            self.request
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Register New Beneficiary'
        ctx['submit_text'] = 'Register Beneficiary'
        return ctx


class BeneficiaryUpdateView(StaffRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Form view to edit an existing beneficiary's profile.
    """
    model = Beneficiary
    form_class = BeneficiaryForm
    template_name = 'beneficiaries/form.html'
    success_url = reverse_lazy('beneficiaries:list')
    success_message = 'Beneficiary profile updated successfully!'

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(
            self.request.user, 'beneficiary.updated', self.object,
            f'Updated beneficiary {self.object.get_full_name()}',
            self.request
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Edit: {self.object.get_full_name()}'
        ctx['submit_text'] = 'Save Changes'
        return ctx


class AssistanceRequestListView(StaffRequiredMixin, ListView):
    """
    List of all assistance requests with status filtering.
    """
    model = AssistanceRequest
    template_name = 'beneficiaries/requests.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        qs = AssistanceRequest.objects.select_related('beneficiary', 'requested_by')
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['status_choices'] = AssistanceRequest.STATUS_CHOICES
        return ctx


class AssistanceRequestCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Staff form to submit a new assistance request.
    """
    model = AssistanceRequest
    form_class = AssistanceRequestForm
    template_name = 'beneficiaries/request_form.html'
    success_url = reverse_lazy('beneficiaries:requests')
    success_message = 'Assistance request submitted successfully!'

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        response = super().form_valid(form)
        log_action(
            self.request.user, 'request.created', self.object,
            f'Submitted assistance request {self.object.request_ref}',
            self.request
        )
        # Notify admins of new pending request
        from apps.communications.models import Notification
        from django.contrib.auth.models import User
        admins = User.objects.filter(profile__role='admin')
        for admin_user in admins:
            Notification.objects.create(
                user=admin_user,
                notification_type='system',
                title='New Assistance Request',
                message=f'{self.object.request_ref}: {self.object.beneficiary.get_full_name()} needs {self.object.get_request_type_display()}',
                link=f'/beneficiaries/requests/'
            )
        return response


@login_required
def review_request(request, pk):
    """
    Admin view to approve or reject an assistance request.
    """
    assistance_request = get_object_or_404(AssistanceRequest, pk=pk)

    # Check admin permission
    profile = getattr(request.user, 'profile', None)
    if not (profile and profile.role == 'admin') and not request.user.is_superuser:
        messages.error(request, 'Only administrators can review requests.')
        return redirect('beneficiaries:requests')

    if request.method == 'POST':
        form = AssistanceReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            assistance_request.reviewed_by = request.user
            assistance_request.review_notes = form.cleaned_data.get('review_notes', '')

            if action == 'approve':
                assistance_request.status = 'approved'
                messages.success(request, f'Request {assistance_request.request_ref} approved.')
                log_action(request.user, 'request.approved', assistance_request,
                           f'Approved request {assistance_request.request_ref}', request)
            else:
                assistance_request.status = 'rejected'
                messages.warning(request, f'Request {assistance_request.request_ref} rejected.')
                log_action(request.user, 'request.rejected', assistance_request,
                           f'Rejected request {assistance_request.request_ref}', request)

            assistance_request.save()

            # Notify the requesting staff member
            from apps.communications.models import Notification
            if assistance_request.requested_by:
                Notification.objects.create(
                    user=assistance_request.requested_by,
                    notification_type=f'request_{action}d',
                    title=f'Request {assistance_request.request_ref} {action}d',
                    message=f'Your request for {assistance_request.beneficiary.get_full_name()} has been {action}d.',
                    link=f'/beneficiaries/requests/'
                )

    return redirect('beneficiaries:requests')


class BeneficiaryProgressCreateView(StaffRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Staff form to create a progress update for a beneficiary.
    """
    model = BeneficiaryUpdate
    form_class = BeneficiaryUpdateForm
    template_name = 'beneficiaries/update_form.html'
    success_url = reverse_lazy('beneficiaries:list')
    success_message = 'Beneficiary update created successfully!'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_action(
            self.request.user, 'beneficiary_update.created', self.object,
            f'Created update: {self.object.title}',
            self.request
        )
        return response


# Need to import models for Q lookups in ListView
from django.db import models
