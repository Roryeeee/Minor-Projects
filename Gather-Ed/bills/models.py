from django.db import models
from django.contrib.auth.models import User
from eventpollapp.models import Event
from decimal import Decimal
from collections import defaultdict

class Bill(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bills')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_settled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event.title} - {self.title}"

    def calculate_total(self):
        """Calculate total amount from all expenses"""
        total = sum(expense.amount for expense in self.expenses.all())
        self.total_amount = total
        self.save()
        return total

    def get_split_calculation(self):
        """Calculate who owes whom and how much"""
        expenses = self.expenses.all()
        participants = set()
        
        # Collect all participants
        for expense in expenses:
            participants.add(expense.paid_by)
            participants.update(expense.shared_by.all())
        
        if not participants:
            return {}
        
        # Calculate total expenses per person
        person_expenses = defaultdict(Decimal)
        person_payments = defaultdict(Decimal)
        
        for expense in expenses:
            # Add to what this person paid
            person_payments[expense.paid_by] += expense.amount
            
            # Calculate how much each person should pay
            shared_by_count = expense.shared_by.count()
            if shared_by_count > 0:
                amount_per_person = expense.amount / shared_by_count
                for person in expense.shared_by.all():
                    person_expenses[person] += amount_per_person
        
        # Calculate net balances (positive = owed money, negative = owes money)
        balances = {}
        for person in participants:
            balances[person] = person_payments[person] - person_expenses[person]
        
        # Calculate settlements (who pays whom)
        settlements = []
        debtors = [(person, -balance) for person, balance in balances.items() if balance < 0]
        creditors = [(person, balance) for person, balance in balances.items() if balance > 0]
        
        debtors.sort(key=lambda x: x[1], reverse=True)  # Largest debts first
        creditors.sort(key=lambda x: x[1], reverse=True)  # Largest credits first
        
        i = j = 0
        while i < len(debtors) and j < len(creditors):
            debtor, debt = debtors[i]
            creditor, credit = creditors[j]
            
            settlement_amount = min(debt, credit)
            if settlement_amount > 0.01:  # Avoid tiny settlements
                settlements.append({
                    'from_user': debtor,
                    'to_user': creditor,
                    'amount': round(settlement_amount, 2)
                })
            
            debtors[i] = (debtor, debt - settlement_amount)
            creditors[j] = (creditor, credit - settlement_amount)
            
            if debtors[i][1] <= 0.01:
                i += 1
            if creditors[j][1] <= 0.01:
                j += 1
        
        return {
            'balances': {person: round(balance, 2) for person, balance in balances.items()},
            'settlements': settlements,
            'total_amount': self.total_amount
        }


class Expense(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')
    shared_by = models.ManyToManyField(User, related_name='shared_expenses')
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.description} - ${self.amount}"

    def amount_per_person(self):
        """Calculate amount per person for this expense"""
        shared_count = self.shared_by.count()
        if shared_count == 0:
            return 0
        return self.amount / shared_count


class Settlement(models.Model):
    """Track actual settlements/payments between users"""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='settlements')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='settlements_made')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='settlements_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "✓" if self.is_confirmed else "⏳"
        return f"{status} {self.from_user.username} → {self.to_user.username}: ${self.amount}"


class BillParticipant(models.Model):
    """Track who is involved in a bill"""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['bill', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.bill.title}"