from rest_framework import serializers
from campaigns.models.campanaemail import CampanaEmail
from campaigns.models.plantillaemail import PlantillaEmail


class PlantillaEmailSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado de PlantillaEmail.

    Se utiliza para mostrar información básica de la plantilla
    dentro de la campaña.
    """

    class Meta:
        model = PlantillaEmail
        fields = ["id", "nombre", "asunto"]


class CampanaEmailSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo CampanaEmail.

    Se encarga de:

    - Convertir datos JSON <-> modelo CampanaEmail
    - Validar que la plantilla pertenece a la empresa
    - Garantizar aislamiento multiempresa
    """

    plantilla_detalle = PlantillaEmailSimpleSerializer(
        source="plantilla",
        read_only=True
    )

    class Meta:
        model = CampanaEmail
        fields = "__all__"
        read_only_fields = ["empresa"]

    def validate(self, data):
        """
        Validación personalizada.

        Reglas:
        - La plantilla es obligatoria
        - La plantilla debe pertenecer a la misma empresa
        """

        request = self.context.get("request")

        if not request:
            return data

        empresa = request.user.empresa
        plantilla = data.get("plantilla")

        if not plantilla:
            raise serializers.ValidationError(
                "La plantilla es obligatoria para crear una campaña."
            )

        # VALIDACIÓN MULTIEMPRESA (CLAVE)
        if plantilla.empresa != empresa:
            raise serializers.ValidationError(
                "La plantilla no pertenece a tu empresa."
            )

        return data