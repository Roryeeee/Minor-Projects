
from django.contrib import admin
from .models import Event, DateOption, DateVote, EventRequirement, EventComment, EventParticipant

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'required_role', 'is_date_finalized', 'created_at']
    list_filter = ['is_date_finalized', 'created_at', 'required_role']
    search_fields = ['title', 'description', 'creator__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DateOption)
class DateOptionAdmin(admin.ModelAdmin):
    list_display = ['event', 'proposed_date', 'proposed_by', 'vote_count']
    list_filter = ['proposed_date', 'created_at']
    search_fields = ['event__title']

    def vote_count(self, obj):
        return obj.votes.count()
    vote_count.short_description = 'Votes'

@admin.register(DateVote)
class DateVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_option', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'date_option__event__title']

@admin.register(EventRequirement)
class EventRequirementAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'requirement_type', 'assigned_to', 'is_completed', 'added_by']
    list_filter = ['requirement_type', 'is_completed', 'created_at']
    search_fields = ['title', 'event__title']

@admin.register(EventComment)
class EventCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'event__title', 'content']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'status', 'joined_at']
    list_filter = ['status', 'joined_at']
    search_fields = ['user__username', 'event__title']