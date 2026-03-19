from rest_framework import serializers
from clients.models import Cliente, EstadoCliente


class EstadoClienteSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado de EstadoCliente.

    Este serializer se utiliza únicamente para mostrar información
    básica del estado dentro del cliente (mejora de la respuesta de la API).
    """

    class Meta:
        model = EstadoCliente
        fields = ["id", "nombre"]


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Cliente.

    Se encarga de:

    - Convertir datos JSON <-> modelo Cliente
    - Validar relaciones entre modelos
    - Proteger el sistema multiempresa
    - Mejorar la representación de datos en la API
    """

    """
    Campo adicional de solo lectura.

    En lugar de devolver solo el ID del estado_cliente,
    devolvemos también información útil (id + nombre).

    Esto mejora la experiencia del frontend.
    """
    estado_cliente_detalle = EstadoClienteSimpleSerializer(
        source="estado_cliente",
        read_only=True
    )

    class Meta:
        model = Cliente

        """
        Incluimos todos los campos del modelo.
        Además, DRF incluirá automáticamente el campo
        estado_cliente_detalle definido arriba.
        """
        fields = "__all__"

        """
        La empresa no puede ser enviada desde el frontend.
        Se asigna automáticamente en el ViewSet.
        """
        read_only_fields = ["empresa"]

    def validate(self, data):
        """
        Validación personalizada.

        Comprobamos que el estado_cliente pertenece
        a la misma empresa que el usuario autenticado.

        Esto es CRÍTICO en un sistema multiempresa.
        """

        request = self.context.get("request")

        """
        Seguridad: si no hay request o usuario,
        evitamos errores y devolvemos los datos.
        """
        if not request or not request.user:
            return data

        empresa = request.user.empresa
        estado_cliente = data.get("estado_cliente")

        """
        Validamos que el estado pertenece a la empresa del usuario.
        """
        if estado_cliente and estado_cliente.empresa != empresa:
            raise serializers.ValidationError(
                "El estado de cliente no pertenece a tu empresa."
            )

        return data