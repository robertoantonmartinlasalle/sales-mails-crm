from rest_framework import serializers
from crm.models import Oportunidad
from clients.models import Cliente


class ClienteSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado de Cliente.

    Se utiliza para mostrar información básica del cliente
    dentro de la oportunidad.
    """

    class Meta:
        model = Cliente
        fields = ["id", "nombre"]


class OportunidadSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Oportunidad.

    Se encarga de:

    - Convertir datos JSON <-> modelo Oportunidad
    - Validar que el cliente pertenece a la empresa del usuario
    - Garantizar aislamiento multiempresa
    - Asignar empresa y usuario_responsable automáticamente
    """

    cliente_detalle = ClienteSimpleSerializer(
        source="cliente",
        read_only=True
    )

    class Meta:
        model = Oportunidad
        fields = "__all__"
        read_only_fields = ["empresa", "usuario_responsable", "fecha_creacion"]

    def validate_cliente(self, value):
        """
        Valida que el cliente pertenece a la empresa del usuario.

        Evita que un usuario asigne clientes de otra empresa
        a una oportunidad de la suya.
        """
        request = self.context.get("request")
        if not request:
            return value

        if value.empresa != request.user.empresa:
            raise serializers.ValidationError(
                "El cliente no pertenece a tu empresa."
            )
        return value

    def validate_fecha_cierre_prevista(self, value):
        from django.utils import timezone

        if value and value.date() < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de cierre no puede ser anterior a hoy."
            )
        return value

    def validate(self, data):
        estado = data.get("estado", getattr(self.instance, "estado", None))
        valor_estimado = data.get(
            "valor_estimado",
            getattr(self.instance, "valor_estimado", None)
        )
        probabilidad = data.get(
            "probabilidad",
            getattr(self.instance, "probabilidad", None)
        )

        if estado in ["ganada", "perdida"]:
            if valor_estimado is None:
                raise serializers.ValidationError(
                    "Para cerrar una oportunidad debes indicar un valor estimado."
                )
            if probabilidad is None:
                raise serializers.ValidationError(
                    "Para cerrar una oportunidad debes indicar una probabilidad."
                )

        return data
