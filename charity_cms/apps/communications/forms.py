"""
CharityOS — Communications Forms
===================================
Forms for sending internal messages and broadcasting emails.
"""
from django import forms
from django.contrib.auth.models import User
from .models import Message


class MessageForm(forms.ModelForm):
    """
    Form for composing internal direct messages.
    Only allows sending messages to admin or staff users.
    """
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-input'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Message subject'}),
            'body': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Type your message...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter recipients to only include staff and admins
        self.fields['recipient'].queryset = User.objects.filter(
            profile__role__in=['admin', 'staff']
        ).select_related('profile')


class BroadcastForm(forms.Form):
    """
    Form for admins to broadcast an email to all donors.
    """
    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Broadcast Subject'
        })
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 8,
            'placeholder': 'Write the email content here...'
        })
    )
