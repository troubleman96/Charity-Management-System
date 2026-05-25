"""
CharityOS — Beneficiaries Forms
==================================
Forms for beneficiary registration, assistance requests, and progress updates.
"""
from django import forms
from .models import Beneficiary, AssistanceRequest, BeneficiaryUpdate


class BeneficiaryForm(forms.ModelForm):
    """
    Form for registering or editing a beneficiary profile.
    Used by staff and admin users.
    """
    class Meta:
        model = Beneficiary
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'photo',
            'school_name', 'school_grade', 'health_status',
            'guardian_name', 'guardian_phone', 'guardian_relationship',
            'location_region', 'location_district',
            'date_enrolled', 'status', 'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
            'school_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'School name'}),
            'school_grade': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Grade / Class'}),
            'health_status': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Health notes'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Guardian full name'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+255...'}),
            'guardian_relationship': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Aunt, Uncle'}),
            'location_region': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Region'}),
            'location_district': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'District'}),
            'date_enrolled': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Internal notes'}),
        }


class AssistanceRequestForm(forms.ModelForm):
    """
    Form for staff to submit assistance requests for beneficiaries.
    """
    class Meta:
        model = AssistanceRequest
        fields = ['beneficiary', 'request_type', 'description', 'estimated_cost']
        widgets = {
            'beneficiary': forms.Select(attrs={'class': 'form-input'}),
            'request_type': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 4,
                'placeholder': 'Describe what the beneficiary needs and why...'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Estimated cost in TZS'
            }),
        }


class AssistanceReviewForm(forms.Form):
    """
    Form for admin to approve or reject an assistance request.
    """
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.HiddenInput()
    )
    review_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input', 'rows': 3,
            'placeholder': 'Optional review notes...'
        })
    )


class BeneficiaryUpdateForm(forms.ModelForm):
    """
    Form for staff to create progress updates for beneficiaries.
    """
    class Meta:
        model = BeneficiaryUpdate
        fields = ['beneficiary', 'title', 'content', 'photo']
        widgets = {
            'beneficiary': forms.Select(attrs={'class': 'form-input'}),
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Update title (e.g., "Term 1 Report Card")'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 5,
                'placeholder': 'Share the beneficiary\'s progress...'
            }),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
        }
