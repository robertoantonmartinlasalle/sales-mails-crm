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

    Todo filtrado por empresa (multiempresa).
    """

    serializer_class = CampanaEmailSerializer
    permission_classes = [IsAuthenticated, PermisosPorRol]

    def get_queryset(self):
        """
        Devolvemos únicamente las campañas
        de la empresa del usuario autenticado.
        """
        return CampanaEmail.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        """
        Asignamos automáticamente la empresa al crear.

        El usuario NO puede definirla manualmente.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )