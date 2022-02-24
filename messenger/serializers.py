from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class RegisterCredentialsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, validators=[password_validation.validate_password])
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')


class AuthCredentialsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
    )

    class Meta:
        model = User
        fields = ('username', 'password')
