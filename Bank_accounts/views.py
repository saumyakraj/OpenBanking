from django.db.models.query import QuerySet
from accounts.models import CustomUser
from django.shortcuts import render
from rest_framework import serializers, generics, status
from .serializers import AccountSerialzer, BankTransferSerialzer, AddBeneficiary, BankSerializer, Verify_BankSerializer, BankBranchSerialzer
# Using Generic Classes to update endpoints
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView, ListAPIView
from rest_framework import permissions
from .models import Bank_Accounts, Bank_Transaction, Account_Data, Banks, Bank_Branch
from rest_framework.response import Response
# For checking owner
from .permissions import IsOwner, IsUser
# Create your views here.
from .models import Account_Data
from .renderers import UserRender
from django.http import JsonResponse
from django.core.validators import RegexValidator
import re

import random
from datetime import datetime

# class AccountsList(ListCreateAPIView):
#     serializer_class = AccountSerialzer
#     renderer_classes = (UserRender,)
#     # For  Authentications
#     permission_classes = (permissions.IsAuthenticated,)

#     # QuerySet to find user object
#     queryset = Bank_Accounts.objects.all()

#     # Overide a method, to link logged in user with owner

#     def perform_create(self, serializer):

#         model = serializer.save(owner=self.request.user)
#         data = self.request.data

#         try:
#             check = Account_Data.objects.get(Account_no=data['Account_no'])
#         except Account_Data.DoesNotExist:

#             copy = Account_Data(Account_no=model.Account_no,
#                                 balance=model.balance)

#             copy.save()
#         else:
#             check = Account_Data.objects.get(Account_no=data['Account_no'])
#             model = serializer.save(
#                 owner=self.request.user, balance=check.balance)
#             print(check.balance)
#         return model
# 
    # def get_queryset(self):
    #     return self.queryset.filter(owner=self.request.user)

# class AccountDetailsList(RetrieveUpdateDestroyAPIView):
#     serializer_class = AccountSerialzer

#     # For  Authentications
#     permission_classes = (permissions.IsAuthenticated, IsOwner,)
#     lookup_field = 'id'
#     # lookup_value_regex = "[^/]+"
#     # lookup_url_kwarg = 'Account_no'

#     # QuerySet to find user object
#     queryset = Bank_Accounts.objects.all()

#     # Overide a method, to link logged in user with owner

#     def perform_create(self, serializer):
#         return serializer.save(owner=self.request.user)

#     def get_queryset(self):
#         return self.queryset.filter(owner=self.request.user)

