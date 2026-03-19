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
    - Validar relaciones
    - Mejorar la respuesta de la API
    """

    """
    Campos de solo lectura para enriquecer la respuesta.
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

        Comprobamos que:
        - Existe la campaña
        - Existe el cliente
        """

        campana = data.get("campana")
        cliente = data.get("cliente")

        if not campana:
            raise serializers.ValidationError(
                "La campaña es obligatoria."
            )

        if not cliente:
            raise serializers.ValidationError(
                "El cliente es obligatorio."
            )

        return data