from rest_framework import serializers
from campaigns.models.campaignsend import CampaignSend
from campaigns.models.campanaemail import CampanaEmail
from clients.models import Cliente


class CampanaSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado de CampanaEmail.

    Se utiliza para mostrar información básica de la campaña
    dentro del envío.
    """

    class Meta:
        model = CampanaEmail
        fields = ["id", "nombre"]


class ClienteSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado de Cliente.

    Se utiliza para mostrar información básica del cliente
    dentro del envío.
    """

    class Meta:
        model = Cliente
        fields = ["id", "nombre", "email"]


class CampaignSendSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo CampaignSend.

    Se encarga de:

    - Convertir datos JSON <-> modelo CampaignSend
    - Validar relaciones entre cliente y campaña
    - Garantizar aislamiento multiempresa
    - Mejorar la respuesta de la API
    """

    campana_detalle = CampanaSimpleSerializer(
        source="campana",
        read_only=True
    )

    cliente_detalle = ClienteSimpleSerializer(
        source="cliente",
        read_only=True
    )

    class Meta:
        model = CampaignSend
        fields = "__all__"

    def validate(self, data):
        """
        Validación personalizada.

        Comprobamos:

        1. Que existen campaña y cliente
        2. Que ambos pertenecen a la misma empresa del usuario
        3. Que campaña y cliente pertenecen a la misma empresa entre sí
        """

        request = self.context.get("request")

        if not request or not request.user:
            return data

        empresa = request.user.empresa

        campana = data.get("campana")
        cliente = data.get("cliente")

        # Validaciones básicas
        if not campana:
            raise serializers.ValidationError(
                "La campaña es obligatoria."
            )

        if not cliente:
            raise serializers.ValidationError(
                "El cliente es obligatorio."
            )

        # VALIDACIÓN MULTIEMPRESA (IMPORTANTE)
        if campana.empresa != empresa:
            raise serializers.ValidationError(
                "La campaña no pertenece a tu empresa."
            )

        if cliente.empresa != empresa:
            raise serializers.ValidationError(
                "El cliente no pertenece a tu empresa."
            )

        # VALIDACIÓN ENTRE ELLOS
        if campana.empresa != cliente.empresa:
            raise serializers.ValidationError(
                "La campaña y el cliente no pertenecen a la misma empresa."
            )

        return data