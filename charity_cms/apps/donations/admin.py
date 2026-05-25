"""
CharityOS — Donations Admin Registration
"""
from django.contrib import admin
from .models import Donation, DonationReceipt, DonationAllocation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donation_ref', 'donor', 'donation_type', 'amount', 'donation_date', 'status')
    list_filter = ('donation_type', 'status', 'donation_date')
    search_fields = ('donation_ref', 'donor__user__first_name', 'transaction_reference')
    readonly_fields = ('donation_ref', 'created_at', 'updated_at')
    raw_id_fields = ('donor', 'recorded_by')


@admin.register(DonationReceipt)
class DonationReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'donation', 'email_status', 'emailed_at')
    list_filter = ('email_status',)
    search_fields = ('receipt_number', 'donation__donation_ref')
    readonly_fields = ('receipt_number', 'created_at')
    raw_id_fields = ('donation',)


@admin.register(DonationAllocation)
class DonationAllocationAdmin(admin.ModelAdmin):
    list_display = ('donation', 'amount', 'allocation_type', 'beneficiary', 'allocated_at')
    list_filter = ('allocation_type', 'allocated_at')
    search_fields = ('donation__donation_ref', 'beneficiary__first_name')
    raw_id_fields = ('donation', 'beneficiary', 'assistance_request', 'allocated_by')
