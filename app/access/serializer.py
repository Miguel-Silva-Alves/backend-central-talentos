from rest_framework import serializers
from .models import (
    User, EmailPasswordAuthentication, GoogleAuthentication, Token,
    RefreshToken, RecoveryPassword, ValidateEmail
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'created_at', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class EmailPasswordAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailPasswordAuthentication
        fields = '__all__'


class GoogleAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleAuthentication
        fields = '__all__'


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class RefreshTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefreshToken
        fields = '__all__'


class RecoveryPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecoveryPassword
        fields = '__all__'


class ValidateEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidateEmail
        fields = '__all__'
