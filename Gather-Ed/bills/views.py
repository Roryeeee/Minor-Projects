# Path: bills/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from eventpollapp.models import Event
from .models import Bill, Expense, Settlement, BillParticipant
from .forms import BillForm, ExpenseForm, SettlementForm, BillFilterForm
from datetime import datetime

@login_required
def bill_list(request):
    """List all bills for user's events"""
    filter_form = BillFilterForm(request.user, request.GET)
    
    # Get bills for events where user is involved
    bills = Bill.objects.filter(
        Q(event__creator=request.user) | Q(event__participants__user=request.user)
    ).distinct().select_related('event', 'created_by')
    
    # Apply filters
    if filter_form.is_valid():
        event_id = filter_form.cleaned_data.get('event')
        settlement_status = filter_form.cleaned_data.get('settlement_status')
        
        if event_id:
            bills = bills.filter(event_id=event_id)
        
        if settlement_status == 'settled':
            bills = bills.filter(is_settled=True)
        elif settlement_status == 'unsettled':
            bills = bills.filter(is_settled=False)
    
    # Calculate summary for each bill
    for bill in bills:
        bill.expense_count = bill.expenses.count()
        bill.user_balance = bill.get_split_calculation().get('balances', {}).get(request.user, 0)
    
    context = {
        'bills': bills,
        'filter_form': filter_form,
    }
    return render(request, 'bills/bill_list.html', context)

