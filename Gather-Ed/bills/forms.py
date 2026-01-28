from django import forms
from django.contrib.auth.models import User
from eventpollapp.models import Event
from .models import Bill, Expense, Settlement
from django.db.models import Q

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show events where user is creator or participant
        from django.db.models import Q
        self.fields['event'] = forms.ModelChoiceField(
            queryset=Event.objects.filter(
                Q(creator=user) | Q(participants__user=user),
                is_date_finalized=True
            ).distinct(),
            widget=forms.Select(attrs={'class': 'form-control'}),
            empty_label="Select an event..."
        )


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['description', 'amount', 'paid_by', 'shared_by', 'receipt_image']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'paid_by': forms.Select(attrs={'class': 'form-control'}),
            'shared_by': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'receipt_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, bill, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get event participants for this bill
        event_participants = User.objects.filter(
            Q(created_events=bill.event) | Q(eventparticipant__event=bill.event)
        ).distinct()
        
        self.fields['paid_by'].queryset = event_participants
        self.fields['shared_by'].queryset = event_participants
        
        # Pre-select all participants for shared_by by default
        if not self.instance.pk:
            self.fields['shared_by'].initial = event_participants


class SettlementForm(forms.ModelForm):
    class Meta:
        model = Settlement
        fields = ['to_user', 'amount', 'notes']
        widgets = {
            'to_user': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional notes...'}),
        }

    def __init__(self, bill, from_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get other participants in the bill
        other_participants = User.objects.filter(
            Q(created_events=bill.event) | Q(eventparticipant__event=bill.event)
        ).exclude(id=from_user.id).distinct()
        
        self.fields['to_user'].queryset = other_participants


class BillFilterForm(forms.Form):
    EVENT_CHOICES = [
        ('', 'All Events'),
    ]
    SETTLEMENT_CHOICES = [
        ('', 'All Bills'),
        ('settled', 'Settled'),
        ('unsettled', 'Unsettled'),
    ]
    
    event = forms.ChoiceField(
        choices=EVENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    settlement_status = forms.ChoiceField(
        choices=SETTLEMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get user's events
        from django.db.models import Q
        user_events = Event.objects.filter(
            Q(creator=user) | Q(participants__user=user)
        ).distinct()
        
        event_choices = [('', 'All Events')]
        for event in user_events:
            event_choices.append((event.id, event.title))
        
        self.fields['event'].choices = event_choices