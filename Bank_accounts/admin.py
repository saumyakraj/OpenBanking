from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Bank_Accounts, Bank_Transaction, Account_Data, Banks, Bank_Branch
# Register your models here.

admin.site.register(Bank_Accounts)
admin.site.register(Bank_Transaction)
# admin.site.register(Account_Data)
admin.site.register(Banks)
admin.site.register(Bank_Branch)