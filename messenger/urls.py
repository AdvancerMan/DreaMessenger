from django.urls import path

from messenger.views import HelloView, LoginView, LogoutView, RegisterView

urlpatterns = [
    path('hello/', HelloView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('register/', RegisterView.as_view()),
]
