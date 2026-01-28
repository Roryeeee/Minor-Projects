# Path: eventpollapp/models.py

from django.db import models
from django.contrib.auth.models import User
from accounts.models import Role
import random

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    required_role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    is_date_finalized = models.BooleanField(default=False)
    finalized_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_winning_date_option(self):
        """Get the date option with the most votes"""
        if self.is_date_finalized and self.finalized_date:
            return self.dateoption_set.filter(proposed_date=self.finalized_date).first()
        
        vote_counts = []
        for date_option in self.dateoption_set.all():
            vote_count = date_option.votes.count()
            vote_counts.append((date_option, vote_count))
        
        if not vote_counts:
            return None
        
        # Sort by vote count (descending)
        vote_counts.sort(key=lambda x: x[1], reverse=True)
        
        # Check for ties at the top
        max_votes = vote_counts[0][1]
        tied_options = [option for option, count in vote_counts if count == max_votes]
        
        if len(tied_options) > 1:
            # Random selection for tie-breaking
            return random.choice(tied_options)
        
        return tied_options[0]

    def finalize_date(self):
        """Finalize the event date based on voting"""
        winning_option = self.get_winning_date_option()
        if winning_option:
            self.finalized_date = winning_option.proposed_date
            self.is_date_finalized = True
            self.save()
        return winning_option
    
    def get_top_voted_options(self):
        """Return the top voted options (handles ties)"""
        vote_counts = []
        for date_option in self.dateoption_set.all():
            vote_count = date_option.votes.count()
            vote_counts.append((date_option, vote_count))

        if not vote_counts:
            return []

        vote_counts.sort(key=lambda x: x[1], reverse=True)
        max_votes = vote_counts[0][1]

        tied_options = [option for option, count in vote_counts if count == max_votes]
        return tied_options


class DateOption(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    proposed_date = models.DateTimeField()
    proposed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'proposed_date']
        ordering = ['proposed_date']

    def __str__(self):
        return f"{self.event.title} - {self.proposed_date.strftime('%Y-%m-%d %H:%M')}"

    def vote_count(self):
        return self.votes.count()


class DateVote(models.Model):
    date_option = models.ForeignKey(DateOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['date_option', 'user']

    def __str__(self):
        return f"{self.user.username} voted for {self.date_option}"


class EventRequirement(models.Model):
    REQUIREMENT_TYPES = [
        ('transport', 'Transportation'),
        ('route', 'Route/Directions'),
        ('supplies', 'Supplies Needed'),
        ('food', 'Food & Drinks'),
        ('accommodation', 'Accommodation'),
        ('other', 'Other'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='requirements')
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requirements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_completed', '-created_at']

    def __str__(self):
        return f"{self.event.title} - {self.title}"


class EventComment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.event.title}"


class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    PARTICIPATION_STATUS = [
        ('interested', 'Interested'),
        ('going', 'Going'),
        ('maybe', 'Maybe'),
        ('not_going', 'Not Going'),
    ]
    status = models.CharField(max_length=20, choices=PARTICIPATION_STATUS, default='interested')

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"