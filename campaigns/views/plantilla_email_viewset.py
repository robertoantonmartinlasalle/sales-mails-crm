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
    - Cada usuario solo accede a las plantillas de su empresa
    - Usamos TenantManager para centralizar lógica y logging
    """

    serializer_class = PlantillaEmailSerializer
    permission_classes = [IsAuthenticated, PermisosPorRol]

    def get_queryset(self):
        """

        Utilizamos el TenantManager para filtrar por empresa
        y además registrar logs automáticamente.

        Esto evita repetir lógica y nos da trazabilidad.
        """
        return PlantillaEmail.objects.for_empresa(
            self.request.user.empresa
        )

    def perform_create(self, serializer):
        """

        Asignamos automáticamente la empresa del usuario autenticado.

        Nunca permitimos que el cliente envíe la empresa,
        evitando manipulaciones y garantizando aislamiento.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )

    def create(self, request, *args, **kwargs):
        """
        Soporte para:
        - Crear una plantilla
        - Crear múltiples plantillas (bulk)

        Detectamos si request.data es una lista o un objeto.
        """

        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(
            data=request.data,
            many=is_many
        )

        serializer.is_valid(raise_exception=True)

        
        # En ambos casos usamos perform_create para mantener consistencia
        if is_many:
            for item in serializer.validated_data:
                item["empresa"] = request.user.empresa

            serializer.save()
        else:
            self.perform_create(serializer)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )