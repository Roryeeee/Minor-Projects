# Path: eventpollapp/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from accounts.models import Friendship, UserRole
from .models import Event, DateOption, DateVote, EventRequirement, EventComment, EventParticipant
from .forms import EventForm, DateOptionForm, EventRequirementForm, EventCommentForm, EventParticipationForm
from datetime import datetime
import calendar

@login_required
def dashboard(request):
    """Main dashboard with calendar view"""
    now = datetime.now()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))

    user_events = Event.objects.filter(
        Q(creator=request.user) | Q(participants__user=request.user)
    ).filter(
        finalized_date__month=month,
        finalized_date__year=year,
        is_date_finalized=True
    ).distinct()

    recent_events = Event.objects.filter(
        Q(creator=request.user) |
        Q(required_role__userrole__user=request.user) |
        Q(required_role__isnull=True)
    ).distinct()[:5]

    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    calendar_days = cal.monthdays2calendar(year, month)

    events_by_day = {}
    for event in user_events:
        day = event.finalized_date.day
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    context = {
        'current_month': month,
        'current_year': year,
        'calendar_days': calendar_days,
        'events_by_day': events_by_day,
        'recent_events': recent_events,
        'month_name': calendar.month_name[month],
        'prev_month': month - 1 if month > 1 else 12,
        'next_month': month + 1 if month < 12 else 1,
        'prev_year': year if month > 1 else year - 1,
        'next_year': year if month < 12 else year + 1,
    }

    return render(request, 'eventpollapp/dashboard.html', context)


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.creator != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to delete this event.")
        return redirect('eventpollapp:dashboard')
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('eventpollapp:dashboard')


@login_required
def event_list(request):
    """List all events user can see"""
    user_roles = request.user.userrole_set.values_list('role_id', flat=True)

    events = Event.objects.filter(
        Q(required_role__isnull=True) |
        Q(required_role_id__in=user_roles) |
        Q(creator=request.user)
    ).distinct().prefetch_related('dateoption_set', 'participants')

    return render(request, 'eventpollapp/event_list.html', {'events': events})


