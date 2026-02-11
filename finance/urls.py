from django.urls import path
from .views import (
    DashboardView, TransactionListView, TransactionCreateView, 
    TransactionUpdateView, TransactionDeleteView,
    BudgetListView, BudgetCreateView, ReportView, BankImportView,
    AnomalyDetectionView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/add/', TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),
    
    path('budgets/', BudgetListView.as_view(), name='budget_list'),
    path('budgets/add/', BudgetCreateView.as_view(), name='budget_create'),
    path('reports/', ReportView.as_view(), name='reports'),
    path('import/', BankImportView.as_view(), name='bank_import'),
    path('anomalies/', AnomalyDetectionView.as_view(), name='anomalies'),
]
