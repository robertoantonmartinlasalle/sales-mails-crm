from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from crm.models import Oportunidad
from crm.serializers import OportunidadSerializer


class OportunidadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar oportunidades comerciales.

    Permite:
    - Listar oportunidades de la empresa
    - Crear oportunidades
    - Editar oportunidades (incluyendo cambio de estado)
    - Eliminar oportunidades
    - Cada usuario solo accede a las oportunidades de su empresa
    """

    serializer_class = OportunidadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra las oportunidades por la empresa del usuario autenticado.

        Opcionalmente filtra por cliente si se pasa ?cliente=<id>.
        """
        qs = Oportunidad.objects.for_empresa(
            self.request.user.empresa
        ).select_related("cliente", "usuario_responsable").order_by("estado", "-fecha_creacion")

        cliente_id = self.request.query_params.get("cliente")
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)

        return qs

    def perform_create(self, serializer):
        """
        Asigna empresa y usuario_responsable automáticamente al crear.

        Nunca se permite que el cliente envíe estos campos,
        garantizando el aislamiento multiempresa.
        """
        serializer.save(
            empresa=self.request.user.empresa,
            usuario_responsable=self.request.user,
        )

    def perform_update(self, serializer):
        """
        Garantiza que la empresa no cambia en una actualización.
        """
        serializer.save(
            empresa=self.request.user.empresa,
        )
