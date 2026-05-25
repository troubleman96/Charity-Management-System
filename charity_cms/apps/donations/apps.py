"""
CharityOS — Donations App Configuration
Manages cash and in-kind donations, digital receipts, and fund allocation.
"""
from django.apps import AppConfig


class DonationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.donations'
    verbose_name = 'Donation Management'
