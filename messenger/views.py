import json

from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework.views import APIView


class HelloView(APIView):
    def get(self, request):
        return Response({"message": "Hello world!"})


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=400
            )
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"detail": "Success"})
        return Response(
            {"detail": "Invalid credentials"},
            status=400,
        )


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Success"})
