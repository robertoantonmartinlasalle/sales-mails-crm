from rest_framework import serializers
from crm.models import Oportunidad
from clients.models import Cliente
from crm.models import Actividad


"""
NOTA DE DISEÑO

En este módulo no se ha separado la lógica en múltiples archivos
(vistas y serializers) para evitar cambios innecesarios, ya que
el backend ya está integrado con el frontend.

Se ha priorizado mantener estabilidad y reducir riesgos,
dejando ambas clases (Oportunidad y Actividad) en el mismo archivo.

Como mejora futura, se podría modularizar siguiendo la estructura
del resto del proyecto para mejorar mantenibilidad.
"""

class ClienteSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado de Cliente.

    Se utiliza para mostrar información básica del cliente
    dentro de la oportunidad.
    """

    class Meta:
        model = Cliente
        fields = ["id", "nombre"]


class OportunidadSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Oportunidad.

    Se encarga de:

    - Convertir datos JSON <-> modelo Oportunidad
    - Validar que el cliente pertenece a la empresa del usuario
    - Garantizar aislamiento multiempresa
    - Asignar empresa y usuario_responsable automáticamente
    """

    cliente_detalle = ClienteSimpleSerializer(
        source="cliente",
        read_only=True
    )

    class Meta:
        model = Oportunidad
        fields = "__all__"
        read_only_fields = ["empresa", "usuario_responsable", "fecha_creacion"]

    def validate_cliente(self, value):
        """
        Valida que el cliente pertenece a la empresa del usuario.

        Evita que un usuario asigne clientes de otra empresa
        a una oportunidad de la suya.
        """
        request = self.context.get("request")
        if not request:
            return value

        if value.empresa != request.user.empresa:
            raise serializers.ValidationError(
                "El cliente no pertenece a tu empresa."
            )
        return value

    def validate_fecha_cierre_prevista(self, value):
        from django.utils import timezone

        if value and value.date() < timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de cierre no puede ser anterior a hoy."
            )
        return value

    def validate(self, data):
        estado = data.get("estado", getattr(self.instance, "estado", None))
        valor_estimado = data.get(
            "valor_estimado",
            getattr(self.instance, "valor_estimado", None)
        )
        probabilidad = data.get(
            "probabilidad",
            getattr(self.instance, "probabilidad", None)
        )

        if estado in ["ganada", "perdida"]:
            if valor_estimado is None:
                raise serializers.ValidationError(
                    "Para cerrar una oportunidad debes indicar un valor estimado."
                )
            if probabilidad is None:
                raise serializers.ValidationError(
                    "Para cerrar una oportunidad debes indicar una probabilidad."
                )

        return data
    

class ActividadSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo Actividad.

    Se encarga de:

    - Convertir datos JSON <-> modelo Actividad
    - Validar datos básicos antes de guardar
    - Mantener integridad en entorno multiempresa

    Notas importantes:
    - La empresa NO se envía desde el cliente
    - El usuario NO se envía desde el cliente
    - Ambos se asignan automáticamente en la vista
    """

    class Meta:
        model = Actividad
        fields = "__all__"

        # Estos campos se gestionan en backend
        read_only_fields = ["empresa", "usuario"]

    def validate(self, data):
        """
        Validación personalizada.

        Reglas:
        - La actividad debe tener fecha
        - Si se asigna cliente, debe pertenecer a la empresa del usuario
        - Si se asigna oportunidad, debe pertenecer a la empresa
        """

        request = self.context.get("request")

        if not request:
            return data

        empresa = request.user.empresa

        cliente = data.get("cliente")
        oportunidad = data.get("oportunidad")

        # Validar cliente
        if cliente and cliente.empresa != empresa:
            raise serializers.ValidationError(
                "El cliente no pertenece a tu empresa."
            )

        # Validar oportunidad
        if oportunidad and oportunidad.empresa != empresa:
            raise serializers.ValidationError(
                "La oportunidad no pertenece a tu empresa."
            )

        return data
