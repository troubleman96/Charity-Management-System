"""
CharityOS — Communications App Configuration
Manages internal messaging, system notifications, and email logs.
"""
from django.apps import AppConfig


class CommunicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.communications'
    verbose_name = 'Comms & Notifications'
