from django.urls import path

from messenger.views import HelloView

urlpatterns = [
    path('hello/', HelloView.as_view())
]
