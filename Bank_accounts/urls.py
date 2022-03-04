from django.urls import path
from . import views

urlpatterns = [
     path('bank', views.Bank.as_view(), name = 'Bank'),
     path('verify_bank', views.Verify_Bank.as_view(), name = 'Verify_Bank'),
     path('bank_branch', views.Bank_branch.as_view(), name = 'Bank_branch'),
     path('',views.AccountsList.as_view(), name = 'Accounts'),
     path('<int:id>',views.AccountDetailsList.as_view(), name = 'AccountDetails'),
     path('beneficiary', views.Beneficiary.as_view(), name = 'Beneficiary'),
     path('transfer', views.BankTransfer.as_view(), name='Bank Transfer'),
     path('transactions',views.TransactionList.as_view(), name = 'Transactions'),
     path('transaction_report',views.ProfileList.as_view(), name = 'transaction_report'),

     path('account_activate', views.Activate.as_view(), name = 'Activate'),
     path('account_suspend', views.Suspend.as_view(), name = 'Suspend'),
     path('show_profile', views.Show_Profile.as_view(), name = 'Show_Profile'),
     path('remove_profile', views.Remove_Profile.as_view(), name = 'Remove_Profile'),
     path('accounts_on_profile', views.Accounts_On_Profile.as_view(), name = 'Accounts_On_Profile'),
]
