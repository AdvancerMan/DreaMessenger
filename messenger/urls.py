from django.urls import path

from messenger.views import HelloView, LoginView, LogoutView

urlpatterns = [
    path('hello/', HelloView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
]
