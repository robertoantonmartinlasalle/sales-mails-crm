from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils import timezone

from campaigns.models.campaignsend import CampaignSend
from campaigns.serializers.campaign_send_serializer import CampaignSendSerializer

from core.services.email_service import send_email  # Importamos el servicio de envío de emails


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

    Además incluye:
    - Acción personalizada para enviar campañas
    """

    serializer_class = CampaignSendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CampaignSend.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        serializer.save(
            empresa=self.request.user.empresa
        )

    @action(detail=True, methods=["post"])
    def enviar(self, request, pk=None):
        """
        Acción personalizada para enviar una campaña.

        Flujo:

        1. Obtener el envío
        2. Validar estado
        3. Construir email desde plantilla
        4. Enviar email real
        5. Actualizar estado y fecha
        """

        envio = self.get_object()

        # Solo permitir envío si está pendiente
        if envio.estado != "pendiente":
            return Response(
                {"error": "Este envío ya fue procesado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        """
        Obtenemos la plantilla asociada a la campaña.

        Flujo:
        CampaignSend → CampanaEmail → PlantillaEmail
        """
        plantilla = envio.campana.plantilla

        """
        Construimos el mensaje sustituyendo variables dinámicas.

        De momento soportamos {{nombre}}, pero esto se podrá ampliar.
        """
        mensaje = plantilla.cuerpo.replace(
            "{{nombre}}",
            envio.cliente.nombre
        )

        """
        Ejecutamos el envío real utilizando nuestro servicio de email.
        """
        enviado = send_email(
            to=envio.cliente.email,
            subject=plantilla.asunto,
            message=mensaje
        )

        # 🚨 Si falla el envío
        if not enviado:
            envio.estado = "error"
            envio.save()

            return Response(
                {"error": "Error al enviar el email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        
        envio.estado = "enviado"
        envio.fecha_envio = timezone.now()
        envio.save()

        return Response(
            {"message": "Campaña enviada correctamente."},
            status=status.HTTP_200_OK
        )