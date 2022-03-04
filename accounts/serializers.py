from rest_framework import serializers
from .models import CustomUser
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.validators import RegexValidator
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
# from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    # phone_regex = RegexValidator( regex=r'^(?:\s+|)((0|(?:(\+|)91))(?:\s|-)*(?:(?:\d(?:\s|-)*\d{9})|(?:\d{2}(?:\s|-)*\d{8})|(?:\d{3}(?:\s|-)*\d{7}))|\d{10})(?:\s+|)', 
    # )
    # phone = serializers.CharField(max_length=14, validators=[phone_regex] )
    
    

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'
        }

    class Meta:
        model = CustomUser
        fields = ('id','email', 'username', 'name', 'user_type', 'password', 'password2',)
        read_only_fields = ('id',)
        #extra_kwargs = {"phone": {"error_messages": {"required": "Phone Number already exists"}}}

    

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        #phone = attrs.get('phone', '')
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        
        name = attrs.get('name', '')
        user_type = attrs.get('user_type', '')
        # country=attrs.get('country','')


        Allowed_users = ['CUSTOMER', 'ORG_ADMIN','DEVELOPER','FINTRACT_ADMIN']
        ok = False
        for x in Allowed_users:
            if x == user_type:
                ok = True

        if not ok:
            raise serializers.ValidationError("User type not allowed")

        if user_type == "ORG_ADMIN":
            ok = True
            if "@gmail.com" in email:
                ok = False  
            elif "@rediff.com" in email:
                ok = False
            elif "@yahoo.com" in email:
                ok = False
            elif "@fintract.co.uk" in email:
                ok = False
            if ok != True:
                raise serializers.ValidationError("Use Your Organisation Email Address only")

        if password != password2:
            raise serializers.ValidationError("Passwords should be same")
        if not username.isalnum():
            raise serializers.ValidationError(self.default_error_messages)
    

        res = name != '' and all(chr.isalpha() or chr.isspace() for chr in name)
        if not res:
            raise serializers.ValidationError("Name should only contain alphabets")
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = CustomUser
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only = True)
    customer_id = serializers.CharField(max_length=255, min_length=3, read_only = True)
    tokens = serializers.CharField(max_length=80, min_length=3, read_only = True)
    #username = serializers.CharField(max_length=225, min_length=3)

    class Meta:
        model = CustomUser
        fields = ['id','email', 'password','username','customer_id','tokens']
        read_only_fields = ('id',)
        #fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        
        return {
            'id' : user.id,
            'email' : user.email,
            'username' : user.username,
            'customer_id' : user.customer_id,
            # 'tokens' : user.tokens()
            
            }
        return super().validate(attrs)

class AdminapproveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['customer_id']


class OTPVerificationSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=555)
    
    class Meta:
        model = CustomUser
        fields = ['otp']

    

class ResetPasswordEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        model = CustomUser
        fields = ['email']


class ResetToken(serializers.ModelSerializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        model = CustomUser
        fields = ['email']

class UpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['username', 'name']