import datetime

from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Value, Q, When, Case
from django.db.models.functions import StrIndex, Least
from django.http import HttpResponse
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404, CreateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from messenger import serializers, pagination, models


def create_string_response(response, status=200):
    return Response({"detail": response}, status=status)


def create_validation_error_response(errors, status=400):
    return Response(errors, status=status)


class HelloView(APIView):
    def get(self, request):
        return create_string_response("Hello world!")


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        if get_user(request).is_authenticated:
            return create_string_response("User has already logged in", 400)

        serializer = serializers.RegisterCredentialsSerializer(data=request.data)
        if not serializer.is_valid():
            return create_validation_error_response(serializer.errors)

        user = User.objects.create_user(username=serializer.data['username'],
                                        password=serializer.data['password'],
                                        first_name=serializer.data['first_name'],
                                        last_name=serializer.data['last_name'])
        models.UserInfo.objects.create(user=user)

        return create_string_response("Success")


class SessionLoginView(APIView):
    permission_classes = []

    def post(self, request):
        if get_user(request).is_authenticated:
            return create_string_response("User has already logged in", 400)

        serializer = serializers.AuthCredentialsSerializer(data=request.data)
        if not serializer.is_valid():
            return create_validation_error_response(serializer.errors)

        user = authenticate(username=serializer.data['username'],
                            password=serializer.data['password'])
        if user is not None:
            login(request, user)
            return create_string_response("Success")
        else:
            return create_string_response("Invalid credentials", 400)


class SessionLogoutView(APIView):
    def post(self, request):
        logout(request)
        return create_string_response("Success")


class MyDialoguesView(ListAPIView):
    pagination_class = pagination.DefaultPagination
    serializer_class = serializers.DialogueResponseSerializer

    def get_queryset(self):
        return self.request.user.dialogues.all().order_by('-updated_at')


class MessagesByDialogueView(ListAPIView):
    pagination_class = pagination.DefaultPagination
    serializer_class = serializers.MessageResponseSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return models.Message.objects \
            .filter(dialogue__pk=pk, dialogue__users=self.request.user) \
            .order_by('-created_at')


class PictureView(APIView):
    permission_classes = []

    def get(self, request, uuid):
        image = get_object_or_404(models.PictureV2.objects, uuid=uuid)
        return HttpResponse(image.data, content_type='image/jpeg')


class MyUserView(RetrieveAPIView):
    serializer_class = serializers.UserResponseSerializer

    def get_object(self):
        return self.request.user


class UserView(RetrieveAPIView):
    serializer_class = serializers.UserResponseSerializer
    queryset = User.objects.all()
    lookup_field = 'username'


class SendDialogueMessageView(APIView):
    parser_classes = [MultiPartParser]

    @transaction.atomic
    def post(self, request, pk):
        dialogue = get_object_or_404(models.Dialogue, pk=pk, users=request.user)

        serializer = serializers.PictureSerializer(data=request.data)
        if not serializer.is_valid():
            return create_validation_error_response(serializer.errors)

        picture = serializer.save()
        message = models.Message(
            dialogue=dialogue,
            from_user=request.user,
            picture=picture,
        )
        message.save()

        dialogue.updated_at = datetime.datetime.utcnow()
        dialogue.save(update_fields=['updated_at'])

        return create_string_response("Ok")


class CreateDialogueView(CreateAPIView):
    serializer_class = serializers.PairDialogueCreateSerializer


class UserSuggestView(ListAPIView):
    pagination_class = pagination.DefaultPagination
    serializer_class = serializers.UserResponseSerializer

    def get_queryset(self):
        name_substring = self.request.query_params.get('name_substring', '').strip()

        fields = [
            ('username', name_substring, 'default'),
            ('first_name', name_substring, 'default'),
            ('last_name', name_substring, 'default'),
        ]
        if ' ' in name_substring:
            fields.append(('first_name', name_substring[:name_substring.index(' ')].strip(), 'space'))
            fields.append(('last_name', name_substring[name_substring.index(' '):].strip(), 'space'))

        str_index_expressions = {}
        search_index_expressions = []
        for field_name, substring, meta_description in fields:
            index_expression = StrIndex(field_name, Value(substring))
            str_index_expression_name = f'{field_name}_{meta_description}'
            str_index_expressions[str_index_expression_name] = index_expression
            expression = Case(When(**{str_index_expression_name: 0}, then=10 ** 9), default=str_index_expression_name)
            search_index_expressions.append(expression)

        query_condition = (Q(username__icontains=name_substring) |
                           Q(first_name__icontains=name_substring) |
                           Q(last_name__icontains=name_substring))
        if ' ' in name_substring:
            query_condition = (query_condition |
                               Q(first_name__icontains=name_substring[:name_substring.index(' ')].strip()) &
                               Q(last_name__icontains=name_substring[name_substring.index(' '):].strip()))

        return User.objects.filter(query_condition) \
            .annotate(**str_index_expressions) \
            .annotate(search_index=Least(*search_index_expressions)) \
            .order_by('search_index', 'username')


class SetUserAvatarView(APIView):
    parser_classes = [MultiPartParser]

    @transaction.atomic
    def post(self, request):
        serializer = serializers.PictureSerializer(data=request.data)
        if not serializer.is_valid():
            return create_validation_error_response(serializer.errors)

        picture = serializer.save()
        request.user.info.avatar = picture
        request.user.info.save(update_fields=['avatar'])

        return create_string_response("Ok")
