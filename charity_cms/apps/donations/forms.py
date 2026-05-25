"""
CharityOS — Donations Forms
===============================
Forms for recording donations and allocating funds.
"""
from django import forms
from .models import Donation, DonationAllocation


class DonationForm(forms.ModelForm):
    """
    Form for staff to record a new incoming donation.
    Handles both cash and in-kind validation.
    """
    class Meta:
        model = Donation
        fields = [
            'donor', 'donation_type', 'donation_date', 'purpose',
            'amount', 'payment_method', 'transaction_reference',
            'in_kind_description', 'in_kind_estimated_value', 'notes'
        ]
        widgets = {
            'donor': forms.Select(attrs={'class': 'form-input'}),
            'donation_type': forms.Select(attrs={'class': 'form-input', 'id': 'id_donation_type'}),
            'donation_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'purpose': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., General Fund'}),

            # Cash fields
            'amount': forms.NumberInput(attrs={'class': 'form-input cash-field', 'placeholder': 'TZS'}),
            'payment_method': forms.Select(attrs={'class': 'form-input cash-field'}),
            'transaction_reference': forms.TextInput(attrs={'class': 'form-input cash-field'}),

            # In-kind fields
            'in_kind_description': forms.Textarea(attrs={'class': 'form-input inkind-field', 'rows': 3}),
            'in_kind_estimated_value': forms.NumberInput(attrs={'class': 'form-input inkind-field', 'placeholder': 'TZS (Optional)'}),

            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }

    def clean(self):
        """Validate conditional fields based on donation type."""
        cleaned = super().clean()
        dtype = cleaned.get('donation_type')

        if dtype == 'cash':
            if not cleaned.get('amount'):
                self.add_error('amount', 'Amount is required for cash donations.')
            if not cleaned.get('payment_method'):
                self.add_error('payment_method', 'Payment method is required for cash donations.')

        elif dtype == 'in_kind':
            if not cleaned.get('in_kind_description'):
                self.add_error('in_kind_description', 'Description is required for in-kind donations.')

        return cleaned


class AllocationForm(forms.ModelForm):
    """
    Form for admins to allocate funds from a cash donation to a beneficiary/request.
    """
    class Meta:
        model = DonationAllocation
        fields = ['beneficiary', 'assistance_request', 'amount', 'allocation_type', 'description']
        widgets = {
            'beneficiary': forms.Select(attrs={'class': 'form-input'}),
            'assistance_request': forms.Select(attrs={'class': 'form-input'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'TZS'}),
            'allocation_type': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.donation = kwargs.pop('donation', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        """Ensure allocation doesn't exceed remaining donation funds."""
        amount = self.cleaned_data.get('amount')
        if self.donation and amount:
            if amount > self.donation.remaining_amount:
                raise forms.ValidationError(
                    f'Allocation amount (TZS {amount:,.0f}) exceeds available balance (TZS {self.donation.remaining_amount:,.0f}).'
                )
            if amount <= 0:
                raise forms.ValidationError('Amount must be greater than zero.')
        return amount
