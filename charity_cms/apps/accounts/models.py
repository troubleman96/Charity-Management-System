"""
CharityOS — Accounts Models
==============================
UserProfile extends Django's built-in User model with role and profile data.
Uses a OneToOne relationship pattern (not custom User model) for simplicity.

Roles:
    - admin:  Full system access, user management, approvals
    - staff:  Beneficiary management, donation recording, requests
    - donor:  View own donations, sponsored beneficiaries, receipts
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user profile linked to Django's User model.
    Every User gets a UserProfile via the post_save signal (see signals.py).

    Fields:
        user       — OneToOne link to Django's User model
        role       — System role determining access level
        phone      — Contact phone number (optional)
        avatar     — Profile picture (optional)
        created_at — When the profile was created
        updated_at — When the profile was last modified
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff / Volunteer'),
        ('donor', 'Donor'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text='The Django User this profile extends'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='donor',
        help_text='Determines which dashboard and features the user can access'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Contact phone number (e.g., +255712345678)'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text='Profile picture'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['role'])]
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        """Check if the user has admin role."""
        return self.role == 'admin'

    @property
    def is_staff_member(self):
        """Check if the user has staff role."""
        return self.role == 'staff'

    @property
    def is_donor(self):
        """Check if the user has donor role."""
        return self.role == 'donor'
