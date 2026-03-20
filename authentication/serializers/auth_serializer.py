from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para la autenticación mediante JWT.

    Este serializer se encarga de:

    - Validar las credenciales del usuario (email + contraseña)
    - Generar los tokens JWT (access y refresh)
    - Incluir información adicional del usuario en la respuesta
    - Añadir datos personalizados dentro del propio token

    Se ha diseñado específicamente para este proyecto, donde:

    - El usuario se autentica mediante email (no username)
    - Existe un sistema multiempresa
    - Cada usuario tiene un rol asociado

    Esto nos permitirá posteriormente:

    - Identificar la empresa del usuario en cada petición
    - Aplicar permisos según el rol
    - Evitar consultas adicionales a base de datos
    """

    # =========================================================
    # CONFIGURACIÓN DEL CAMPO DE LOGIN
    # =========================================================
    # Indicamos explícitamente que el campo de autenticación
    # será el email en lugar del username.
    username_field = "email"

    # =========================================================
    # VALIDACIÓN DE CREDENCIALES
    # =========================================================
    def validate(self, attrs):
        """
        Método principal de validación.

        Se ejecuta cuando el usuario intenta hacer login.

        Responsabilidades:
        - Extraer email y password
        - Autenticar usuario contra Django
        - Verificar que el usuario está activo
        - Generar tokens JWT
        - Construir la respuesta personalizada
        """

        email = attrs.get("email")
        password = attrs.get("password")

        # -----------------------------------------------------
        # AUTENTICACIÓN DEL USUARIO
        # -----------------------------------------------------
        # Utilizamos el sistema interno de Django para validar
        # las credenciales (incluye hashing de contraseñas).
        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password
        )

        # Si las credenciales no son válidas
        if not user:
            raise serializers.ValidationError("Credenciales inválidas")

        # Si el usuario existe pero está desactivado
        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo")

        # -----------------------------------------------------
        # GENERACIÓN DE TOKENS
        # -----------------------------------------------------
        # Llamamos al método original para generar:
        # - access token
        # - refresh token
        data = super().validate(attrs)

        # -----------------------------------------------------
        # RESPUESTA PERSONALIZADA
        # -----------------------------------------------------
        # Añadimos información del usuario en la respuesta.
        # Esto evita tener que hacer una llamada adicional
        # desde el frontend para obtener datos básicos.
        data["user"] = {
            "id": str(user.id),
            "email": user.email,
            "empresa_id": str(user.empresa.id),
            "rol": user.rol.nombre,
        }

        return data

    # =========================================================
    # PERSONALIZACIÓN DEL TOKEN JWT
    # =========================================================
    @classmethod
    def get_token(cls, user):
        """
        Método que permite modificar el contenido del token JWT.

        Aquí añadimos información relevante del usuario
        directamente dentro del token.

        Ventajas:
        - Evitamos consultas repetidas a la base de datos
        - Podemos identificar al usuario rápidamente
        - Permite implementar control de permisos eficiente
        """

        token = super().get_token(user)

        # -----------------------------------------------------
        # DATOS PERSONALIZADOS EN EL TOKEN
        # -----------------------------------------------------
        token["user_id"] = str(user.id)
        token["email"] = user.email
        token["empresa_id"] = str(user.empresa.id)
        token["rol"] = user.rol.nombre

        return token