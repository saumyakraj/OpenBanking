from django.db import models
# from django.db.models.deletion import CASCADE
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime
from accounts.models import CustomUser
# Create your models here.
import random

class Banks(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=122, blank= False)
    main_address = models.TextField(blank=False)
    bank_id = models.BigIntegerField(default = datetime.now().strftime('%y%m%d%f') + str(random.randint(1000,9999)), unique = False, primary_key=True,)
    is_verified = models.BooleanField(default=False )

    def __str__(self):
        return self.name

class Bank_Branch(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=122, blank= False)
    ifsc = models.CharField(max_length=10, blank=False)
    branch_id = models.BigIntegerField(default = datetime.now().strftime('%y%m%d%f') + str(random.randint(1000,9999)), unique = False, primary_key=True)
    branch_address = models.TextField(blank=False)
    # is_verified = models.BooleanField(default=False )
    bank_name = models.ForeignKey(to=Banks, on_delete=models.CASCADE)

    def __str__(self):
        return self.ifsc+" "+self.name

class Bank_Accounts(models.Model):

    CATEGORY_OPTIONS = [
        ('UK', 'UK'),
        ('India', 'India')
    ]
    ACCOUNT_TYPE = [
        ('CURRENT', 'CURRENT'),
        ('SAVINGS', 'SAVINGS'),
        ('PENSION', 'PENSION'),
        ('LOAN', 'LOAN'),
        ('MORTGAGE', 'MORTGAGE'),
        ('PENSION', 'PENSION')
    ]

    account_type = models.CharField(choices=ACCOUNT_TYPE, max_length=20, default='CURRENT')
    category = models.CharField(choices=CATEGORY_OPTIONS, max_length=10)
    Account_Holder_Fname = models.CharField(max_length=100, blank=False)
    Account_Holder_Mname = models.CharField(max_length=100, blank=True)
    Account_Holder_Lname = models.CharField(max_length=100, blank=False)
    # phone_regex = RegexValidator(
    #     regex=r'^(?:\s+|)((0|(?:(\+|)91))(?:\s|-)*(?:(?:\d(?:\s|-)*\d{9})|(?:\d{2}(?:\s|-)*\d{8})|(?:\d{3}(?:\s|-)*\d{7}))|\d{10})(?:\s+|)',
    #     message=("Phone Number is not valid"))
    #phone = models.CharField(max_length=14, blank=False, validators=[phone_regex] )
    account_no_regex = RegexValidator(
        regex=r'[0-9]{9,18}', message=("Account Number is not valid"))

    Account_no = models.CharField(max_length=18, blank=False, validators=[
                                  account_no_regex], unique=True)

    # phone_regex = RegexValidator(
    # regex=r'^(?:\s+|)((0|(?:(\+|)91))(?:\s|-)*(?:(?:\d(?:\s|-)*\d{9})|(?:\d{2}(?:\s|-)*\d{8})|(?:\d{3}(?:\s|-)*\d{7}))|\d{10})(?:\s+|)', message=("Phone Number is not valid"))
    #phone = models.CharField(max_length=14, blank=False )
    owner = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    bank_branch = models.ForeignKey(to=Bank_Branch, related_name='BANK_BRANCH', on_delete= models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    balance = models.IntegerField(default=random.randint(1000, 9999), )

    beneficiary_users = models.ManyToManyField(CustomUser, related_name='beneficiary', blank= True) 

    active = models.BooleanField(default=True,)
    on_profile = models.BooleanField(default=False,)

    # date = models.DateField()

    def __str__(self):
        return self.Account_no+" "+str(self.id)


class Bank_Transaction(models.Model):

    CATEGORY_OPTIONS = [
        ('Sent', 'Successfully transfered'),
        ('Received', 'Received Successfully'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed')
    ]

    TRANSACTION_TYPES = [
        ('P2P', 'P2P'),
        ('Food', 'Food transaction'),
        ('Electricity', 'Electricity transaction'),
        ('self', 'self'),
    ]

    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    #account = models.ForeignKey(to=Bank_Accounts, on_delete=models.CASCADE)
    account = models.CharField(max_length=18, blank=False)
    to_account_no = models.CharField(max_length=18, blank=False)
    # to_account_holder = models.CharField(max_length=32, blank=False)
    # to_account_ifsc = models.CharField(max_length=32, blank=False)
    amount_send = models.IntegerField(blank=False)
    transfer_type = models.CharField(
         choices=TRANSACTION_TYPES, max_length=20, default='P2P')
    
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(choices=CATEGORY_OPTIONS, max_length=10,
                              default='Pending')

    def __str__(self):
        return str(self.id)


class Account_Data(models.Model):
    Account_no = models.CharField(max_length=18, blank=False)
    balance = models.IntegerField(blank=False)

    def __str__(self):
        return "Account No: "+str(self.Account_no) + " Balance: "+str(self.balance)
