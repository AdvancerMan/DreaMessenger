from django.urls import path

import messenger.views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('hello/', messenger.views.HelloView.as_view()),

    path('auth/session/login/', messenger.views.SessionLoginView.as_view()),
    path('auth/session/logout/', messenger.views.SessionLogoutView.as_view()),
    path('auth/token/login/', TokenObtainPairView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view()),
    path('auth/register/', messenger.views.RegisterView.as_view()),

    path('dialogue/my/', messenger.views.MyDialoguesView.as_view()),
    path('dialogue/<int:pk>/messages/', messenger.views.MessagesByDialogueView.as_view()),
    path('dialogue/<int:pk>/messages/send/', messenger.views.SendDialogueMessageView.as_view()),
    path('picture/<uuid>/', messenger.views.PictureView.as_view(), name='picture'),
    path('dialogue/create/', messenger.views.CreateDialogueView.as_view()),

    path('user/my/', messenger.views.MyUserView.as_view()),
    path('user/find/<username>/', messenger.views.UserView.as_view()),
    path('user/suggest/', messenger.views.UserSuggestView.as_view()),
    path('user/avatar/', messenger.views.SetUserAvatarView.as_view()),
]
