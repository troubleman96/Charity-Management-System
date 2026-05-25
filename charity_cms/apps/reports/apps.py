"""
CharityOS — Reports App Configuration
Provides PDF generation and data export views for admins.
"""
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reports'
    verbose_name = 'Reporting & Analytics'
