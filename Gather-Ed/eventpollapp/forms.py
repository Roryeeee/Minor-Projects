# Path: eventpollapp/forms.py

from django import forms
from django.contrib.auth.models import User
from accounts.models import Role, UserRole
from .models import Event, DateOption, EventRequirement, EventComment

class EventForm(forms.ModelForm):
    date_options = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter multiple date/time options, one per line.\nFormat: YYYY-MM-DD HH:MM\nExample:\n2024-12-25 14:00\n2024-12-26 16:30'
        }),
        help_text="Enter date and time options, one per line (Format: YYYY-MM-DD HH:MM)"
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'required_role', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'required_role': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show roles created by the user
        self.fields['required_role'].queryset = Role.objects.filter(created_by=user)
        self.fields['required_role'].empty_label = "No specific role required"

    def clean_date_options(self):
        date_options_text = self.cleaned_data['date_options']
        date_options = []
        
        for line in date_options_text.strip().split('\n'):
            line = line.strip()
            if line:
                try:
                    from datetime import datetime
                    # Parse datetime in format YYYY-MM-DD HH:MM
                    dt = datetime.strptime(line, '%Y-%m-%d %H:%M')
                    date_options.append(dt)
                except ValueError:
                    raise forms.ValidationError(f'Invalid date format: "{line}". Use YYYY-MM-DD HH:MM format.')
        
        if not date_options:
            raise forms.ValidationError('At least one date option is required.')
        
        return date_options


class DateOptionForm(forms.ModelForm):
    class Meta:
        model = DateOption
        fields = ['proposed_date']
        widgets = {
            'proposed_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }


class EventRequirementForm(forms.ModelForm):
    class Meta:
        model = EventRequirement
        fields = ['requirement_type', 'title', 'description', 'assigned_to']
        widgets = {
            'requirement_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get users who have the required role for this event
        if event.required_role:
            eligible_users = User.objects.filter(
                userrole__role=event.required_role
            ).distinct()
        else:
            # If no specific role required, get event creator's friends
            from accounts.models import Friendship
            from django.db.models import Q
            eligible_users = User.objects.filter(
                Q(friendship_requests_sent__to_user=event.creator, friendship_requests_sent__status='accepted') |
                Q(friendship_requests_received__from_user=event.creator, friendship_requests_received__status='accepted')
            ).distinct()
        
        self.fields['assigned_to'].queryset = eligible_users
        self.fields['assigned_to'].empty_label = "Not assigned"


class EventCommentForm(forms.ModelForm):
    class Meta:
        model = EventComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            })
        }


class EventParticipationForm(forms.Form):
    STATUS_CHOICES = [
        ('interested', 'Interested'),
        ('going', 'Going'),
        ('maybe', 'Maybe'),
        ('not_going', 'Not Going'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )