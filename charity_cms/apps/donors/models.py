"""
CharityOS — Donors Models
============================
Donor model stores extended donor-specific information beyond the User profile.

Each Donor is linked to a User account via OneToOne relationship.
The Donor model tracks organization affiliation, anonymity preferences,
and provides computed properties for donation totals.
"""
from django.db import models
from django.contrib.auth.models import User


class Donor(models.Model):
    """
    Extended donor profile linked to a User account.

    Fields:
        user         — OneToOne link to the User account
        organization — Company/org name if corporate donor
        address      — Mailing address
        national_id  — Government ID (for tax receipts)
        is_anonymous — Whether to hide donor name in public displays
        notes        — Internal admin notes about this donor
        created_at   — When the donor record was created
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='donor_profile',
        help_text='The User account this donor profile belongs to'
    )
    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text='Organization name (for corporate donors)'
    )
    address = models.TextField(
        blank=True,
        help_text='Mailing address'
    )
    national_id = models.CharField(
        max_length=50,
        blank=True,
        help_text='National ID for tax receipt purposes'
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text='Hide donor name in public listings'
    )
    notes = models.TextField(
        blank=True,
        help_text='Internal notes about this donor (admin only)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Donor'
        verbose_name_plural = 'Donors'

    def __str__(self):
        if self.is_anonymous:
            return 'Anonymous Donor'
        return self.user.get_full_name() or self.user.email

    @property
    def total_donated(self):
        """Calculate total cash amount donated by this donor."""
        return self.donations.filter(
            donation_type='cash'
        ).aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def donation_count(self):
        """Count total number of donations made."""
        return self.donations.count()

    @property
    def display_name(self):
        """Get display name respecting anonymity preference."""
        if self.is_anonymous:
            return 'Anonymous'
        return self.user.get_full_name() or self.user.email
