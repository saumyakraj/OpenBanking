from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser
#to store data as form obj, and not as string(optional)
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
# from .managers import CustomUserManager, BaseUserManager
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin #optional -> to be used for AbstractBaseUser

import random

#For customer id
import random
from datetime import datetime
import shortuuid

from django.contrib.auth.base_user import BaseUserManager

#For Login
from rest_framework_simplejwt.tokens import RefreshToken

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, username, email, name, user_type, password=None, password2=None):
        """
        Create and save a User with the given email and password.
        """
        if username is None:
            raise TypeError('Users should have a username')

        if email is None:
            raise TypeError('Users should have a Email')

        if name is None:
            raise TypeError('Users should have a name')

        if user_type is None:
            raise TypeError('Users should have a user_type')

        # if phone is None:
        #     raise TypeError('Users should have a phone_number')

        
        email = self.normalize_email(email)       
        #lowercasing the domain part of email to prevent multiple signups
        user = self.model(username = username,email=email, name = name, user_type = user_type)           #self.normalize_email(email).lower 
        
        #set password for hashing of password
        user.set_password(password)
        user.save()

        if user_type == "CUSTOMER":
            user.admin_approved = True
            user.save()
        return user

    def create_superuser(self, username,email, password=None):
        """
        Create and save a SuperUser with the given email and password.
        """
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
        return user
class LowercaseEmailField(models.EmailField):
    """
    Override EmailField to convert emails to lowercase before saving.
    """
    def to_python(self, value):
        """
        Convert email to lowercase.
        """
        value = super(LowercaseEmailField, self).to_python(value)
        # Value can be None so check that it's a string before lowercasing.
        if isinstance(value, str):
            return value.lower()
        return value

class CustomUser(AbstractBaseUser, PermissionsMixin):
  USER_TYPES = [
        ('CUSTOMER', 'CUSTOMER'),
        ('ORG_ADMIN', 'ORG_ADMIN'),
        ('DEVELOPER', 'DEVELOPER'),
        ('FINTRACT_ADMIN', 'FINTRACT_ADMIN'),
    ]
  user_type = models.CharField(choices=USER_TYPES, max_length=20, default='CUSTOMER')
  username = models.CharField(max_length=255, unique=True)
  email = LowercaseEmailField(_('email address'), unique=True)
  #phone = models.CharField(max_length=20,unique=True)

#   phone_regex = RegexValidator(
#         regex=r'^(?:\s+|)((0|(?:(\+|)91))(?:\s|-)*(?:(?:\d(?:\s|-)*\d{9})|(?:\d{2}(?:\s|-)*\d{8})|(?:\d{3}(?:\s|-)*\d{7}))|\d{10})(?:\s+|)', 
#         message=("Phone Number is not valid"))
#   phone = models.CharField(max_length=14, unique=True, validators=[phone_regex] )

  customer_id = models.CharField(
      max_length=60,default = datetime.now().strftime('%y%m%d%f') + str(random.randint(1000,9999)))

  name = models.CharField(max_length=255,null=True, default="")
  is_staff = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)
  is_verified = models.BooleanField(default=False)
  admin_approved = models.BooleanField(default=False)
  

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  otp = models.CharField(max_length=255,default=0)
  otp_time=models.DateTimeField(auto_now=False,null=False, blank=False,auto_now_add=True)

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['username']

  objects = CustomUserManager()


  def __str__(self):
    return self.email
  

  def tokens(self):
      refresh = RefreshToken.for_user(self)
      return {
          'refresh':str(refresh),
          'access':str(refresh.access_token)
      }
