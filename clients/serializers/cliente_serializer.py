from rest_framework import serializers
from clients.models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Cliente.

    Se encarga de:

    - Convertir datos JSON <-> modelo Cliente
    - Validar datos antes de guardar
    - Proteger relaciones multiempresa
    """

    class Meta:
        model = Cliente
        fields = "__all__"
        read_only_fields = ["empresa"]

    def validate(self, data):
        """
        Validación personalizada.

        Aquí comprobamos que el estado_cliente
        pertenece a la misma empresa que el usuario.
        """

        request = self.context.get("request")

        if not request or not request.user:
            return data

        empresa = request.user.empresa

        estado_cliente = data.get("estado_cliente")

        # Validamos que el estado pertenece a la empresa
        if estado_cliente and estado_cliente.empresa != empresa:
            raise serializers.ValidationError(
                "El estado de cliente no pertenece a tu empresa."
            )

        return data