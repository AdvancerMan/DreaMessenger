from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from messenger import models


class RegisterCredentialsSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, validators=[password_validation.validate_password])
    first_name = serializers.CharField(max_length=150, min_length=1, allow_blank=False)
    last_name = serializers.CharField(max_length=150, min_length=1, allow_blank=False)

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


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class DialogueResponseSerializer(serializers.ModelSerializer):
    users = UserResponseSerializer(many=True)

    class Meta:
        model = models.Dialogue
        fields = ('users', 'id')


class PictureLinkSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField('serialize_link')

    def serialize_link(self, picture):
        return self.context['request'].build_absolute_uri(reverse('dialogue-picture', args=[picture.pk]))

    class Meta:
        model = models.Picture
        fields = ('link',)


class MessageResponseSerializer(serializers.ModelSerializer):
    from_user = UserResponseSerializer()
    picture = PictureLinkSerializer()

    class Meta:
        model = models.Message
        fields = ('from_user', 'picture', 'is_edited', 'edited_at', 'created_at')
