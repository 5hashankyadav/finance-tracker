import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User
from finance.models import Category, Transaction, Budget

def seed():
    # 1. Get/Create Admin User
    admin, created = User.objects.get_or_create(username='admin')
    if created:
        admin.set_password('admin123')
        admin.email = 'admin@example.com'
        admin.save()
        print("Created admin user.")
    else:
        print("Admin user already exists.")

    # 2. Get Categories (Should be created via signal, but let's be sure)
    income_cats = list(Category.objects.filter(user=admin, type='INCOME'))
    expense_cats = list(Category.objects.filter(user=admin, type='EXPENSE'))

    if not income_cats or not expense_cats:
        # Manually trigger signal logic if somehow missed
        from users.models import create_default_categories
        create_default_categories(User, admin, True)
        income_cats = list(Category.objects.filter(user=admin, type='INCOME'))
        expense_cats = list(Category.objects.filter(user=admin, type='EXPENSE'))

    print(f"Found {len(income_cats)} income and {len(expense_cats)} expense categories.")

    # 3. Create Transactions for last 60 days
    today = datetime.date.today()
    tx_count = 0
    
    # 3.1 Income
    for i in range(2): # 2 salaries
        Transaction.objects.get_or_create(
            user=admin,
            category=random.choice(income_cats),
            amount=5000.00,
            description=f"Monthly Salary {i+1}",
            date=today - datetime.timedelta(days=i*30 + 5)
        )
        tx_count += 1

    # 3.2 Random Expenses
    descriptions = {
        'Food': ['Grocery Shopping', 'Dinner at Italian Place', 'Starbucks Coffee', 'Lunch with team'],
        'Rent': ['Monthly Rent Payment'],
        'Utilities': ['Electricity Bill', 'Water Bill', 'Internet Subscription'],
        'Transportation': ['Uber ride', 'Gas refill', 'Metro card recharge'],
        'Entertainment': ['Netflix Subscription', 'Movie Tickets', 'Gaming Console Skins'],
        'Shopping': ['Amazon Electronics', 'New T-shirt', 'Sneakers'],
        'Health': ['Pharmacy - Vitamins', 'Gym Membership'],
    }

    for d in range(60):
        date = today - datetime.timedelta(days=d)
        # 1-3 transactions per day
        for _ in range(random.randint(1, 3)):
            cat = random.choice(expense_cats)
            desc_list = descriptions.get(cat.name, [f"Spent at {cat.name}"])
            Transaction.objects.create(
                user=admin,
                category=cat,
                amount=round(random.uniform(10.0, 150.0), 2),
                description=random.choice(desc_list),
                date=date
            )
            tx_count += 1

    print(f"Created {tx_count} transactions.")

    # 4. Create Budgets for this month
    month_start = today.replace(day=1)
    budgets_created = 0
    for cat in expense_cats[:4]:
        Budget.objects.get_or_create(
            user=admin,
            category=cat,
            amount=random.choice([500.00, 1000.00, 1500.00]),
            month=month_start
        )
        budgets_created += 1
    
    print(f"Created {budgets_created} budgets for {month_start.strftime('%B %Y')}.")

if __name__ == "__main__":
    seed()
