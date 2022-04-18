from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Value
from django.db.models.functions import StrIndex
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

        User.objects.create_user(username=serializer.data['username'],
                                 password=serializer.data['password'],
                                 first_name=serializer.data['first_name'],
                                 last_name=serializer.data['last_name'])
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
        return models.Message.objects\
            .filter(dialogue__pk=pk, dialogue__users=self.request.user)\
            .order_by('-created_at')


class DialoguePictureView(APIView):
    permission_classes = []

    def get(self, request, pk):
        image = get_object_or_404(models.Picture.objects, pk=pk)
        return HttpResponse(image.data, content_type='image/png')


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

        return create_string_response("Ok")


class CreateDialogueView(CreateAPIView):
    serializer_class = serializers.PairDialogueCreateSerializer


class UserSuggestView(ListAPIView):
    pagination_class = pagination.DefaultPagination
    serializer_class = serializers.UserResponseSerializer

    def get_queryset(self):
        username_substring = self.kwargs['username_substring']
        return User.objects.filter(username__icontains=username_substring)\
            .annotate(search_index=StrIndex('username', Value(username_substring)))\
            .order_by('search_index', 'username')