@login_required
def create_event(request):
    """Create a new event"""
    if request.method == 'POST':
        form = EventForm(request.user, request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()

            date_options = form.cleaned_data['date_options']
            for date_option in date_options:
                DateOption.objects.create(
                    event=event,
                    proposed_date=date_option,
                    proposed_by=request.user
                )

            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('eventpollapp:event_detail', event_id=event.id)
    else:
        form = EventForm(request.user)

    return render(request, 'eventpollapp/create_event.html', {'form': form})


@login_required
def event_detail(request, event_id):
    """View event details with voting and collaboration"""
    event = get_object_or_404(Event, id=event_id)

    can_access = (
        event.creator == request.user or
        event.required_role is None or
        UserRole.objects.filter(user=request.user, role=event.required_role).exists()
    )
    if not can_access:
        messages.error(request, "You don't have permission to view this event.")
        return redirect('eventpollapp:event_list')

    user_votes = DateVote.objects.filter(
        user=request.user,
        date_option__event=event
    ).values_list('date_option_id', flat=True)

    date_options = event.dateoption_set.annotate(
        vote_count=Count('votes')
    ).order_by('-vote_count', 'proposed_date')

    comment_form = EventCommentForm()
    requirement_form = EventRequirementForm(event)

    try:
        participation = EventParticipant.objects.get(event=event, user=request.user)
        current_status = participation.status
    except EventParticipant.DoesNotExist:
        current_status = None

    participation_form = EventParticipationForm(initial={'status': current_status})

    context = {
        'event': event,
        'date_options': date_options,
        'user_votes': user_votes,
        'comment_form': comment_form,
        'requirement_form': requirement_form,
        'participation_form': participation_form,
        'current_status': current_status,
        'can_edit': event.creator == request.user,
    }

    return render(request, 'eventpollapp/event_detail.html', context)


@login_required
@require_POST
def vote_date(request, event_id, date_option_id):
    """Vote for a date option"""
    event = get_object_or_404(Event, id=event_id)
    date_option = get_object_or_404(DateOption, id=date_option_id, event=event)

    can_access = (
        event.creator == request.user or
        event.required_role is None or
        UserRole.objects.filter(user=request.user, role=event.required_role).exists()
    )
    if not can_access:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if event.is_date_finalized:
        return JsonResponse({'error': 'Event date is already finalized'}, status=400)

    vote, created = DateVote.objects.get_or_create(
        user=request.user,
        date_option=date_option
    )

    if not created:
        vote.delete()
        voted = False
    else:
        voted = True

    vote_count = date_option.votes.count()

    return JsonResponse({
        'voted': voted,
        'vote_count': vote_count
    })


@login_required
@require_POST
def finalize_event_date(request, event_id):
    """Finalize the event date, or trigger wheel if tie"""
    event = get_object_or_404(Event, id=event_id, creator=request.user)

    if event.is_date_finalized:
        messages.warning(request, "Event date is already finalized.")
        return redirect('eventpollapp:event_detail', event_id=event_id)

    # If wheel already selected a date
    selected_date_id = request.POST.get("selected_date")
    if selected_date_id:
        winning_option = get_object_or_404(DateOption, id=selected_date_id, event=event)
        event.finalized_date = winning_option.proposed_date
        event.is_date_finalized = True
        event.save()
        messages.success(request, f"Event date finalized for {event.finalized_date.strftime('%B %d, %Y at %I:%M %p')}!")
        return redirect('eventpollapp:event_detail', event_id=event_id)

    # Otherwise, check top-voted options
    tied_options = event.get_top_voted_options()
    if not tied_options:
        messages.error(request, "No date options available to finalize.")
        return redirect('eventpollapp:event_detail', event_id=event_id)

    if len(tied_options) > 1:
        # Render wheel page to break tie
        return render(request, "eventpollapp/randomize_wheel.html", {
            "event": event,
            "tied_options": tied_options,
        })

    # Only one top option → finalize directly
    winning_option = tied_options[0]
    event.finalized_date = winning_option.proposed_date
    event.is_date_finalized = True
    event.save()
    messages.success(request, f"Event date finalized for {event.finalized_date.strftime('%B %d, %Y at %I:%M %p')}!")
    return redirect('eventpollapp:event_detail', event_id=event_id)


@login_required
def add_requirement(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    can_access = (
        event.creator == request.user or
        event.required_role is None or
        UserRole.objects.filter(user=request.user, role=event.required_role).exists()
    )
    if not can_access:
        messages.error(request, "You don't have permission to add requirements to this event.")
        return redirect('eventpollapp:event_detail', event_id=event_id)

    if request.method == 'POST':
        form = EventRequirementForm(event, request.POST)
        if form.is_valid():
            requirement = form.save(commit=False)
            requirement.event = event
            requirement.added_by = request.user
            requirement.save()
            messages.success(request, 'Requirement added successfully!')
            return redirect('eventpollapp:event_detail', event_id=event_id)

    return redirect('eventpollapp:event_detail', event_id=event_id)


@login_required
@require_POST
def toggle_requirement_completion(request, requirement_id):
    requirement = get_object_or_404(EventRequirement, id=requirement_id)

    can_modify = (
        requirement.added_by == request.user or
        requirement.assigned_to == request.user or
        requirement.event.creator == request.user
    )
    if not can_modify:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    requirement.is_completed = not requirement.is_completed
    requirement.save()

    return JsonResponse({'is_completed': requirement.is_completed})


@login_required
@require_POST
def add_comment(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    can_access = (
        event.creator == request.user or
        event.required_role is None or
        UserRole.objects.filter(user=request.user, role=event.required_role).exists()
    )
    if not can_access:
        messages.error(request, "You don't have permission to comment on this event.")
        return redirect('eventpollapp:event_detail', event_id=event_id)

    form = EventCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.event = event
        comment.user = request.user
        comment.save()
        messages.success(request, 'Comment added!')

    return redirect('eventpollapp:event_detail', event_id=event_id)


@login_required
@require_POST
def update_participation(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    can_access = (
        event.creator == request.user or
        event.required_role is None or
        UserRole.objects.filter(user=request.user, role=event.required_role).exists()
    )
    if not can_access:
        messages.error(request, "You don't have permission to participate in this event.")
        return redirect('eventpollapp:event_detail', event_id=event_id)

    form = EventParticipationForm(request.POST)
    if form.is_valid():
        status = form.cleaned_data['status']
        participation, created = EventParticipant.objects.get_or_create(
            event=event,
            user=request.user,
            defaults={'status': status}
        )
        if not created:
            participation.status = status
            participation.save()

        messages.success(request, f'Participation status updated to: {status.title()}')

    return redirect('eventpollapp:event_detail', event_id=event_id)


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.creator != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to edit this event.")
        return redirect('eventpollapp:event_detail', event_id=event.id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully.")
            return redirect('eventpollapp:event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, 'eventpollapp/edit_event.html', {'form': form, 'event': event})
