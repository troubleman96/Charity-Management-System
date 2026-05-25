"""
CharityOS — Communications Models
====================================
Models for internal messaging, system notifications, and outbound email logging.
"""
from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """
    In-app system notification for a specific user.
    Alerts users to important events like new donations, approvals, etc.
    """
    TYPES = [
        ('donation_received', 'Donation Received'),
        ('low_funds', 'Low Funds Alert'),
        ('request_approved', 'Request Approved'),
        ('request_rejected', 'Request Rejected'),
        ('update_available', 'Beneficiary Update'),
        ('system', 'System Message'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.URLField(
        max_length=500, blank=True,
        help_text='URL to the relevant item'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'{self.title} ({"Read" if self.is_read else "Unread"})'


class Message(models.Model):
    """
    Internal direct message between staff/admin users.
    """
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='received_messages'
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'From {self.sender} to {self.recipient}: {self.subject}'


class EmailLog(models.Model):
    """
    Audit log of all outbound emails sent by the system (via Celery).
    Tracks delivery status and stores error messages if sending fails.
    """
    EMAIL_TYPES = [
        ('donation_receipt', 'Donation Receipt'),
        ('low_funds_alert', 'Low Funds Alert'),
        ('broadcast', 'Broadcast Message'),
        ('update', 'Beneficiary Update'),
        ('password_reset', 'Password Reset'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    email_type = models.CharField(max_length=50, choices=EMAIL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    celery_task_id = models.CharField(max_length=255, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'

    def __str__(self):
        return f'{self.email_type} to {self.recipient_email} ({self.status})'
