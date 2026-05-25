"""
CharityOS — Donors Forms
============================
Forms for managing donor profiles.
"""
from django import forms
from .models import Donor


class DonorProfileForm(forms.ModelForm):
    """
    Form for donors to update their extended profile information.
    """
    class Meta:
        model = Donor
        fields = ['organization', 'address', 'national_id', 'is_anonymous']
        widgets = {
            'organization': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Organization name (optional)',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Your mailing address',
                'rows': 3,
            }),
            'national_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'National ID (for tax receipts)',
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-checkbox',
            }),
        }
