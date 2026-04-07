from django.contrib import admin
from django.urls import path, include

# Importamos la vista de refresh de JWT
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),

    # =========================================================
    # API PRINCIPAL
    # =========================================================
    path('api/', include('clients.urls')),
    path('api/', include('campaigns.urls')),

    # =========================================================
    # AUTENTICACIÓN
    # =========================================================
    path("api/auth/", include("authentication.urls")),

    # =========================================================
    # REFRESH TOKEN (JWT)
    # =========================================================
    # Endpoint para renovar el access token utilizando el refresh token
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),


    # =========================================================
    # USUARIOS
    # =========================================================
     
    path('api/', include('users.urls')),
]