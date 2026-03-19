from rest_framework import serializers
from campaigns.models.campaignsend import CampaignSend
from campaigns.models.campanaemail import CampanaEmail
from clients.models import Cliente


class CampaignSendSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo CampaignSend.

    Se encarga de:

    - Convertir datos JSON <-> modelo CampaignSend
    - Validar relaciones entre cliente y campaña
    """

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