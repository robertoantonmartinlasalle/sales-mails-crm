from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from clients.models import Cliente
from clients.serializers.cliente_serializer import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar clientes.

    Permite:
    - Listar clientes
    - Crear clientes
    - Editar clientes
    - Eliminar clientes

    Todo filtrado por empresa (multiempresa).
    """

    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Devuelve únicamente los clientes de la empresa
        del usuario autenticado.
        """
        return Cliente.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        """
        Asigna automáticamente la empresa del usuario autenticado
        al crear un cliente.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )