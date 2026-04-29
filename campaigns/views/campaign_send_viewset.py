from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils import timezone

from campaigns.models.campaignsend import CampaignSend
from campaigns.models.plantillaemail import PlantillaEmail
from campaigns.serializers.campaign_send_serializer import CampaignSendSerializer

from clients.models import Cliente
from clients.models.actividad_cliente import ActividadCliente

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

        Acepta ?campana=<id> para filtrar por campaña.
        """
        qs = CampaignSend.objects.for_empresa(
            self.request.user.empresa
        )

        campana_id = self.request.query_params.get("campana")
        if campana_id:
            qs = qs.filter(campana_id=campana_id)

        return qs

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

        ActividadCliente.objects.create(
            cliente=envio.cliente,
            empresa=envio.cliente.empresa,
            usuario=request.user,
            tipo="email_enviado",
            descripcion=f"Email de campaña enviado: '{asunto}'",
        )

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

        campana_id = request.data.get("campana_id")
        if campana_id:
            envios = envios.filter(campana_id=campana_id)

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

                ActividadCliente.objects.create(
                    cliente=envio.cliente,
                    empresa=envio.cliente.empresa,
                    usuario=request.user,
                    tipo="email_enviado",
                    descripcion=f"Email de campaña enviado: '{asunto}'",
                )
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

    # =========================================================
    # ENVÍO DIRECTO (sin campaña previa)
    # =========================================================
    @action(detail=False, methods=["post"], url_path="send-direct")
    def send_direct(self, request):
        """
        Envía un email directo a una lista de clientes sin necesidad
        de crear una CampanaEmail previamente.

        Endpoint:
            POST /api/campaign-sends/send-direct/

        Payload:
            {
                "cliente_ids": [1, 2, 3],
                "asunto": "...",
                "mensaje": "..."
            }

        Validaciones:
            - cliente_ids, asunto y mensaje son obligatorios
            - Los clientes deben pertenecer a la empresa del usuario
            - Los clientes deben estar activos
            - El cliente debe tener email

        Respuesta:
            {
                "total": N,
                "enviados": N,
                "errores": [{"cliente_id": X, "error": "..."}]
            }
        """
        cliente_ids = request.data.get("cliente_ids", [])
        plantilla_id = request.data.get("plantilla_id")
        asunto = request.data.get("asunto", "").strip()
        mensaje = request.data.get("mensaje", "").strip()

        if not cliente_ids:
            return Response(
                {"error": "cliente_ids es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resolver asunto y mensaje: plantilla tiene prioridad como base,
        # pero asunto/mensaje del payload hacen override si se proporcionan.
        if plantilla_id:
            try:
                plantilla = PlantillaEmail.objects.get(
                    id=plantilla_id,
                    empresa=request.user.empresa,
                )
            except PlantillaEmail.DoesNotExist:
                return Response(
                    {"error": "Plantilla no encontrada o no pertenece a tu empresa"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            asunto_final = asunto or plantilla.asunto
            mensaje_final = mensaje or plantilla.cuerpo
        else:
            asunto_final = asunto
            mensaje_final = mensaje

        if not asunto_final or not mensaje_final:
            return Response(
                {"error": "Debes proporcionar asunto y mensaje, o seleccionar una plantilla"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        clientes = Cliente.objects.filter(
            id__in=cliente_ids,
            empresa=request.user.empresa,
            activo=True,
        )

        total = len(cliente_ids)
        enviados = 0
        errores = []

        for cliente in clientes:
            if not cliente.email:
                errores.append({
                    "cliente_id": cliente.id,
                    "error": "Cliente sin email",
                })
                continue

            # Personalizamos {{nombre}} si aparece en el mensaje
            mensaje_personalizado = mensaje_final.replace("{{nombre}}", cliente.nombre)
            asunto_personalizado = asunto_final.replace("{{nombre}}", cliente.nombre)

            ok, error_msg = send_email(
                to=cliente.email,
                subject=asunto_personalizado,
                message=mensaje_personalizado,
            )

            if ok:
                enviados += 1
                ActividadCliente.objects.create(
                    cliente=cliente,
                    empresa=cliente.empresa,
                    usuario=request.user,
                    tipo="email_enviado",
                    descripcion=f"Email enviado: '{asunto_personalizado}'",
                )
            else:
                errores.append({
                    "cliente_id": cliente.id,
                    "error": error_msg,
                })

        return Response({
            "total": total,
            "enviados": enviados,
            "errores": errores,
        }, status=status.HTTP_200_OK)