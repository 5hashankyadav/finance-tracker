from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from .models import Budget, Transaction
import datetime

def check_budget_overrun(user, category):
    if category.type != 'EXPENSE':
        return
    
    today = datetime.date.today()
    month_start = today.replace(day=1)
    
    budget = Budget.objects.filter(user=user, category=category, month=month_start).first()
    if not budget:
        return
    
    total_spent = Transaction.objects.filter(
        user=user, 
        category=category, 
        date__gte=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    if total_spent > budget.amount:
        # Send notification
        subject = f'Budget Alert: {category.name}'
        message = f'You have exceeded your budget for {category.name}. \nBudget: {budget.amount} \nSpent: {total_spent}'
        recipient_list = [user.email]
        
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
            print(f"Notification sent to {user.email}")
        except Exception as e:
            print(f"Error sending email: {e}")
