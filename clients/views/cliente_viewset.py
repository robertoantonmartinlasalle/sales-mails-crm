from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from clients.models import Cliente
from clients.models.actividad_cliente import ActividadCliente
from clients.serializers.cliente_serializer import ClienteSerializer
from clients.serializers.actividad_cliente_serializer import ActividadClienteSerializer
from users.permissions import PermisosPorRol


def _registrar_actividad(cliente, usuario, tipo, descripcion):
    ActividadCliente.objects.create(
        cliente=cliente,
        empresa=cliente.empresa,
        usuario=usuario,
        tipo=tipo,
        descripcion=descripcion,
    )


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
        cliente = serializer.save(
            empresa=self.request.user.empresa
        )
        _registrar_actividad(
            cliente=cliente,
            usuario=self.request.user,
            tipo="cliente_creado",
            descripcion=f"Cliente '{cliente.nombre}' creado.",
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
        Devuelve 404 si no existe, no pertenece a la empresa o ya está inactivo.
        """
        try:
            cliente = Cliente.objects.get(
                id=kwargs["pk"],
                empresa=request.user.empresa,
                activo=True,
            )
        except Cliente.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        cliente.activo = False
        cliente.save(update_fields=["activo"])

        _registrar_actividad(
            cliente=cliente,
            usuario=request.user,
            tipo="cliente_eliminado",
            descripcion=f"Cliente '{cliente.nombre}' marcado como inactivo.",
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """
        Actualiza el cliente. Si cambia estado_cliente, registra actividad específica.
        En cualquier otro cambio, registra actividad genérica de actualización.
        """
        partial = kwargs.pop("partial", False)

        try:
            cliente = Cliente.objects.get(
                id=kwargs["pk"],
                empresa=request.user.empresa,
            )
        except Cliente.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        estado_anterior = cliente.estado_cliente

        serializer = self.get_serializer(cliente, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        cliente_actualizado = serializer.save()

        estado_nuevo = cliente_actualizado.estado_cliente

        if estado_anterior != estado_nuevo:
            _registrar_actividad(
                cliente=cliente_actualizado,
                usuario=request.user,
                tipo="estado_cambiado",
                descripcion=(
                    f"Estado cambiado de '{estado_anterior.nombre}' "
                    f"a '{estado_nuevo.nombre}'."
                ),
            )
        else:
            _registrar_actividad(
                cliente=cliente_actualizado,
                usuario=request.user,
                tipo="cliente_actualizado",
                descripcion=f"Cliente '{cliente_actualizado.nombre}' actualizado.",
            )

        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="inactive")
    def inactive(self, request):
        """
        Devuelve los clientes inactivos (soft deleted) de la empresa.
        """
        clientes = Cliente.objects.filter(
            empresa=request.user.empresa,
            activo=False,
        ).order_by("-fecha_creacion")
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """
        Restaura un cliente inactivo. Devuelve el cliente actualizado.
        """
        try:
            cliente = Cliente.objects.get(
                id=pk,
                empresa=request.user.empresa,
                activo=False,
            )
        except Cliente.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        cliente.activo = True
        cliente.save(update_fields=["activo"])

        _registrar_actividad(
            cliente=cliente,
            usuario=request.user,
            tipo="cliente_restaurado",
            descripcion=f"Cliente '{cliente.nombre}' restaurado.",
        )

        serializer = self.get_serializer(cliente)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="activity")
    def activity(self, request, pk=None):
        """
        Devuelve el historial de actividad de un cliente, ordenado por fecha descendente.
        """
        if not Cliente.objects.filter(
            id=pk,
            empresa=request.user.empresa,
        ).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        actividades = ActividadCliente.objects.filter(
            cliente_id=pk,
            empresa=request.user.empresa,
        )
        serializer = ActividadClienteSerializer(actividades, many=True)
        return Response(serializer.data)