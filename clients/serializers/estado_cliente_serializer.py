from rest_framework import serializers
from clients.models import EstadoCliente


class EstadoClienteSerializer(serializers.ModelSerializer):
    """
    Serializer del modelo EstadoCliente.

    Se encarga de:
    - Serializar/deserializar los datos
    - Aplicar validaciones personalizadas
    - Garantizar que no haya estados duplicados por empresa
    """

    class Meta:
        model = EstadoCliente
        fields = "__all__"

        # La empresa no se envía desde el cliente,
        # se asigna automáticamente en la vista
        read_only_fields = ["empresa"]

    def validate(self, data):
        """
        Validación personalizada para evitar duplicados
        dentro de la misma empresa.

        Regla de negocio:
        - Una empresa NO puede tener dos estados con el mismo nombre.
        """

        request = self.context.get("request")

        # Seguridad: si por algún motivo no hay request, no validamos
        # (esto puede pasar en tests o usos internos)
        if not request:
            return data

        empresa = request.user.empresa

        # Soportamos tanto CREATE como UPDATE (incluyendo PATCH)
        nombre = data.get(
            "nombre",
            self.instance.nombre if self.instance else None
        )

        # Query base: buscamos estados con mismo nombre en la misma empresa
        qs = EstadoCliente.objects.filter(
            empresa=empresa,
            nombre=nombre
        )

        # Si estamos editando (UPDATE), excluimos el propio objeto
        # para no detectarlo como duplicado de sí mismo
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        # Si existe algún duplicado salta un error
        if qs.exists():
            raise serializers.ValidationError(
                "Ya existe un estado con este nombre en tu empresa."
            )

        return data