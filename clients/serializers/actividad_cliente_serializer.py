from rest_framework import serializers
from clients.models.actividad_cliente import ActividadCliente


class ActividadClienteSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ActividadCliente
        fields = [
            "id",
            "tipo",
            "descripcion",
            "fecha_creacion",
            "usuario_nombre",
        ]

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.email
        return None
