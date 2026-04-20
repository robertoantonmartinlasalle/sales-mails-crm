from django.urls import path

from authentication.views.auth_view import LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),

    # REFRESH TOKEN
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]