from django.contrib import admin
from .models import Bill, Expense, Settlement, BillParticipant

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'created_by', 'total_amount', 'is_settled', 'created_at']
    list_filter = ['is_settled', 'created_at']
    search_fields = ['title', 'event__title', 'created_by__username']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'bill', 'amount', 'paid_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['description', 'bill__title', 'paid_by__username']
    filter_horizontal = ['shared_by']

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'amount', 'bill', 'is_confirmed', 'created_at']
    list_filter = ['is_confirmed', 'created_at']
    search_fields = ['from_user__username', 'to_user__username', 'bill__title']

@admin.register(BillParticipant)
class BillParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'bill', 'joined_at']
    list_filter = ['joined_at']
    search_fields = ['user__username', 'bill__title']