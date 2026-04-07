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
            "rol",
            "empresa",
            "fecha_creacion"
        ]
        read_only_fields = ["id", "empresa", "fecha_creacion"]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        return user