"""
CharityOS — Custom Template Tags & Filters
=============================================
Reusable template filters for formatting data in templates.

Usage in templates:
    {% load charity_tags %}
    {{ amount|currency }}           → "TZS 1,250,000"
    {{ user|initials }}             → "AM"
    {{ "pending"|status_color }}    → "pill-orange"
"""
from django import template

register = template.Library()


@register.filter
def currency(value):
    """
    Format a number as Tanzanian Shilling currency.
    Usage: {{ donation.amount|currency }}
    Output: "TZS 1,250,000"
    """
    if value is None:
        return 'TZS 0'
    try:
        return f'TZS {float(value):,.0f}'
    except (ValueError, TypeError):
        return f'TZS {value}'


@register.filter
def currency_short(value):
    """
    Format a number as abbreviated TZS (e.g., 1.2M, 450K).
    Usage: {{ total|currency_short }}
    Output: "TZS 1.2M" or "TZS 450K"
    """
    if value is None:
        return 'TZS 0'
    try:
        num = float(value)
        if num >= 1_000_000:
            return f'TZS {num / 1_000_000:.1f}M'
        elif num >= 1_000:
            return f'TZS {num / 1_000:.0f}K'
        else:
            return f'TZS {num:,.0f}'
    except (ValueError, TypeError):
        return f'TZS {value}'


@register.filter
def initials(user):
    """
    Extract initials from a User object's name.
    Usage: {{ user|initials }}
    Output: "AM" (for Ali Mwenda)
    """
    if not user:
        return '??'
    first = getattr(user, 'first_name', '') or ''
    last = getattr(user, 'last_name', '') or ''
    if first and last:
        return f'{first[0]}{last[0]}'.upper()
    elif first:
        return first[:2].upper()
    elif hasattr(user, 'email') and user.email:
        return user.email[0].upper()
    return '??'


@register.filter
def status_color(status):
    """
    Map a status string to a CSS pill class for colored badges.
    Usage: {{ donation.status|status_color }}
    Output: "pill-blue" | "pill-green" | "pill-orange" | "pill-red"
    """
    color_map = {
        # Donation statuses
        'received': 'pill-blue',
        'allocated': 'pill-green',
        'partial': 'pill-orange',
        # Request statuses
        'pending': 'pill-orange',
        'approved': 'pill-green',
        'rejected': 'pill-red',
        'fulfilled': 'pill-blue',
        # Beneficiary statuses
        'active': 'pill-green',
        'inactive': 'pill-red',
        'graduated': 'pill-blue',
        # Email statuses
        'sent': 'pill-green',
        'failed': 'pill-red',
        # Donation types
        'cash': 'pill-green',
        'in_kind': 'pill-orange',
    }
    return color_map.get(status, 'pill-blue')


@register.filter
def percentage(value, total):
    """
    Calculate percentage of value relative to total.
    Usage: {{ part|percentage:whole }}
    Output: 72 (as integer)
    """
    try:
        if total and float(total) > 0:
            return int((float(value) / float(total)) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        pass
    return 0
