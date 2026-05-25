"""
CharityOS — Donations Models
===============================
Models for tracking incoming donations, receipts, and allocation of funds.
"""
from datetime import date
from django.db import models
from django.contrib.auth.models import User
from apps.donors.models import Donor
from apps.beneficiaries.models import Beneficiary, AssistanceRequest


class Donation(models.Model):
    """
    Core donation record (both cash and in-kind).

    Status lifecycle:
        received → partial (partially allocated)
        partial → allocated (fully allocated)
        received → allocated (fully allocated at once)
    """
    DONATION_TYPES = [
        ('cash', 'Cash'),
        ('in_kind', 'In-Kind'),
    ]
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('partial', 'Partially Allocated'),
        ('allocated', 'Fully Allocated'),
    ]
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('tigopesa', 'Tigo Pesa'),
        ('bank', 'Bank Transfer'),
        ('other', 'Other'),
    ]

    donation_ref = models.CharField(
        max_length=30, unique=True, editable=False,
        help_text='Auto-generated: DON-YYYY-NNNNN'
    )
    donor = models.ForeignKey(
        Donor, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='donations',
        help_text='NULL indicates an anonymous/unregistered donor'
    )
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES)

    # --- Cash Fields ---
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text='Donation amount in TZS (if cash)'
    )
    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_METHODS, blank=True
    )
    transaction_reference = models.CharField(
        max_length=100, blank=True,
        help_text='Mobile money or bank reference number'
    )

    # --- In-Kind Fields ---
    in_kind_description = models.TextField(
        blank=True,
        help_text='Description of physical items donated'
    )
    in_kind_estimated_value = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text='Estimated value in TZS (optional)'
    )

    # --- General Fields ---
    donation_date = models.DateField()
    purpose = models.CharField(
        max_length=200, blank=True,
        help_text='e.g., Education Fund, General Fund'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='received'
    )
    notes = models.TextField(blank=True)

    # --- Metadata ---
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='recorded_donations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-donation_date', '-created_at']
        indexes = [
            models.Index(fields=['donation_date']),
            models.Index(fields=['status']),
            models.Index(fields=['donation_type']),
        ]

    def __str__(self):
        return f'{self.donation_ref} - {self.get_donation_type_display()} - {self.donor or "Anonymous"}'

    def save(self, *args, **kwargs):
        """Auto-generate donation reference on first save."""
        if not self.donation_ref:
            year = date.today().year
            last_count = Donation.objects.filter(
                donation_ref__startswith=f'DON-{year}'
            ).count()
            self.donation_ref = f'DON-{year}-{str(last_count + 1).zfill(5)}'
        super().save(*args, **kwargs)

    @property
    def allocated_amount(self):
        """Total funds allocated from this donation."""
        return self.allocations.aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def remaining_amount(self):
        """Funds remaining to be allocated."""
        if self.donation_type == 'cash' and self.amount:
            return self.amount - self.allocated_amount
        return 0


class DonationReceipt(models.Model):
    """
    Digital receipt linked to a donation.
    Auto-generated as a PDF and emailed to the donor.
    """
    EMAIL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    donation = models.OneToOneField(
        Donation, on_delete=models.CASCADE,
        related_name='receipt'
    )
    receipt_number = models.CharField(max_length=30, unique=True)
    pdf_file = models.FileField(upload_to='receipts/', blank=True, null=True)
    emailed_at = models.DateTimeField(null=True, blank=True)
    email_status = models.CharField(
        max_length=20, choices=EMAIL_STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Receipt {self.receipt_number} for {self.donation.donation_ref}'


class DonationAllocation(models.Model):
    """
    Record of funds disbursed from a cash donation towards a beneficiary or request.
    """
    ALLOCATION_TYPES = [
        ('education', 'Education'),
        ('food', 'Food'),
        ('medical', 'Medical'),
        ('clothing', 'Clothing'),
        ('general', 'General Operations'),
    ]

    donation = models.ForeignKey(
        Donation, on_delete=models.CASCADE,
        related_name='allocations'
    )
    beneficiary = models.ForeignKey(
        Beneficiary, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='allocations'
    )
    assistance_request = models.ForeignKey(
        AssistanceRequest, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='allocations'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    allocation_type = models.CharField(max_length=50, choices=ALLOCATION_TYPES)
    description = models.TextField(blank=True)

    allocated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='made_allocations'
    )
    allocated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-allocated_at']

    def __str__(self):
        return f'Allocated {self.amount} from {self.donation.donation_ref}'

    def save(self, *args, **kwargs):
        """Update the parent donation status when an allocation is saved."""
        super().save(*args, **kwargs)
        # Update donation status
        don = self.donation
        if don.donation_type == 'cash':
            if don.remaining_amount <= 0:
                don.status = 'allocated'
            elif don.allocated_amount > 0:
                don.status = 'partial'
            don.save(update_fields=['status'])
