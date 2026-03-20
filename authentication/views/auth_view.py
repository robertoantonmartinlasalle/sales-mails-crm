from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny

from authentication.serializers.auth_serializer import CustomTokenObtainPairSerializer


class LoginView(TokenObtainPairView):
    """
    Vista personalizada para el login mediante JWT.

    Esta vista se encarga de:

    - Recibir las credenciales del usuario (email + password)
    - Delegar la validación al serializer personalizado
    - Generar y devolver los tokens JWT (access y refresh)

    A diferencia de la vista por defecto de SimpleJWT:

    - Utiliza email en lugar de username
    - Devuelve información adicional del usuario
    - Incluye datos personalizados en el token (empresa, rol)

    Esta vista representa el punto de entrada principal
    al sistema de autenticación del CRM.
    """

    # =========================================================
    # SERIALIZER PERSONALIZADO
    # =========================================================
    # Indicamos que esta vista utilizará nuestro serializer
    # en lugar del que viene por defecto en SimpleJWT.
    serializer_class = CustomTokenObtainPairSerializer

    # =========================================================
    # PERMISOS
    # =========================================================
    # Permitimos acceso sin autenticación, ya que esta vista
    # es precisamente la que genera el token.
    permission_classes = [AllowAny]