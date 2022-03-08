from django.urls import path

from messenger.views import HelloView, SessionLoginView, SessionLogoutView, RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('hello/', HelloView.as_view()),
    path('auth/session/login/', SessionLoginView.as_view()),
    path('auth/session/logout/', SessionLogoutView.as_view()),
    path('auth/token/login/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/register/', RegisterView.as_view()),
]
