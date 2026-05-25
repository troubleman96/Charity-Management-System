"""
CharityOS — Context Processors
================================
Global context variables available in every template.
Registered in settings.TEMPLATES.OPTIONS.context_processors.

Provides:
    - organization_name: The charity organization's display name
    - unread_notifications_count: Count of unread notifications for current user
    - unread_messages_count: Count of unread messages for current user
    - user_role: The current user's role string (admin/staff/donor)
"""
from django.conf import settings


def global_context(request):
    """
    Inject global variables into every template context.
    This runs on every request, so we keep queries lightweight.
    """
    context = {
        'organization_name': getattr(settings, 'ORGANIZATION_NAME', 'CharityOS'),
        'organization_logo': getattr(settings, 'ORGANIZATION_LOGO', ''),
    }

    # Only add user-specific data for authenticated users
    if request.user.is_authenticated:
        # Get the user's role from their profile
        profile = getattr(request.user, 'profile', None)
        context['user_role'] = profile.role if profile else 'unknown'

        # Count unread notifications (lazy import to avoid circular imports)
        try:
            from apps.communications.models import Notification, Message
            context['unread_notifications_count'] = (
                Notification.objects.filter(user=request.user, is_read=False).count()
            )
            context['unread_messages_count'] = (
                Message.objects.filter(recipient=request.user, is_read=False).count()
            )
        except Exception:
            # Gracefully handle if communications app isn't ready yet
            context['unread_notifications_count'] = 0
            context['unread_messages_count'] = 0

    return context