class Bank(generics.GenericAPIView):
    serializer_class = BankSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        # context = {"msg": "X"}
        if (user.user_type != "ORG_ADMIN"):
            context = {"msg": "This user is not an organization admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.admin_approved):
            context = {"msg": "This organization admin has not been admin_approved, contact fintract admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        if not (user.is_verified):
            context = {"msg": "This organization admin has not been email verified "}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        queryset = Banks.objects.all()
        banks = []
        for x in queryset:
            y = {
                "Bank Name": x.name,
                "Bank Main Address": x.main_address,
                "Admin Verified": x.is_verified,
            }
            banks.append(y)
        return Response(banks, status=status.HTTP_200_OK)


    def post(self, request):
        user = self.request.user
        # context = {"msg": "X"}
        if (user.user_type != "ORG_ADMIN"):
            context = {"msg": "This user is not an organization admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.admin_approved):
            context = {"msg": "This organization admin has not been admin_approved, contact fintract admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.is_verified):
            context = {"msg": "This organization admin has not been email verified "}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
            
        name = request.data['name']
        main_address = request.data['main_address']

        a = Banks.objects.filter(name = name)
        if len(a):
            context = {"msg": "This bank name already exists"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        id = datetime.now().strftime('%y%m%d%f') + str(random.randint(1000,9999))
        bank1 = Banks(name = name, main_address = main_address, bank_id= id, is_verified = False)
        bank1.save()
        context = {"msg": "Bank added successfully"}
        return Response(context, status=status.HTTP_201_CREATED)


class Verify_Bank(generics.GenericAPIView):
    serializer_class = Verify_BankSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        if (user.user_type != "FINTRACT_ADMIN"):
            context = {"msg": "This user is not an FINTRACT admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.admin_approved):
            context = {"msg": "This FINTRACT admin has not been admin_approved, contact fintract admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.is_verified):
            context = {"msg": "This FINTRACT admin has not been email verified "}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        name = request.data['name']
        a = Banks.objects.filter(name = name)
        if not len(a):
            context = {"msg": "This bank doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if (len(a)>1):
            context = {"msg": "Multiple banks have the same name, contact admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        bank = a[0]
        if(bank.is_verified):
            context = {"msg": "This bank is already verified"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        else:
            bank.is_verified = True
            bank.save()
            context = {"msg": "Bank verified"}
            return Response(context, status=status.HTTP_201_CREATED)

class Bank_branch(generics.GenericAPIView):
    serializer_class = BankBranchSerialzer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        if (user.user_type != "ORG_ADMIN"):
            context = {"msg": "This user is not an organization admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.admin_approved):
            context = {"msg": "This organization admin has not been admin_approved, contact fintract admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        if not (user.is_verified):
            context = {"msg": "This organization admin has not been email verified "}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        queryset = Bank_Branch.objects.all()
        banks = []
        for x in queryset:
            y = {
                "Bank Name": x.bank_name.name,
                "Branch Name": x.name,
                "Branch ID": x.branch_id,
                "IFSC": x.ifsc,
                "Branch Address": x.branch_address,
            }
            banks.append(y)
        return Response(banks, status=status.HTTP_200_OK)


    def post(self, request):
        user = self.request.user
        if (user.user_type != "ORG_ADMIN"):
            context = {"msg": "This user is not an organization admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.admin_approved):
            context = {"msg": "This organization admin has not been admin_approved, contact fintract admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.is_verified):
            context = {"msg": "This organization admin has not been email verified "}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
            
        name = request.data['name']
        branch_address = request.data['branch_address']
        ifsc = request.data['ifsc']
        parent_bank = request.data['parent_bank']

        pattern =r'[A-Z]{4}[0-9]{6}'

        if not re.fullmatch(pattern, ifsc):
            context = {"msg": "This ifsc code is not valid"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        a = Banks.objects.filter(name = parent_bank)
        if not len(a):
            context = {"msg": "This bank doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        bank = a[0]
        queryset = Bank_Branch.objects.filter(ifsc = ifsc)
        if len(queryset):
            context = {"msg": "Another bank branch has this ifsc"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        id = datetime.now().strftime('%y%m%d%f') + str(random.randint(1000,9999))
        bank1 = Bank_Branch(name = name, branch_address = branch_address, branch_id= id ,ifsc = ifsc, bank_name = bank)
        bank1.save()
        context = {"msg": "Bank branch added successfully"}
        return Response(context, status=status.HTTP_201_CREATED)
        

class AccountsList(GenericAPIView):
    serializer_class = AccountSerialzer
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        user = self.request.user
        queryset = Bank_Accounts.objects.filter(owner = user)
        accounts = []
        for x in queryset:
            accounts.append({"Account_Holder_Fname": x.Account_Holder_Fname, "Account_Holder_Mname": x.Account_Holder_Mname, "Account_Holder_Lname": x.Account_Holder_Lname,"Account_no": x.Account_no, 
            "Bank": x.bank_branch.bank_name.name, "Bank_Branch":x.bank_branch.name, "account_type": x.account_type, "id": x.id, "category": x.category, "balance": x.balance, "active": x.active, "on_profile": x.on_profile})
        return Response(accounts, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = self.request.user
        if (user.user_type != "ORG_ADMIN"):
            context = {"msg": "This user is not an organization admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.admin_approved):
            context = {"msg": "This organization admin has not been admin_approved, contact an approved fintract admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.is_verified):
            context = {"msg": "This organization admin has not been email verified "}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        customer_id = request.data['customer_id']
        Fname = request.data['Account_Holder_Fname']
        Mname = request.data['Account_Holder_Mname']
        Lname = request.data['Account_Holder_Lname']
        Account_no = request.data['Account_no']
        account_type = request.data['account_type']
        category = request.data['category']
        branch_id1 = request.data['parent_bank_branch_id']
        if not branch_id1.isdecimal():
            context = {"msg": "Invalid Branch ID"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        branch_id = int(branch_id1)
        CATEGORY_OPTIONS = ['UK','India']
        ACCOUNT_TYPE = [
        'CURRENT','SAVINGS','PENSION','LOAN','MORTGAGE', 'PENSION']

        customers = CustomUser.objects.filter(customer_id = customer_id)
        if not len(customers):
            context = {"msg": "Requested user doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        bank_customer = CustomUser.objects.get(customer_id = customer_id)

        if (Fname == ""):
            context = {"msg": "First name cannot be empty"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if (Lname == ""):
            context = {"msg": "Last name cannot be empty"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        query2 = Bank_Accounts.objects.filter(Account_no = Account_no)
        if len(query2):
            context = {"msg": "This account already exists"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        # account_no_regex = RegexValidator(
        # regex=r'[0-9]{9,18}', message=("Account Number is not valid"))
        pattern =r'[0-9]{9,18}'

        if not re.fullmatch(pattern, Account_no):
            context = {"msg": "This account number is not valid"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        ok_account_type = False
        ok_category = False
        for x in ACCOUNT_TYPE:
            if x == account_type:
                ok_account_type = True
        for x in CATEGORY_OPTIONS:
            if x == category:
                ok_category = True
        if not ok_account_type:
            context = {"msg": "This account type is not valid"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not ok_category:
            context = {"msg": "This category type is not valid"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Bank_Branch.objects.filter(branch_id = branch_id)
        if not len(queryset):
            context = {"msg": "This bank branch doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if len(queryset)>1:
            context = {"msg": "There are multiple bank branches with this branch id which is not allowed, contact admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        branch = queryset[0]
        if not branch.bank_name.is_verified:
            context = {"msg": "This bank has not been verified by the admin yet"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account1 = Bank_Accounts(Account_Holder_Fname = Fname, Account_Holder_Mname = Mname, Account_Holder_Lname = Lname, 
        Account_no = Account_no, account_type = account_type, category = category, bank_branch = branch, owner = bank_customer, active = True, on_profile = False)
        account1.save()

        context = {"msg": "Bank account added successfully"}
        return Response(context, status=status.HTTP_201_CREATED)

class AccountDetailsList(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, id):
        user = self.request.user

        queryset = Bank_Accounts.objects.filter(owner = user, id = id)
        if not len(queryset):
            context = {"msg": "This bankaccount doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        x = queryset[0]
        if not x.bank_branch.bank_name.is_verified:
            context = {"msg": "Bank not verified, contact admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        accounts = []
        accounts.append({"Account_Holder_Fname": x.Account_Holder_Fname, "Account_Holder_Mname": x.Account_Holder_Mname, "Account_Holder_Lname": x.Account_Holder_Lname, "Account_no": x.Account_no,
         "Bank": x.bank_branch.bank_name.name, "Bank_Branch":x.bank_branch.name, "account_type": x.account_type, "id": x.id, "category": x.category, "balance": x.balance, "active": x.active, "on_profile": x.on_profile})
            
        return Response(accounts, status=status.HTTP_200_OK)

    def delete(self, request, id):
        user = self.request.user

        queryset = Bank_Accounts.objects.filter(owner = user, id = id)
        if not len(queryset):
            context = {"msg": "This bankaccount doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        x = queryset[0]
        if not x.bank_branch.bank_name.is_verified:
            context = {"msg": "Bank not verified, contact admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        x.delete()
        context = {"msg": "Bank account deleted successfully"}
        return Response(context, status=status.HTTP_201_CREATED)
        

class Beneficiary(generics.GenericAPIView):    
    
    serializer_class = AddBeneficiary
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        queryset =  user.beneficiary.all()
        accounts = []
        for x in queryset:
            bank_account = {
                "Account No": x.Account_no ,
                "Account_Holder_Fname": x.Account_Holder_Fname ,
                "Account_Holder_Mname": x.Account_Holder_Mname ,
                "Account_Holder_Lname": x.Account_Holder_Lname ,
                "Account type": x.account_type ,
                "Category": x.category ,
            }
            accounts.append(bank_account)
        return Response(accounts, status=status.HTTP_200_OK)

    def post(self, request):
        user = self.request.user
        data = request.data['Account_no']
        if (data == ""):
            context = {"msg": "This cannot be empty"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        queryset =  user.beneficiary.all()
        for x in queryset:
            y = x.Account_no
            if (data == y):
                context = {"msg": "You already have this beneficiary"}
                return Response(context, status=status.HTTP_400_BAD_REQUEST)

        queryset = Bank_Accounts.objects.all().filter(Account_no = data)
        if not len(queryset):
            context = {"msg": "This Bank Account does not exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        account = queryset[0]
        if not account.active:
            context = {"msg": "Beneficiary account is not active(suspended)"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        account.beneficiary_users.add(user)
        context = {"msg": "Beneficiary successfully added"}
        return Response(context, status=status.HTTP_200_OK)

    def patch(self, request):
        user = self.request.user
        data = request.data['Account_no']
        # context = {"msg": "X"}

        if (data == ""):
            context = {"msg": "This cannot be empty"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        queryset = Bank_Accounts.objects.all().filter(Account_no = data)
        if not len(queryset):
            context = {"msg": "This Bank Account does not exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        queryset2 =  user.beneficiary.all()
        ok = False
        for x in queryset2:
            y = x.Account_no
            if (data == y):
                ok = True
                
        if not ok:
            context = {"msg": "This Beneficiary doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        account = queryset[0]
        account.beneficiary_users.remove(user)
        context = {"msg": "Beneficiary successfully removed"}
        return Response(context, status=status.HTTP_200_OK)


class BankTransfer(GenericAPIView):
    renderer_classes = (UserRender,)
    serializer_class = BankTransferSerialzer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def post(self, request):

        user = self.request.user  # making authentication using jwt
        # print(request.data)
        data = request.data
        your_account_no = data['account']     # your account to transfer funds
        to_account_no = data['to_account_no']               # reciver account no
        # holder = data['to_account_holder']                       #reciver holder name
        # ifsc = data['to_account_ifsc']                          # reciver account ifsc
        amount = data['amount_send']                       # amount to tranfer
        transfer_type = data['transfer_type']
        # print(your_account_no)

        ####################

        if(amount <= 0):
            return Response({'error': 'Please Enter a valid amount'})

        if(your_account_no == to_account_no):
            return Response({'error':
                             'Cannot Send Self Transfer to same account '})

        if(transfer_type == ""):
            return Response({'error':
                            'Transfer Type is empty'})

        if(transfer_type != "Food" and transfer_type != "Electricity" and transfer_type != "P2P" and transfer_type != "self"):
            return Response({'error':
                             'Invalid Transfer Type'})

        ####################

        try:
            account = Bank_Accounts.objects.get(
                Account_no=your_account_no)  # matching user and his account in Bank_Accounts
        except:
            return Response({'error':
                             'Sender Account Not Found'})

        # try:
        #     account_1 = Account_Data.objects.get(Account_no=your_account_no)
        # except:
        #     return Response({'message':
        #                      'Sender Account Not Found in Account_Data database, contact admin'}) # matching user and his account in Account_Data

        if(account.owner != user):  # verify the account belong to you or not
            return Response({'message':
                             'This sender account Doesn\'t belong to you'})

        try:
            acc = Bank_Accounts.objects.get(Account_no=to_account_no)
        except:
            return Response({'error':
                             'Reciever account Not Found'})
        # try:
        #     acc2 = Account_Data.objects.get(Account_no=to_account_no)
        # except:
        #     return Response({'error':
        #                      'Reciever account Not Found in Account_Data database, contact admin'})
        
        intra_transfer = False
        if(acc.owner == user):
            intra_transfer = True

        # print(intra_transfer)
        # print(user.id)
        # print(acc.owner.id)

        ####################

        if(intra_transfer):
            if(transfer_type!="self"):
                return Response({'error':
                             'Both accouts belong to same user but transfer type is not self'})
        
        if(not intra_transfer):
            if(transfer_type=="self"):
                return Response({'error':
                             'Both accouts do not belong to same user but transfer type is self'})
        ####################
        account_from = Bank_Accounts.objects.get(Account_no=your_account_no)
        account_to = Bank_Accounts.objects.get(Account_no=to_account_no)

        if not account_from.active:
            context = {"msg": "Your Account is not active (suspended)"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        if not account_to.active:
            context = {"msg": "Reciever Account is not active (suspended)"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        ####################

        try:
            account_to = Bank_Accounts.objects.get(Account_no=to_account_no)  # matching user and his account
            # account_to_1 = Account_Data.objects.get(Account_no=to_account_no)
            inter = True
            print("to Address matched in db")
        except:
            inter = False

        acc_no = str(account).split()[0]

        # checking for sufficent balance
        # print(account)
        if(account.balance < amount):
            transaction = Bank_Transaction(user=user, account=acc_no,
                                           to_account_no=to_account_no, amount_send=amount, transfer_type=transfer_type,
                                           status='Failed')
            transaction.save()
            return Response({'message':
                             'Insufficient Balance'})

        # reducing this balance after tranfer
        account.balance -= amount
        # account_1.balance -= amount
        # account_1.save()
        account.save()
        if(inter):
            # account_to_1.balance += amount
            # account_to_1.save()
            account_to.balance += amount
            account_to.save()

         ######################################################################
         # Saving transaction

        transaction = Bank_Transaction(user=user, account=acc_no,
                                       to_account_no=to_account_no, amount_send=amount, transfer_type=transfer_type,
                                       status='Sent')
        transaction.save()

        use2 = Bank_Accounts.objects.get(Account_no=to_account_no)
        try:
            user2 = CustomUser.objects.get(id=use2.owner_id)
        except:
            return Response({'error':
                             'Beneficiary account user Not Found'})

        print(use2.owner_id)

        transaction1 = Bank_Transaction(user=user2, account=acc_no,  # Saving transaction
                                        to_account_no=to_account_no, amount_send=amount, transfer_type=transfer_type,
                                        status='Received')
        transaction1.save()

        ########################################################################

        return Response({'message': 'Amount Transferd Successfully'})

class TransactionList(ListAPIView):

    serializer_class = BankTransferSerialzer

    permission_classes = (permissions.IsAuthenticated,)

    queryset = Bank_Transaction.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ProfileList(GenericAPIView):
    renderer_classes = (UserRender,)
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def get(self, request):
        user = self.request.user
        # data = request.data
        queryset = Bank_Transaction.objects.all()

        food_tr = queryset.filter(user=user, transfer_type='Food', status = 'Sent')
        food_ex = 0
        for item in food_tr:
            food_ex = food_ex + item.amount_send

        electricity_tr = queryset.filter(user=user, transfer_type='Electricity', status = 'Sent')
        electricity_ex = 0
        for item in electricity_tr:
            electricity_ex = electricity_ex + item.amount_send

        P2P_tr = queryset.filter(user=user, transfer_type='P2P', status = 'Sent')
        P2P_ex = 0
        for item in P2P_tr:
            P2P_ex = P2P_ex + item.amount_send

        self_tr = queryset.filter(user=user, transfer_type='self', status = 'Sent')
        self_ex = 0
        for item in self_tr:
            self_ex = self_ex + item.amount_send
        # self_ex = self_ex / 2

        net_expenditure = food_ex + electricity_ex + P2P_ex

        received_tr = queryset.filter(user = user, status = 'Received')
        received_ex = 0
        for item in received_tr:
            if(item.transfer_type!= "self"):
                received_ex += item.amount_send

        responseData = {
            'Food_Expense': food_ex,
            'Electricity_Expense': electricity_ex,
            'P2P_Transfer': P2P_ex,
            'Self_Transfer': self_ex,
            'Net_Transfer (Total excluding self transfers)' : net_expenditure,
            'Net_Received (Total received excluding self transfers)' : received_ex,
        }
        return JsonResponse(responseData)


class Activate(GenericAPIView):
    serializer_class = AddBeneficiary
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        if (user.user_type != "ORG_ADMIN"):
            context = {"msg": "This user is not an organization admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.admin_approved):
            context = {"msg": "This organization admin has not been admin_approved, contact fintract admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.is_verified):
            context = {"msg": "This organization admin has not been email verified "}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        data = request.data['Account_no']
        queryset = Bank_Accounts.objects.filter(Account_no = data)
        if not len(queryset):
            context = {"msg": "This bank account doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account = queryset[0]
        if account.active:
            context = {"msg": "This account is already active"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account.active = True
        account.save()
        context = {"msg": "Account activated"}
        return Response(context, status=status.HTTP_200_OK)

class Suspend(GenericAPIView):
    serializer_class = AddBeneficiary
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = self.request.user

        if (user.user_type != "ORG_ADMIN"):
            context = {"msg": "This user is not an organization admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.admin_approved):
            context = {"msg": "This organization admin has not been admin_approved, contact fintract admin"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        if not (user.is_verified):
            context = {"msg": "This organization admin has not been email verified "}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)

        data = request.data['Account_no']
        queryset = Bank_Accounts.objects.filter(Account_no = data)
        if not len(queryset):
            context = {"msg": "This bank account doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account = queryset[0]
        if not account.active:
            context = {"msg": "This account is already suspended"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account.active = False
        account.on_profile = False
        account.save()
        context = {"msg": "Account suspended and removed from profile"}
        return Response(context, status=status.HTTP_200_OK)

class Show_Profile(GenericAPIView):
    serializer_class = AddBeneficiary
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = self.request.user

        data = request.data['Account_no']
        queryset = Bank_Accounts.objects.filter(Account_no = data, owner = user)
        if not len(queryset):
            context = {"msg": "This bank account doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account = queryset[0]
        if account.on_profile:
            context = {"msg": "This account is already on profile"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account.on_profile = True
        account.save()
        context = {"msg": "Account displayed on profile"}
        return Response(context, status=status.HTTP_200_OK)

class Remove_Profile(GenericAPIView):
    serializer_class = AddBeneficiary
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = self.request.user

        data = request.data['Account_no']
        queryset = Bank_Accounts.objects.filter(owner = user, Account_no = data)
        if not len(queryset):
            context = {"msg": "This bank account doesn't exist"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account = queryset[0]
        if not account.on_profile:
            context = {"msg": "This account is already removed from profile"}
            return Response(context, status=status.HTTP_400_BAD_REQUEST)
        
        account.on_profile = False
        account.save()
        context = {"msg": "Account removed from profile"}
        return Response(context, status=status.HTTP_200_OK)

class Accounts_On_Profile(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        queryset = Bank_Accounts.objects.filter(owner = user)
        # if not len(queryset):
        #     context = {"msg": "This user has no accounts"}
        #     return Response(context, status=status.HTTP_400_BAD_REQUEST)
        data = []
        for x in queryset:
            if x.on_profile and x.active:
                data.append(x.Account_no)
        return Response(data, status=status.HTTP_200_OK)