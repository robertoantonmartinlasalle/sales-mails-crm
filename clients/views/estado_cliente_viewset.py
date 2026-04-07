from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from clients.models import EstadoCliente
from clients.serializers.estado_cliente_serializer import EstadoClienteSerializer
from users.permissions import PermisosPorRol


class EstadoClienteViewSet(viewsets.ModelViewSet):
    """
    API para gestionar los estados de cliente.

    Todas las operaciones están limitadas a la empresa del usuario autenticado.
    """

    serializer_class = EstadoClienteSerializer
    permission_classes = [IsAuthenticated, PermisosPorRol]

    def get_queryset(self):
        """
        Devuelve únicamente los estados pertenecientes a la empresa del usuario.
        """
        return EstadoCliente.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        """
        Asigna automáticamente la empresa del usuario al crear el estado.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )