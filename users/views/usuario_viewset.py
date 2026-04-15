from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.models.usuario import Usuario
from users.serializers.usuario_serializer import UsuarioSerializer
from users.permissions import IsAdminEmpresa


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios.

    Permite:
    - Listar usuarios
    - Crear usuarios
    - Editar usuarios
    - Eliminar usuarios

    Reglas de negocio:
    - Todos los usuarios pertenecen a una empresa
    - Cada usuario solo puede ver usuarios de su empresa (multiempresa)
    - Solo los administradores pueden crear, editar o eliminar usuarios
    """

    serializer_class = UsuarioSerializer

    # =========================================================
    # QUERYSET MULTIEMPRESA
    # =========================================================
    def get_queryset(self):
        """
        Filtramos los usuarios por empresa utilizando TenantManager.

        De esta forma evitamos repetir:
            Usuario.objects.filter(empresa=...)

        Y centralizamos la lógica multiempresa en un solo punto.

        IMPORTANTE:
        Esto garantiza que un usuario SOLO vea datos de su empresa.
        """
        return Usuario.objects.for_empresa(
            self.request.user.empresa
        )

    # =========================================================
    # PERMISOS DINÁMICOS
    # =========================================================
    def get_permissions(self):
        """
        Definimos permisos según la acción:

        - Lectura (list, retrieve):
            → cualquier usuario autenticado

        - Escritura (create, update, delete):
            → solo administradores de empresa
        """

        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminEmpresa()]

        return [IsAuthenticated()]

    # =========================================================
    # CREACIÓN SEGURA (MULTIEMPRESA)
    # =========================================================
    def perform_create(self, serializer):
        """
        Asignamos automáticamente la empresa del usuario autenticado.

        Esto evita que el cliente pueda enviar manualmente una empresa distinta,
        lo que sería un problema de seguridad en un sistema multiempresa.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )

    # =========================================================
    # UPDATE SEGURO
    # =========================================================
    def perform_update(self, serializer):
        """
        Nos aseguramos de que la empresa NO se pueda modificar.

        Aunque el campo ya es read_only en el serializer,
        reforzamos la seguridad desde la vista.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )