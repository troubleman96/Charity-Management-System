"""
CharityOS — Donors Admin Registration
"""
from django.contrib import admin
from .models import Donor


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'is_anonymous', 'total_donated', 'created_at')
    list_filter = ('is_anonymous', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'organization')
    raw_id_fields = ('user',)
