import hashlib
import io
import uuid

import PIL.Image
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


class PictureLinkSerializer(serializers.ModelSerializer):
    link = serializers.SerializerMethodField('serialize_link')

    def serialize_link(self, picture):
        return self.context['request'].build_absolute_uri(reverse('picture', args=[picture.uuid]))

    class Meta:
        model = models.PictureV2
        fields = ('link',)


class UserInfoResponseSerializer(serializers.ModelSerializer):
    avatar = PictureLinkSerializer()

    class Meta:
        model = models.UserInfo
        fields = ('avatar',)


class UserResponseSerializer(serializers.ModelSerializer):
    info = UserInfoResponseSerializer()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'info')


class DialogueResponseSerializer(serializers.ModelSerializer):
    users = UserResponseSerializer(many=True)

    class Meta:
        model = models.Dialogue
        fields = ('users', 'id')


class MessageResponseSerializer(serializers.ModelSerializer):
    from_user = UserResponseSerializer()
    picture = PictureLinkSerializer()

    class Meta:
        model = models.Message
        fields = ('id', 'from_user', 'picture', 'is_edited', 'edited_at', 'created_at')


class PictureSerializer:
    def __init__(self, data):
        self.data = data
        self.cleaned_data = None
        self.errors = None

    def is_valid(self):
        self.cleaned_data = {}
        if 'data' not in self.data:
            self.errors = {'data': 'Required'}
            return False

        try:
            image = PIL.Image.open(self.data['data'].file)
        except IOError:
            self.errors = {'data': 'Not an image'}
            return False

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        self.cleaned_data['data'] = img_byte_arr.getvalue()
        return True

    def save(self):
        assert self.cleaned_data is not None, 'Not validated'

        data = self.cleaned_data['data']
        sha256 = hashlib.sha256(data).hexdigest()
        existing = models.PictureV2.objects.filter(sha256=sha256)

        for picture in existing:
            if bytes(picture.data) == data:
                return picture
        return models.PictureV2.objects.create(uuid=uuid.uuid4(), data=self.cleaned_data['data'], sha256=sha256)


class PairDialogueCreateSerializer(serializers.Serializer):
    with_user = serializers.CharField(
        max_length=150,
        help_text=_('Required. Username to create dialogue with. '
                    '150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
    )

    def validate(self, attrs):
        user_matched = User.objects.filter(username=attrs['with_user']).first()
        if user_matched is None:
            raise serializers.ValidationError(detail=f"Unknown user {attrs['with_user']}")

        originator = self.context['request'].user
        if originator == user_matched:
            raise serializers.ValidationError(detail=f"Self dialogues are prohibited")

        if models.Dialogue.objects.filter(users=user_matched, is_tetatet=True).filter(users=originator).exists():
            raise serializers.ValidationError(detail="Dialogue already exists")

        return attrs

    def create(self, validated_data):
        with_user = User.objects.filter(username=validated_data['with_user']).first()
        originator = self.context['request'].user
        dialogue = models.Dialogue.objects.create(
            is_tetatet=True,
        )
        dialogue.users.set((originator, with_user))

        return {
            'with_user': with_user,
            'dialogue': dialogue,
        }

    def update(self, instance, validated_data):
        raise NotImplementedError('Unexpected update of an instance')

    def to_representation(self, instance):
        return {
            "dialogue": instance['dialogue'].id
        }
