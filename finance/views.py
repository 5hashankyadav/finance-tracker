import csv
import io
import math
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.contrib import messages
from .models import Transaction, Category, Budget
import datetime

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.date.today()
        month_start = today.replace(day=1)
        
        transactions = Transaction.objects.filter(user=self.request.user, date__gte=month_start)
        
        income = transactions.filter(category__type='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
        expenses = transactions.filter(category__type='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
        savings = income - expenses
        
        context['income'] = income
        context['expenses'] = expenses
        context['savings'] = savings
        context['recent_transactions'] = Transaction.objects.filter(user=self.request.user).order_by('-date')[:5]
        
        return context

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'finance/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'finance/transaction_form.html'
    fields = ['category', 'amount', 'description', 'date', 'currency', 'receipt']
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        from .services import check_budget_overrun
        check_budget_overrun(self.request.user, form.instance.category)
        return response

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    template_name = 'finance/transaction_form.html'
    fields = ['category', 'amount', 'description', 'date', 'currency', 'receipt']
    success_url = reverse_lazy('transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'finance/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'finance/budget_list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).order_by('-month')

class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = Budget
    template_name = 'finance/budget_form.html'
    fields = ['category', 'amount', 'month']
    success_url = reverse_lazy('budget_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Last 6 months report
        six_months_ago = datetime.date.today() - datetime.timedelta(days=180)
        
        currency = self.request.GET.get('currency', self.request.user.currency)
        context['selected_currency'] = currency
        
        monthly_data = Transaction.objects.filter(
            user=self.request.user, 
            date__gte=six_months_ago,
            currency=currency
        ).annotate(
            month=TruncMonth('date')
        ).values('month', 'category__type').annotate(
            total=Sum('amount')
        ).order_by('month')

        # Organize data for the template
        report_data = {}
        for item in monthly_data:
            m = item['month'].strftime('%b %Y')
            if m not in report_data:
                report_data[m] = {'INCOME': 0, 'EXPENSE': 0, 'SAVINGS': 0}
            report_data[m][item['category__type']] = item['total']
        
        # Calculate savings after collecting all data for the month
        for m in report_data:
            report_data[m]['SAVINGS'] = report_data[m]['INCOME'] - report_data[m]['EXPENSE']
        
        context['report_data'] = report_data
        return context

class BankImportView(LoginRequiredMixin, View):
    template_name = 'finance/import.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        csv_file = request.FILES.get('file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('bank_import')

        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        count = 0
        for row in reader:
            try:
                # Basic mapping: Date, Amount, Description, Category
                date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d').date()
                amount = float(row['Amount'])
                desc = row.get('Description', '')
                cat_name = row.get('Category', 'Other')
                
                # Auto-categorization logic (Partial)
                cat_type = 'EXPENSE' if amount < 0 else 'INCOME'
                amount = abs(amount) # Store absolute amount
                
                category, _ = Category.objects.get_or_create(
                    name=cat_name, 
                    type=cat_type, 
                    user=request.user
                )

                Transaction.objects.create(
                    user=request.user,
                    category=category,
                    amount=amount,
                    description=desc,
                    date=date
                )
                count += 1
            except Exception as e:
                print(f"Error importing row: {e}")
                continue

        messages.success(request, f'Successfully imported {count} transactions.')
        return redirect('transaction_list')

class AnomalyDetectionView(LoginRequiredMixin, ListView):
    template_name = 'finance/anomalies.html'
    context_object_name = 'anomalies'

    def get_queryset(self):
        user = self.request.user
        expenses = Transaction.objects.filter(user=user, category__type='EXPENSE')
        
        # Group by category to find average and std dev
        categories = Category.objects.filter(user=user, type='EXPENSE')
        anomalies = []
        
        for category in categories:
            cat_txs = expenses.filter(category=category)
            if cat_txs.count() < 3: # Need at least 3 transactions to detect anomaly
                continue
            
            avg = cat_txs.aggregate(models.Avg('amount'))['amount__avg']
            # Manual std dev calculation if needed, or use Avg and filter
            # Simpler: filter transactions > 2 * avg
            threshold = avg * 2
            cat_anomalies = cat_txs.filter(amount__gt=threshold)
            anomalies.extend(list(cat_anomalies))
            
        return anomalies
