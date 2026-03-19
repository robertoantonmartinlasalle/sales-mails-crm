from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from campaigns.models.plantillaemail import PlantillaEmail
from campaigns.serializers.plantilla_email_serializer import PlantillaEmailSerializer


class PlantillaEmailViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar plantillas de email.

    Permite:
    - Listar plantillas
    - Crear plantillas
    - Editar plantillas
    - Eliminar plantillas
    """

    serializer_class = PlantillaEmailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Devuelve todas las plantillas.

        En este caso no filtramos por empresa (por ahora),
        ya que las plantillas pueden ser reutilizables.
        """
        return PlantillaEmail.objects.all()