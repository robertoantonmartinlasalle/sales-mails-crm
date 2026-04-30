from rest_framework import serializers
from users.models.usuario import Usuario


class UsuarioSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "rol",
            "empresa",
            "fecha_creacion"
        ]
        read_only_fields = ["id", "empresa", "fecha_creacion"]

    # =========================================================
    # VALIDACIÓN DE SEGURIDAD (ROL MULTIEMPRESA)
    # =========================================================
    def validate_rol(self, value):
        """
        Validamos que el rol seleccionado pertenece a la misma empresa
        que el usuario autenticado.

        Esto evita que desde el cliente (Postman, frontend, etc.)
        se pueda asignar un rol de otra empresa, lo cual rompería
        el aislamiento multiempresa.
        """

        request = self.context.get("request")

        # Seguridad: comprobamos que el rol pertenece a la misma empresa
        if value.empresa != request.user.empresa:
            raise serializers.ValidationError(
                "El rol seleccionado no pertenece a tu empresa"
            )

        return value

    # =========================================================
    # CREACIÓN DE USUARIO
    # =========================================================
    def create(self, validated_data):
        """
        Sobrescribimos la creación para encriptar correctamente la contraseña.

        IMPORTANTE:
        Nunca guardamos la contraseña en texto plano.
        """
        password = validated_data.pop("password")

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        return user


class MeSerializer(serializers.ModelSerializer):
    """
    Serializer restringido para el endpoint /me/.

    Solo permite leer y editar datos personales básicos.
    Campos sensibles (rol, empresa, is_staff, is_superuser)
    son siempre de solo lectura.
    """

    class Meta:
        model = Usuario
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "fecha_creacion",
        ]
        read_only_fields = ["id", "fecha_creacion"]
