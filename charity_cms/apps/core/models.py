"""
CharityOS — Core Models
========================
Contains the AuditLog model for tracking all system actions.
This provides an immutable audit trail for security and accountability.
"""
from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    """
    Immutable audit trail entry.
    Records who did what, when, and from where.
    Used for security monitoring and regulatory compliance.

    Fields:
        user        — The user who performed the action (NULL for system actions)
        action      — Machine-readable action key (e.g., "donation.created")
        object_type — The type of object affected (e.g., "Donation")
        object_id   — The primary key of the affected object
        description — Human-readable summary of what happened
        ip_address  — The IP address of the request
        user_agent  — The browser/client user agent string
        timestamp   — When the action occurred (auto-set)
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text='User who performed the action. NULL for system actions.'
    )
    action = models.CharField(
        max_length=100,
        help_text='Machine-readable action key, e.g. "donation.created"'
    )
    object_type = models.CharField(
        max_length=100,
        blank=True,
        help_text='Type of object affected, e.g. "Donation"'
    )
    object_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='Primary key of the affected object'
    )
    description = models.TextField(
        blank=True,
        help_text='Human-readable summary of the action'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the request (IPv4 or IPv6)'
    )
    user_agent = models.TextField(
        blank=True,
        help_text='Browser/client user agent string'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['action']),
            models.Index(fields=['object_type']),
            models.Index(fields=['timestamp']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        user_str = self.user.get_full_name() if self.user else 'System'
        return f'[{self.timestamp:%Y-%m-%d %H:%M}] {user_str}: {self.action}'
