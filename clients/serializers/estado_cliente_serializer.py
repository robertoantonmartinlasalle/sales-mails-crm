from rest_framework import serializers
from clients.models import EstadoCliente


class EstadoClienteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EstadoCliente
        fields = "__all__"
        read_only_fields = ["empresa"]

    def validate(self, data):
        """
        Validación personalizada para evitar duplicados
        dentro de la misma empresa.

        No queremos que una empresa tenga dos estados con el mismo nombre.
        """

        request = self.context.get("request")

        # Seguridad: si por algún motivo no hay request, evitamos error
        if not request:
            return data

        empresa = request.user.empresa
        nombre = data.get("nombre")

        # Comprobamos si ya existe ese nombre en la misma empresa
        if EstadoCliente.objects.filter(
            empresa=empresa,
            nombre=nombre
        ).exists():
            raise serializers.ValidationError(
                "Ya existe un estado con este nombre en tu empresa."
            )

        return data