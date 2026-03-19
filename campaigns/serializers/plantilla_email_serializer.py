from rest_framework import serializers
from campaigns.models.plantillaemail import PlantillaEmail


class PlantillaEmailSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo PlantillaEmail.

    Se encarga de:

    - Convertir datos JSON <-> modelo PlantillaEmail
    - Validar los datos antes de guardar
    - Definir qué campos se exponen en la API
    """

    class Meta:
        model = PlantillaEmail

        """
        Usamos todos los campos del modelo.
        """
        fields = "__all__"

    def validate(self, data):
        """
        Validación personalizada.

        Aquí podríamos añadir reglas de negocio en el futuro,
        como evitar nombres duplicados o validar longitud del contenido.
        """

        nombre = data.get("nombre")
        asunto = data.get("asunto")
        cuerpo = data.get("cuerpo")

        """
        Validaciones básicas para evitar datos vacíos.
        """
        if not nombre:
            raise serializers.ValidationError(
                "El nombre de la plantilla es obligatorio."
            )

        if not asunto:
            raise serializers.ValidationError(
                "El asunto es obligatorio."
            )

        if not cuerpo:
            raise serializers.ValidationError(
                "El cuerpo del email no puede estar vacío."
            )

        return data