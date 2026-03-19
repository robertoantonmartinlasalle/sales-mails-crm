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
    """

    serializer_class = CampaignSendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Devuelve todos los envíos.

        (Más adelante podremos filtrar por empresa a través del cliente).
        """
        return CampaignSend.objects.all()