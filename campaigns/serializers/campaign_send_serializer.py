from rest_framework import serializers
from campaigns.models.campaignsend import CampaignSend
from campaigns.models.campanaemail import CampanaEmail
from clients.models import Cliente


class CampanaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampanaEmail
        fields = ["id", "nombre"]


class ClienteSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nombre", "email"]


class CampaignSendSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo CampaignSend.

    Se encarga de:

    - Validar relaciones campaña-cliente
    - Garantizar multiempresa
    - Soportar envíos masivos
    """

    clientes = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    campana_detalle = CampanaSimpleSerializer(source="campana", read_only=True)
    cliente_detalle = ClienteSimpleSerializer(source="cliente", read_only=True)

    class Meta:
        model = CampaignSend
        fields = "__all__"
        read_only_fields = ["empresa", "error_mensaje"]

    def validate(self, data):
        request = self.context.get("request")

        if not request:
            return data

        empresa = request.user.empresa
        campana = data.get("campana")
        clientes_ids = data.get("clientes")

        # VALIDAR CAMPAÑA
        if not campana:
            raise serializers.ValidationError("La campaña es obligatoria.")

        if campana.empresa != empresa:
            raise serializers.ValidationError(
                "La campaña no pertenece a tu empresa."
            )

        # VALIDAR PLANTILLA DE LA CAMPAÑA
        if campana.plantilla.empresa != empresa:
            raise serializers.ValidationError(
                "La plantilla asociada a la campaña no pertenece a tu empresa."
            )

        # =========================================================
        # ENVÍO MASIVO
        # =========================================================
        if clientes_ids:

            clientes = Cliente.objects.for_empresa(empresa).filter(
                id__in=clientes_ids
            )

            # 🔥 VALIDAR IDs EXISTENTES
            if len(clientes_ids) != clientes.count():
                raise serializers.ValidationError(
                    "Algunos clientes no existen."
                )

            return data

        # =========================================================
        # ENVÍO INDIVIDUAL
        # =========================================================
        cliente = data.get("cliente")

        if not cliente:
            raise serializers.ValidationError(
                "El cliente es obligatorio."
            )

        if cliente.empresa != empresa:
            raise serializers.ValidationError(
                "El cliente no pertenece a tu empresa."
            )

        return data