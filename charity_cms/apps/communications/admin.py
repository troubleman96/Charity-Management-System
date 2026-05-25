"""
CharityOS — Communications Admin Registration
"""
from django.contrib import admin
from .models import Notification, Message, EmailLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'email_type', 'subject', 'status', 'sent_at')
    list_filter = ('status', 'email_type', 'created_at')
    search_fields = ('recipient_email', 'subject')
    readonly_fields = ('created_at', 'sent_at')
