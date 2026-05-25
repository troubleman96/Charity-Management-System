"""
CharityOS — Beneficiaries Models
===================================
Core models for managing orphan beneficiaries:

- Beneficiary:          Child profile with education, health, and guardian details
- DonorBeneficiaryLink: Links donors to sponsored beneficiaries
- AssistanceRequest:    Staff-submitted requests for beneficiary needs
- BeneficiaryUpdate:   Progress updates shared with linked donors
"""
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from apps.donors.models import Donor


class Beneficiary(models.Model):
    """
    Represents an orphaned child registered in the system.
    Auto-generates a unique code like BEN-2025-0001 on creation.

    Status lifecycle:
        active → inactive (admin deactivates)
        active → graduated (aged out or completed program)
        inactive → active (re-enrolled)
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    # --- Identification ---
    beneficiary_code = models.CharField(
        max_length=20, unique=True, editable=False,
        help_text='Auto-generated code: BEN-YYYY-NNNN'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    photo = models.ImageField(upload_to='beneficiaries/', blank=True, null=True)

    # --- Education ---
    school_name = models.CharField(max_length=200, blank=True)
    school_grade = models.CharField(max_length=50, blank=True)

    # --- Health ---
    health_status = models.TextField(
        blank=True,
        help_text='Current health conditions or notes'
    )

    # --- Guardian Information ---
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_relationship = models.CharField(
        max_length=50, blank=True,
        help_text='e.g., Aunt, Uncle, Grandmother'
    )

    # --- Location ---
    location_region = models.CharField(max_length=100, blank=True)
    location_district = models.CharField(max_length=100, blank=True)

    # --- Program Status ---
    date_enrolled = models.DateField(help_text='Date beneficiary was enrolled in the program')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, help_text='Internal notes about this beneficiary')

    # --- Metadata ---
    registered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='registered_beneficiaries',
        help_text='Staff member who registered this beneficiary'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Beneficiaries'
        ordering = ['-date_enrolled']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['beneficiary_code']),
            models.Index(fields=['location_region']),
        ]

    def __str__(self):
        return f'{self.get_full_name()} ({self.beneficiary_code})'

    def save(self, *args, **kwargs):
        """Auto-generate beneficiary code on first save."""
        if not self.beneficiary_code:
            year = date.today().year
            last_count = Beneficiary.objects.filter(
                beneficiary_code__startswith=f'BEN-{year}'
            ).count()
            self.beneficiary_code = f'BEN-{year}-{str(last_count + 1).zfill(4)}'
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Return the beneficiary's full name."""
        return f'{self.first_name} {self.last_name}'

    @property
    def age(self):
        """Calculate the beneficiary's current age in years."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class DonorBeneficiaryLink(models.Model):
    """
    Links a donor to a beneficiary they sponsor.
    A donor can sponsor multiple beneficiaries, and a beneficiary
    can have multiple sponsors.

    The is_active flag and end_date track sponsorship lifecycle.
    """
    donor = models.ForeignKey(
        Donor, on_delete=models.CASCADE,
        related_name='sponsored_beneficiaries'
    )
    beneficiary = models.ForeignKey(
        Beneficiary, on_delete=models.CASCADE,
        related_name='donor_links'
    )
    start_date = models.DateField()
    end_date = models.DateField(
        null=True, blank=True,
        help_text='NULL means currently active sponsorship'
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('donor', 'beneficiary')
        verbose_name = 'Donor-Beneficiary Link'
        verbose_name_plural = 'Donor-Beneficiary Links'

    def __str__(self):
        return f'{self.donor} → {self.beneficiary}'


class AssistanceRequest(models.Model):
    """
    A request submitted by staff for a beneficiary's needs.
    Must be approved by an admin before funds can be allocated.

    Status lifecycle:
        pending → approved (admin approves)
        pending → rejected (admin rejects)
        approved → fulfilled (funds allocated)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('fulfilled', 'Fulfilled'),
    ]
    REQUEST_TYPES = [
        ('education', 'Education'),
        ('food', 'Food'),
        ('medical', 'Medical'),
        ('clothing', 'Clothing'),
        ('other', 'Other'),
    ]

    request_ref = models.CharField(
        max_length=30, unique=True, editable=False,
        help_text='Auto-generated: REQ-YYYY-NNNN'
    )
    beneficiary = models.ForeignKey(
        Beneficiary, on_delete=models.CASCADE,
        related_name='assistance_requests'
    )
    requested_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='submitted_requests',
        help_text='Staff member who submitted this request'
    )
    request_type = models.CharField(max_length=50, choices=REQUEST_TYPES)
    description = models.TextField(help_text='Detailed description of the need')
    estimated_cost = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text='Estimated cost in TZS'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_requests',
        help_text='Admin who approved/rejected'
    )
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['beneficiary']),
            models.Index(fields=['status']),
            models.Index(fields=['request_type']),
        ]

    def __str__(self):
        return f'{self.request_ref} - {self.beneficiary.get_full_name()} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        """Auto-generate request reference on first save."""
        if not self.request_ref:
            year = date.today().year
            last_count = AssistanceRequest.objects.filter(
                request_ref__startswith=f'REQ-{year}'
            ).count()
            self.request_ref = f'REQ-{year}-{str(last_count + 1).zfill(4)}'
        super().save(*args, **kwargs)


class BeneficiaryUpdate(models.Model):
    """
    Progress update for a beneficiary, shared with linked donors.
    Contains a title, narrative content, and optional photo.
    When created, linked donors are notified via email/in-app notification.
    """
    beneficiary = models.ForeignKey(
        Beneficiary, on_delete=models.CASCADE,
        related_name='updates'
    )
    title = models.CharField(max_length=200)
    content = models.TextField(help_text='Progress narrative for donors')
    photo = models.ImageField(
        upload_to='beneficiary_updates/',
        blank=True, null=True,
        help_text='Optional photo to accompany the update'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='created_updates'
    )
    notified_donors = models.BooleanField(
        default=False,
        help_text='Whether linked donors have been notified'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.beneficiary.get_full_name()}'
