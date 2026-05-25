"""
CharityOS — Core App Configuration
The core app provides shared utilities, audit logging, RBAC mixins,
template tags, context processors, and base views (landing, dashboard redirect).
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core & Audit'
