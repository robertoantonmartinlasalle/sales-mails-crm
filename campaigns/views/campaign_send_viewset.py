from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils import timezone

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

    Además añadimos una acción personalizada:
    - enviar campaña
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

    # Definimos la acción
    @action(detail=True, methods=["post"])
    def enviar(self, request, pk=None):
        """
        Acción personalizada para enviar una campaña.

        Flujo:

        1. Obtener el envío
        2. Validar que está pendiente
        3. Simular envío
        4. Actualizar estado y fecha
        """

        envio = self.get_object()

        # 🔒 Solo permitir enviar si está pendiente
        if envio.estado != "pendiente":
            return Response(
                {"error": "Este envío ya fue procesado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Simulación (aquí luego irá send_email)
        print(f"Enviando email a {envio.cliente.email}")

        #  Actualización de estado
        envio.estado = "enviado"
        envio.fecha_envio = timezone.now()
        envio.save()

        return Response(
            {"message": "Campaña enviada correctamente."},
            status=status.HTTP_200_OK
        )