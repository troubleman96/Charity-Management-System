"""
CharityOS — Beneficiaries Admin Registration
"""
from django.contrib import admin
from .models import Beneficiary, DonorBeneficiaryLink, AssistanceRequest, BeneficiaryUpdate


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ('beneficiary_code', 'first_name', 'last_name', 'status', 'location_region', 'date_enrolled')
    list_filter = ('status', 'gender', 'location_region', 'date_enrolled')
    search_fields = ('beneficiary_code', 'first_name', 'last_name', 'school_name')
    readonly_fields = ('beneficiary_code', 'created_at', 'updated_at')


@admin.register(DonorBeneficiaryLink)
class DonorBeneficiaryLinkAdmin(admin.ModelAdmin):
    list_display = ('donor', 'beneficiary', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('donor__user__first_name', 'beneficiary__first_name')
    raw_id_fields = ('donor', 'beneficiary')


@admin.register(AssistanceRequest)
class AssistanceRequestAdmin(admin.ModelAdmin):
    list_display = ('request_ref', 'beneficiary', 'request_type', 'status', 'estimated_cost', 'created_at')
    list_filter = ('status', 'request_type', 'created_at')
    search_fields = ('request_ref', 'beneficiary__first_name', 'beneficiary__last_name')
    readonly_fields = ('request_ref', 'created_at', 'updated_at')
    raw_id_fields = ('beneficiary', 'requested_by', 'reviewed_by')


@admin.register(BeneficiaryUpdate)
class BeneficiaryUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'beneficiary', 'created_by', 'notified_donors', 'created_at')
    list_filter = ('notified_donors', 'created_at')
    search_fields = ('title', 'beneficiary__first_name')
    raw_id_fields = ('beneficiary', 'created_by')
