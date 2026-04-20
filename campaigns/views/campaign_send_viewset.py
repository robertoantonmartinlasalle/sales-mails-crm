from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils import timezone

from campaigns.models.campaignsend import CampaignSend
from campaigns.serializers.campaign_send_serializer import CampaignSendSerializer

from core.services.email_service import send_email

from users.permissions import PermisosPorRol


class CampaignSendViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los envíos de campañas.

    Representa el envío de una campaña a un cliente.

    Permite:
    - Listar envíos
    - Crear envíos
    - Editar envíos
    - Eliminar envíos
    - Cada usuario solo ve los envíos de su empresa
    - Filtrado automático con TenantManager

    Además incluye:
    - Envío individual
    - Envío masivo
    """

    serializer_class = CampaignSendSerializer
    permission_classes = [IsAuthenticated, PermisosPorRol]

    def get_queryset(self):
        """
        Filtramos todos los envíos por empresa.

        Usamos TenantManager para:
        - Evitar accesos cruzados
        - Añadir trazabilidad mediante logs
        """
        return CampaignSend.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        """
        Asignamos automáticamente la empresa del usuario autenticado.

        Nunca permitimos que el cliente la envíe.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )

    # =========================================================
    # ENVÍO INDIVIDUAL
    # =========================================================
    @action(detail=True, methods=["post"], url_path="send")
    def enviar(self, request, pk=None):
        """
        Acción personalizada para enviar UNA campaña a UN cliente.

        Flujo:

        1. Obtener envío
        2. Validar estado
        3. Validar email del cliente
        4. Construir mensaje dinámico (cuerpo + asunto)
        5. Enviar email
        6. Actualizar estado
        """

        envio = self.get_object()

        # Solo permitir si está pendiente
        if envio.estado != "pendiente":
            return Response(
                {"error": "Este envío ya fue procesado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar email
        if not envio.cliente or not envio.cliente.email:
            return Response(
                {"error": "El cliente no tiene email válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        plantilla = envio.campana.plantilla

        # =====================================================
        # Construcción del mensaje dinámico
        # =====================================================

        # Personalizamos el cuerpo del email
        mensaje = plantilla.cuerpo.replace(
            "{{nombre}}",
            envio.cliente.nombre
        )

        # Personalizamos el asunto
        asunto = plantilla.asunto.replace(
            "{{nombre}}",
            envio.cliente.nombre
        )

        # =====================================================
        # Envío real del email
        # =====================================================
        enviado, error_msg = send_email(
            to=envio.cliente.email,
            subject=asunto,   # ahora sí dinámico
            message=mensaje
        )

        # Manejo de error
        if not enviado:
            envio.estado = "error"
            envio.error_mensaje = error_msg
            envio.save()

            return Response(
                {"error": "Error al enviar el email."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Éxito
        envio.estado = "enviado"
        envio.fecha_envio = timezone.now()
        envio.error_mensaje = None
        envio.save()

        return Response(
            {"message": "Campaña enviada correctamente."},
            status=status.HTTP_200_OK
        )

    # =========================================================
    # ENVÍO MASIVO
    # =========================================================
    @action(detail=False, methods=["post"], url_path="send-bulk")
    def enviar_masivo(self, request):
        """
        Acción personalizada para enviar TODAS las campañas pendientes.

        Endpoint:
        POST /api/campaign-sends/send-bulk/

        Flujo:

        1. Obtener envíos pendientes
        2. Iterar sobre cada uno
        3. Construir mensaje dinámico
        4. Enviar email
        5. Actualizar estado
        6. Devolver resumen
        """

        envios = CampaignSend.objects.for_empresa(
            request.user.empresa
        ).filter(estado="pendiente")

        total = envios.count()
        enviados = 0
        errores = 0

        for envio in envios:

            # Validar email antes de enviar
            if not envio.cliente or not envio.cliente.email:
                envio.estado = "error"
                envio.error_mensaje = "Cliente sin email válido"
                envio.save()
                errores += 1
                continue

            plantilla = envio.campana.plantilla

            # =====================================================
            # Construcción del mensaje dinámico
            # =====================================================

            mensaje = plantilla.cuerpo.replace(
                "{{nombre}}",
                envio.cliente.nombre
            )

            
            asunto = plantilla.asunto.replace(
                "{{nombre}}",
                envio.cliente.nombre
            )

            # =====================================================
            # Envío del email
            # =====================================================
            enviado_ok, error_msg = send_email(
                to=envio.cliente.email,
                subject=asunto,   # ahora dinámico
                message=mensaje
            )

            if enviado_ok:
                envio.estado = "enviado"
                envio.fecha_envio = timezone.now()
                envio.error_mensaje = None
                enviados += 1
            else:
                envio.estado = "error"
                envio.error_mensaje = error_msg
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