from rest_framework import serializers
from campaigns.models.campanaemail import CampanaEmail
from campaigns.models.plantillaemail import PlantillaEmail


class PlantillaEmailSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado de PlantillaEmail.

    Se utiliza para mostrar información básica de la plantilla
    dentro de la campaña (mejora de la respuesta de la API).
    """

    class Meta:
        model = PlantillaEmail
        fields = ["id", "nombre", "asunto"]


class CampanaEmailSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo CampanaEmail.

    Se encarga de:

    - Convertir datos JSON <-> modelo CampanaEmail
    - Validar relaciones (plantilla)
    - Mejorar la representación de datos para el frontend
    """

    """
    Campo adicional para mostrar información detallada
    de la plantilla asociada.
    """
    plantilla_detalle = PlantillaEmailSimpleSerializer(
        source="plantilla",
        read_only=True
    )

    class Meta:
        model = CampanaEmail

        """
        Incluimos todos los campos del modelo.
        """
        fields = "__all__"

    def validate(self, data):
        """
        Validación personalizada.

        Comprobamos que la plantilla existe.
        (DRF ya lo valida, pero dejamos preparado para futuras reglas).
        """

        plantilla = data.get("plantilla")

        if not plantilla:
            raise serializers.ValidationError(
                "La plantilla es obligatoria para crear una campaña."
            )

        return data