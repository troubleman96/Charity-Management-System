"""
CharityOS — Core Utilities
============================
Shared helper functions used across multiple apps.
Includes audit logging, reference number generation, and IP extraction.
"""
from .models import AuditLog


def log_action(user, action, obj=None, description='', request=None):
    """
    Create an audit log entry for a user action.

    Args:
        user:        The User who performed the action (or None for system)
        action:      Machine-readable action key (e.g., 'donation.created')
        obj:         The Django model instance affected (optional)
        description: Human-readable summary of what happened
        request:     The HttpRequest object (for IP/user agent extraction)

    Example:
        log_action(request.user, 'donation.created', donation,
                   f'Recorded donation {donation.donation_ref}', request)
    """
    ip_address = None
    user_agent = ''

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    AuditLog.objects.create(
        user=user,
        action=action,
        object_type=obj.__class__.__name__ if obj else '',
        object_id=obj.pk if obj else None,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
    )


def get_client_ip(request):
    """
    Extract the client's real IP address from the request.
    Handles proxied requests (X-Forwarded-For header).

    Returns:
        str: The client's IP address, or None if unavailable
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs; the first is the client's
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def format_currency(amount, currency='TZS'):
    """
    Format a numeric amount as a currency string.

    Args:
        amount:   The numeric amount (Decimal or float)
        currency: Currency code (default: TZS for Tanzanian Shilling)

    Returns:
        str: Formatted string like "TZS 1,250,000"
    """
    if amount is None:
        return f'{currency} 0'
    return f'{currency} {amount:,.0f}'
