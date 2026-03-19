from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from campaigns.models.campanaemail import CampanaEmail
from campaigns.serializers.campana_email_serializer import CampanaEmailSerializer


class CampanaEmailViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar campañas de email.

    Permite:
    - Listar campañas
    - Crear campañas
    - Editar campañas
    - Eliminar campañas
    """

    serializer_class = CampanaEmailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Devuelve todas las campañas.

        (De momento no filtramos por empresa, pero se podrá añadir).
        """
        return CampanaEmail.objects.all()