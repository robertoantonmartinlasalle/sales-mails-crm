from rest_framework import serializers
from campaigns.models.plantillaemail import PlantillaEmail


class PlantillaEmailSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo PlantillaEmail.

    Se encarga de:

    - Convertir datos JSON <-> modelo PlantillaEmail
    - Validar los datos antes de guardar
    - Garantizar integridad en entorno multiempresa
    """

    class Meta:
        model = PlantillaEmail
        fields = "__all__"

        # La empresa no se envía desde el cliente
        # Se asigna automáticamente en la vista
        read_only_fields = ["empresa"]

    def validate(self, data):
        """
        Validación personalizada.

        Reglas:
        - Campos obligatorios
        - Evitar nombres duplicados dentro de la misma empresa
        """

        request = self.context.get("request")

        if not request:
            return data

        empresa = request.user.empresa

        # Soporte CREATE / UPDATE / PATCH
        nombre = data.get(
            "nombre",
            self.instance.nombre if self.instance else None
        )

        asunto = data.get(
            "asunto",
            self.instance.asunto if self.instance else None
        )

        cuerpo = data.get(
            "cuerpo",
            self.instance.cuerpo if self.instance else None
        )

        # Validaciones básicas
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

        # VALIDACIÓN MULTIEMPRESA
        qs = PlantillaEmail.objects.for_empresa(empresa).filter(
            nombre=nombre
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe una plantilla con ese nombre en tu empresa."
            )

        return data