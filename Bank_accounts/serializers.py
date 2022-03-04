from django.db.models import fields
from django.utils.functional import empty
from rest_framework import serializers
from .models import Bank_Accounts, Bank_Transaction, Banks, Bank_Branch
from accounts.models import CustomUser


class AccountSerialzer(serializers.ModelSerializer):
  customer_id = serializers.CharField(write_only=True)
  parent_bank_branch_id = serializers.CharField(write_only=True)

  class Meta:
    model = Bank_Accounts
    
    fields = [
      'customer_id', 'Account_Holder_Fname','Account_Holder_Mname',
      'Account_Holder_Lname','Account_no','account_type','id','category','balance', 'parent_bank_branch_id']
    read_only_fields = ('id','balance',) 

class BankBranchSerialzer(serializers.ModelSerializer):
  parent_bank = serializers.CharField(write_only=True)

  class Meta:
    model = Bank_Branch
    
    fields = ['name', 'ifsc', 'branch_address','parent_bank' ]

class BankTransferSerialzer(serializers.ModelSerializer):
  

  class Meta:
    model = Bank_Transaction
    
    fields = [
     'account','to_account_no','amount_send','transfer_type','created_at','status']
    read_only_fields = ('created_at','status',)
    
    #lookup_field = 'Account_no'

class BankSerializer(serializers.ModelSerializer):

  class Meta:
    model = Banks

    fields = [
      'name', 'main_address',
    ]
  
class Verify_BankSerializer(serializers.ModelSerializer):

  class Meta:
    model = Banks

    fields = [
      'name',
    ]

class AddBeneficiary(serializers.ModelSerializer):

    class Meta:
        model = Bank_Accounts
        fields = ['Account_no']