@login_required
def create_bill(request):
    """Create a new bill"""
    if request.method == 'POST':
        form = BillForm(request.user, request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.created_by = request.user
            bill.event = form.cleaned_data['event']
            bill.save()
            BillParticipant.objects.get_or_create(bill=bill, user=request.user)
            messages.success(request, f'Bill "{bill.title}" created successfully!')
            return redirect('bills:bill_detail', bill_id=bill.id)
    else:
        form = BillForm(request.user)
    
    return render(request, 'bills/create_bill.html', {'form': form})

@login_required
def bill_detail(request, bill_id):
    """View bill details with expenses and split calculation"""
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Check if user can access this bill
    can_access = (
        bill.event.creator == request.user or
        bill.event.participants.filter(user=request.user).exists() or
        bill.created_by == request.user
    )
    
    if not can_access:
        messages.error(request, "You don't have permission to view this bill.")
        return redirect('bills:bill_list')
    
    # Add user as participant if not already
    BillParticipant.objects.get_or_create(bill=bill, user=request.user)
    
    # Get split calculation
    split_data = bill.get_split_calculation()
    
    # Forms
    expense_form = ExpenseForm(bill)
    settlement_form = SettlementForm(bill, request.user)
    
    # Get user's settlements for this bill
    user_settlements = Settlement.objects.filter(
        bill=bill,
        from_user=request.user
    ).select_related('to_user')
    
    received_settlements = Settlement.objects.filter(
        bill=bill,
        to_user=request.user
    ).select_related('from_user')
    
    context = {
        'bill': bill,
        'split_data': split_data,
        'expense_form': expense_form,
        'settlement_form': settlement_form,
        'user_settlements': user_settlements,
        'received_settlements': received_settlements,
        'can_edit': bill.created_by == request.user,
    }
    
    return render(request, 'bills/bill_detail.html', context)

@login_required
def add_expense(request, bill_id):
    """Add an expense to a bill"""
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Check access
    can_access = (
        bill.event.creator == request.user or
        bill.event.participants.filter(user=request.user).exists() or
        bill.created_by == request.user
    )
    
    if not can_access:
        messages.error(request, "You don't have permission to add expenses to this bill.")
        return redirect('bills:bill_detail', bill_id=bill_id)
    
    if request.method == 'POST':
        form = ExpenseForm(bill, request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.bill = bill
            expense.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Recalculate bill total
            bill.calculate_total()
            
            messages.success(request, 'Expense added successfully!')
            return redirect('bills:bill_detail', bill_id=bill_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ExpenseForm(bill)
    
    return render(request, 'bills/add_expense.html', {'form': form, 'bill': bill})

@login_required
def edit_expense(request, expense_id):
    """Edit an existing expense"""
    expense = get_object_or_404(Expense, id=expense_id)
    bill = expense.bill
    
    # Check permissions
    can_edit = (
        expense.paid_by == request.user or
        bill.created_by == request.user or
        bill.event.creator == request.user
    )
    
    if not can_edit:
        messages.error(request, "You don't have permission to edit this expense.")
        return redirect('bills:bill_detail', bill_id=bill.id)
    
    if request.method == 'POST':
        form = ExpenseForm(bill, request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            
            # Recalculate bill total
            bill.calculate_total()
            
            messages.success(request, 'Expense updated successfully!')
            return redirect('bills:bill_detail', bill_id=bill.id)
    else:
        form = ExpenseForm(bill, instance=expense)
    
    return render(request, 'bills/edit_expense.html', {'form': form, 'expense': expense, 'bill': bill})

@login_required
@require_POST
def delete_expense(request, expense_id):
    """Delete an expense"""
    expense = get_object_or_404(Expense, id=expense_id)
    bill = expense.bill
    
    # Check permissions
    can_delete = (
        expense.paid_by == request.user or
        bill.created_by == request.user or
        bill.event.creator == request.user
    )
    
    if not can_delete:
        messages.error(request, "You don't have permission to delete this expense.")
        return redirect('bills:bill_detail', bill_id=bill.id)
    
    expense.delete()
    
    # Recalculate bill total
    bill.calculate_total()
    
    messages.success(request, 'Expense deleted successfully!')
    return redirect('bills:bill_detail', bill_id=bill.id)

@login_required
def record_settlement(request, bill_id):
    """Record a settlement payment"""
    bill = get_object_or_404(Bill, id=bill_id)
    
    if request.method == 'POST':
        form = SettlementForm(bill, request.user, request.POST)
        if form.is_valid():
            settlement = form.save(commit=False)
            settlement.bill = bill
            settlement.from_user = request.user
            settlement.save()
            
            messages.success(request, f'Settlement of ${settlement.amount} recorded. Waiting for confirmation from {settlement.to_user.username}.')
            return redirect('bills:bill_detail', bill_id=bill_id)
    
    return redirect('bills:bill_detail', bill_id=bill_id)

@login_required
@require_POST
def confirm_settlement(request, settlement_id):
    """Confirm a received settlement"""
    settlement = get_object_or_404(Settlement, id=settlement_id, to_user=request.user)
    
    if not settlement.is_confirmed:
        settlement.is_confirmed = True
        settlement.confirmed_at = datetime.now()
        settlement.save()
        
        messages.success(request, f'Settlement from {settlement.from_user.username} confirmed!')
    else:
        messages.warning(request, 'Settlement was already confirmed.')
    
    return redirect('bills:bill_detail', bill_id=settlement.bill.id)

@login_required
@require_POST
def reject_settlement(request, settlement_id):
    """Reject a received settlement"""
    settlement = get_object_or_404(Settlement, id=settlement_id, to_user=request.user)
    
    if not settlement.is_confirmed:
        settlement.delete()
        messages.info(request, f'Settlement from {settlement.from_user.username} rejected.')
    else:
        messages.warning(request, 'Cannot reject a confirmed settlement.')
    
    return redirect('bills:bill_detail', bill_id=settlement.bill.id)

@login_required
@require_POST
def toggle_bill_settlement(request, bill_id):
    """Toggle bill settlement status"""
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Only bill creator can mark as settled
    if bill.created_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    bill.is_settled = not bill.is_settled
    bill.save()
    
    status_text = "settled" if bill.is_settled else "unsettled"
    messages.success(request, f'Bill marked as {status_text}!')
    
    return JsonResponse({'is_settled': bill.is_settled})

@login_required
def user_summary(request):
    """Show user's overall financial summary across all bills"""
    # Get all bills user is involved in
    user_bills = Bill.objects.filter(
        Q(event__creator=request.user) | 
        Q(event__participants__user=request.user) |
        Q(participants__user=request.user)
    ).distinct()

    summary_data = {
        'total_bills': user_bills.count(),
        'settled_bills': user_bills.filter(is_settled=True).count(),
        'unsettled_bills': user_bills.filter(is_settled=False).count(),
        'total_owed_to_user': 0,
        'total_user_owes': 0,
        'bills_breakdown': [],
    }

    for bill in user_bills:
        split_data = bill.get_split_calculation()
        user_balance = split_data.get('balances', {}).get(request.user, 0)

        bill_info = {
            'bill': bill,
            'balance': user_balance,
            'total_amount': bill.total_amount,
        }
        summary_data['bills_breakdown'].append(bill_info)

        # ✅ Only count unsettled bills in totals
        if not bill.is_settled:
            if user_balance > 0:
                summary_data['total_owed_to_user'] += user_balance
            elif user_balance < 0:
                summary_data['total_user_owes'] += abs(user_balance)

    context = {
        'summary_data': summary_data,
    }
    return render(request, 'bills/user_summary.html', context)