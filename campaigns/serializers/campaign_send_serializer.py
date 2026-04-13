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
    - Proteger el campo empresa
    - Permitir envío individual y masivo
    - Mejorar la respuesta de la API
    """

    """
    Campo adicional para soportar envíos masivos.

    En lugar de enviar un único cliente, podemos enviar
    una lista de IDs de clientes.

    Ejemplo:
    {
        "campana": 1,
        "clientes": [1, 2, 3]
    }

    Este campo NO existe en el modelo, es solo de entrada (write_only).
    """
    clientes = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    """
    Campos enriquecidos para mejorar la respuesta.
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

        """
        La empresa NO puede ser enviada desde el frontend.

        Se asigna automáticamente en el backend.
        """
        read_only_fields = ["empresa", "error_mensaje"]

    def validate(self, data):
        """
        Validación personalizada.

        Comprobamos:

        1. Que existe la campaña
        2. Que los clientes pertenecen a la empresa
        3. Que la campaña pertenece a la empresa
        4. Soporte tanto para envío individual como masivo
        """

        request = self.context.get("request")

        """
        Seguridad: si no hay request o usuario,
        evitamos errores y devolvemos los datos.
        """
        if not request or not request.user:
            return data

        empresa = request.user.empresa
        campana = data.get("campana")

        """
        VALIDACIÓN CASO MASIVO

        Si recibimos el campo "clientes",
        procesamos envío a múltiples clientes.
        """
        clientes_ids = data.get("clientes")

        if clientes_ids:
            clientes = Cliente.objects.filter(id__in=clientes_ids)

            """
            Validamos que los clientes existen.
            """
            if not clientes.exists():
                raise serializers.ValidationError(
                    "Los clientes no son válidos."
                )

            """
            Validamos que todos los clientes pertenecen
            a la empresa del usuario.
            """
            for cliente in clientes:
                if cliente.empresa != empresa:
                    raise serializers.ValidationError(
                        "Uno de los clientes no pertenece a tu empresa."
                    )

            """
            Validamos que la campaña pertenece a la empresa.
            """
            if campana and campana.empresa != empresa:
                raise serializers.ValidationError(
                    "La campaña no pertenece a tu empresa."
                )

            return data

        """
        VALIDACIÓN CASO INDIVIDUAL

        Comportamiento original: un envío → un cliente
        """
        cliente = data.get("cliente")

        if not campana:
            raise serializers.ValidationError(
                "La campaña es obligatoria."
            )

        if not cliente:
            raise serializers.ValidationError(
                "El cliente es obligatorio."
            )

        """
        VALIDACIÓN MULTIEMPRESA
        """
        if campana.empresa != empresa:
            raise serializers.ValidationError(
                "La campaña no pertenece a tu empresa."
            )

        if cliente.empresa != empresa:
            raise serializers.ValidationError(
                "El cliente no pertenece a tu empresa."
            )

        """
        VALIDACIÓN ENTRE ENTIDADES
        """
        if campana.empresa != cliente.empresa:
            raise serializers.ValidationError(
                "La campaña y el cliente no pertenecen a la misma empresa."
            )

        return data