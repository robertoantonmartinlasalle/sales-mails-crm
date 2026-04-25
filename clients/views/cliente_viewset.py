from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from clients.models import Cliente
from clients.serializers.cliente_serializer import ClienteSerializer
from users.permissions import PermisosPorRol


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
    permission_classes = [IsAuthenticated, PermisosPorRol]

    def get_queryset(self):
        """
        Devuelve únicamente los clientes activos de la empresa
        del usuario autenticado.
        """
        return Cliente.objects.for_empresa(
            self.request.user.empresa
        ).filter(activo=True)

    def perform_create(self, serializer):
        """
        Asigna automáticamente la empresa del usuario autenticado
        al crear un cliente.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )

    def create(self, request, *args, **kwargs):
        """
        Sobreescribimos el método create para permitir:

        - Crear un único cliente (comportamiento estándar)
        - Crear múltiples clientes en una sola petición (bulk create)

        Detectamos si request.data es una lista o un objeto.
        """

        # Si recibimos una lista → creación múltiple
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(
            data=request.data,
            many=is_many
        )

        serializer.is_valid(raise_exception=True)

        """
        IMPORTANTE:

        En multiempresa NO confiamos en el frontend.
        La empresa SIEMPRE se asigna desde el usuario autenticado.
        """

        if is_many:
            serializer.save(
                empresa=self.request.user.empresa
            )
        else:
            self.perform_create(serializer)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: marca el cliente como inactivo en lugar de borrarlo.
        Usa update() para evitar cargar el objeto en memoria.
        Devuelve 404 si no existe o no pertenece a la empresa.
        """
        updated = Cliente.objects.filter(
            id=kwargs["pk"],
            empresa=self.request.user.empresa,
            activo=True,
        ).update(activo=False)

        if not updated:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)