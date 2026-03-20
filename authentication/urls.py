from django.urls import path

from authentication.views.auth_view import LoginView


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
]