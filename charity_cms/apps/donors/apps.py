"""
CharityOS — Donors App Configuration
Manages donor profiles, dashboards, and donation history views.
"""
from django.apps import AppConfig


class DonorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.donors'
    verbose_name = 'Donor Management'
