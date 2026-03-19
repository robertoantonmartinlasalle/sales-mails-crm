from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils import timezone

from campaigns.models.campaignsend import CampaignSend
from campaigns.serializers.campaign_send_serializer import CampaignSendSerializer

from core.services.email_service import send_email  # Servicio de envío de emails


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
    - Envío individual (1 cliente)
    - Envío masivo (todos los pendientes)
    """

    serializer_class = CampaignSendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Devolvemos únicamente los envíos
        de la empresa del usuario autenticado.

        Esto garantiza aislamiento multiempresa.
        """
        return CampaignSend.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        """
        Asignamos automáticamente la empresa.

        El usuario NO puede definirla manualmente,
        se obtiene del usuario autenticado.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )

    # =========================================================
    # ENVÍO INDIVIDUAL
    # =========================================================
    @action(detail=True, methods=["post"], url_path="enviar")
    def enviar(self, request, pk=None):
        """
        Acción personalizada para enviar UNA campaña a UN cliente.

        Flujo:

        1. Obtener el envío
        2. Validar que esté en estado "pendiente"
        3. Obtener plantilla asociada a la campaña
        4. Construir mensaje dinámico
        5. Enviar email real
        6. Actualizar estado y fecha
        """

        envio = self.get_object()

        # Solo permitir envío si está pendiente
        if envio.estado != "pendiente":
            return Response(
                {"error": "Este envío ya fue procesado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtenemos plantilla
        plantilla = envio.campana.plantilla

        # Construimos mensaje dinámico
        mensaje = plantilla.cuerpo.replace(
            "{{nombre}}",
            envio.cliente.nombre
        )

        # Enviamos email
        enviado = send_email(
            to=envio.cliente.email,
            subject=plantilla.asunto,
            message=mensaje
        )

        # Si falla
        if not enviado:
            envio.estado = "error"
            envio.save()

            return Response(
                {"error": "Error al enviar el email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Si todo OK
        envio.estado = "enviado"
        envio.fecha_envio = timezone.now()
        envio.save()

        return Response(
            {"message": "Campaña enviada correctamente."},
            status=status.HTTP_200_OK
        )

    # =========================================================
    # ENVÍO MASIVO 
    # =========================================================
    @action(detail=False, methods=["post"], url_path="enviar-masivo")
    def enviar_masivo(self, request):
        """
        Acción personalizada para enviar TODAS las campañas pendientes.

        IMPORTANTE:
        - Este endpoint se registra como:
          /api/campaign-sends/enviar-masivo/
        - Solo acepta POST

        Flujo:

        1. Obtener todos los envíos pendientes de la empresa
        2. Iterar sobre cada envío
        3. Construir mensaje dinámico
        4. Enviar email
        5. Actualizar estado (enviado / error)
        6. Devolver resumen
        """

        envios = CampaignSend.objects.for_empresa(
            request.user.empresa
        ).filter(estado="pendiente")

        total = envios.count()
        enviados = 0
        errores = 0

        for envio in envios:

            plantilla = envio.campana.plantilla

            mensaje = plantilla.cuerpo.replace(
                "{{nombre}}",
                envio.cliente.nombre
            )

            enviado_ok = send_email(
                to=envio.cliente.email,
                subject=plantilla.asunto,
                message=mensaje
            )

            if enviado_ok:
                envio.estado = "enviado"
                envio.fecha_envio = timezone.now()
                enviados += 1
            else:
                envio.estado = "error"
                errores += 1

            envio.save()

        return Response(
            {
                "total": total,
                "enviados": enviados,
                "errores": errores
            },
            status=status.HTTP_200_OK
        )