from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from campaigns.models.campanaemail import CampanaEmail
from campaigns.serializers.campana_email_serializer import CampanaEmailSerializer
from users.permissions import PermisosPorRol


class CampanaEmailViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar campañas de email.

    Permite:
    - Listar campañas
    - Crear campañas
    - Editar campañas
    - Eliminar campañas
    - Cada usuario solo puede acceder a sus campañas
    - Se utiliza TenantManager para filtrar automáticamente
    """

    serializer_class = CampanaEmailSerializer
    permission_classes = [IsAuthenticated, PermisosPorRol]

    def get_queryset(self):
        """

        Filtramos todas las campañas por la empresa del usuario.

        Usamos TenantManager:
        - Centraliza la lógica
        - Añade logging automático
        """
        return CampanaEmail.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        """
        Asignamos automáticamente la empresa al crear la campaña.

        Nunca permitimos que el cliente envíe este campo,
        evitando manipulación y garantizando aislamiento.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )