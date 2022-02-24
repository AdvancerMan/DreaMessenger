from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from messenger import serializers


def create_string_response(response, status=200):
    return Response({"detail": response}, status=status)


def create_validation_error_response(message, errors, status=400):
    response = {}
    for field, errors in errors.items():
        response[field] = [str(error) for error in errors]
    return Response({"detail": message, "errors": response}, status=status)


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
            return create_validation_error_response("Invalid data", serializer.errors)

        user = User.objects.create_user(username=serializer.data['username'],
                                        password=serializer.data['password'],
                                        first_name=serializer.data['first_name'],
                                        last_name=serializer.data['last_name'])
        login(request, user)
        return create_string_response("Success")


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        if get_user(request).is_authenticated:
            return create_string_response("User has already logged in", 400)

        serializer = serializers.AuthCredentialsSerializer(data=request.data)
        if not serializer.is_valid():
            return create_validation_error_response("Invalid data", serializer.errors)

        user = authenticate(username=serializer.data['username'],
                            password=serializer.data['password'])
        if user is not None:
            login(request, user)
            return create_string_response("Success")
        else:
            return create_string_response("Invalid credentials", 400)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return create_string_response("Success")
