from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    currency = models.CharField(max_length=3, default='USD')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.username

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        from finance.models import Category
        # Income Categories
        income_categories = ['Salary', 'Freelance', 'Investments', 'Other Income']
        for cat in income_categories:
            Category.objects.get_or_create(name=cat, type='INCOME', user=instance)
        
        # Expense Categories
        expense_categories = ['Food', 'Rent', 'Utilities', 'Transportation', 'Entertainment', 'Shopping', 'Health', 'Other Expenses']
        for cat in expense_categories:
            Category.objects.get_or_create(name=cat, type='EXPENSE', user=instance)
