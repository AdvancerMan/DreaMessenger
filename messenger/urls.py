from django.urls import path

from messenger.views import HelloView, SessionLoginView, SessionLogoutView, RegisterView, MyDialoguesView, MessagesView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('hello/', HelloView.as_view()),

    path('auth/session/login/', SessionLoginView.as_view()),
    path('auth/session/logout/', SessionLogoutView.as_view()),
    path('auth/token/login/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/register/', RegisterView.as_view()),

    path('dialogue/my/', MyDialoguesView.as_view()),
    path('dialogue/<id>/messages/', MessagesView.as_view()),
]
