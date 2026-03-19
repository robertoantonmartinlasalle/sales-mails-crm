from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from campaigns.models.campaignsend import CampaignSend
from campaigns.serializers.campaign_send_serializer import CampaignSendSerializer


class CampaignSendViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los envíos de campañas.

    Representa el envío de una campaña a un cliente.

    Permite:
    - Listar envíos
    - Crear envíos
    - Editar estado del envío
    - Eliminar envíos

    Todo filtrado por empresa (multiempresa).
    """

    serializer_class = CampaignSendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Devolvemos únicamente los envíos
        de la empresa del usuario autenticado.
        """
        return CampaignSend.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        """
        Asignamos automáticamente la empresa
        del usuario al crear un envío.

        El frontend NO puede decidir la empresa.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )