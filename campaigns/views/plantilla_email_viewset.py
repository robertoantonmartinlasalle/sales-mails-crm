from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from campaigns.models.plantillaemail import PlantillaEmail
from campaigns.serializers.plantilla_email_serializer import PlantillaEmailSerializer
from users.permissions import PermisosPorRol

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
    permission_classes = [IsAuthenticated, PermisosPorRol]

    def get_queryset(self):
        """
        Devuelve todas las plantillas.

        En este caso no filtramos por empresa (por ahora),
        ya que las plantillas pueden ser reutilizables.
        """
        return PlantillaEmail.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Sobreescribimos el método create para permitir:

        - Crear una única plantilla (comportamiento estándar)
        - Crear múltiples plantillas en una sola petición (bulk create)

        Detectamos si request.data es una lista o un objeto.
        """

        # Detectamos si es bulk (lista) o creación individual
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(
            data=request.data,
            many=is_many
        )

        serializer.is_valid(raise_exception=True)

        """
        Como las plantillas no están ligadas a empresa,
        simplemente guardamos directamente.
        """
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )