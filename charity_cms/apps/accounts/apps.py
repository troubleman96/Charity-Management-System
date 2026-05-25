"""
CharityOS — Accounts App Configuration
Handles authentication, user profiles, and role-based access control.
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Accounts & Authentication'

    def ready(self):
        """Import signals when the app is ready."""
        import apps.accounts.signals  # noqa: F401
