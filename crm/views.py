from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from crm.models import Oportunidad
from crm.serializers import OportunidadSerializer
from crm.models import Actividad
from crm.serializers import ActividadSerializer


"""
NOTA DE DISEÑO

En este módulo no se ha separado la lógica en múltiples archivos
(vistas y serializers) para evitar cambios innecesarios, ya que
el backend ya está integrado con el frontend.

Se ha priorizado mantener estabilidad y reducir riesgos,
dejando ambas clases (Oportunidad y Actividad) en el mismo archivo.

Como mejora futura, se podría modularizar siguiendo la estructura
del resto del proyecto para mejorar mantenibilidad.
"""

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



class ActividadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar actividades comerciales.

    Permite:

    - Listar actividades de la empresa
    - Crear nuevas actividades
    - Editar actividades existentes
    - Eliminar actividades

    Características importantes:

    - Cada usuario SOLO accede a actividades de su empresa
    - Se mantiene aislamiento multiempresa
    - Se puede filtrar por cliente u oportunidad en el futuro
    """

    serializer_class = ActividadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra las actividades por la empresa del usuario autenticado.

        También optimiza consultas con select_related para:
        - cliente
        - oportunidad
        - usuario

        Esto mejora el rendimiento en listados.
        """

        qs = Actividad.objects.for_empresa(
            self.request.user.empresa
        ).select_related("cliente", "oportunidad", "usuario")

        # 🔎 Filtros opcionales (muy útiles para el CRM)
        cliente_id = self.request.query_params.get("cliente")
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)

        oportunidad_id = self.request.query_params.get("oportunidad")
        if oportunidad_id:
            qs = qs.filter(oportunidad_id=oportunidad_id)

        return qs

    def perform_create(self, serializer):
        """
        Asigna automáticamente:

        - empresa → del usuario autenticado
        - usuario → usuario que crea la actividad

        Esto evita manipulación desde frontend y mantiene integridad.
        """

        serializer.save(
            empresa=self.request.user.empresa,
            usuario=self.request.user
        )

    def perform_update(self, serializer):
        """
        Garantiza que la empresa no cambia en una actualización.

        Evita que una actividad se pueda mover a otra empresa.
        """

        serializer.save(
            empresa=self.request.user.empresa
        )