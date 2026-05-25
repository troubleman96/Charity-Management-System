"""
CharityOS — Core Admin Registration
=====================================
Register AuditLog in Django's built-in admin for superuser access.
"""
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only admin view for the audit trail."""
    list_display = ('timestamp', 'user', 'action', 'object_type', 'object_id', 'ip_address')
    list_filter = ('action', 'object_type', 'timestamp')
    search_fields = ('description', 'action', 'user__username')
    readonly_fields = (
        'user', 'action', 'object_type', 'object_id',
        'description', 'ip_address', 'user_agent', 'timestamp'
    )
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        """Audit logs are created programmatically, not manually."""
        return False

    def has_change_permission(self, request, obj=None):
        """Audit logs are immutable."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Audit logs should never be deleted."""
        return False
