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
    # QUERYSET MULTIEMPRESA (AQUÍ USAMOS TENANT MANAGER)
    # =========================================================
    def get_queryset(self):
        """
        Filtramos los usuarios por empresa utilizando TenantManager.

        En lugar de hacer:
            Usuario.objects.filter(empresa=...)

        Usamos:
            Usuario.objects.for_empresa(...)

        Ventajas:
        - Código más limpio
        - Reutilizable en todo el proyecto
        - Evita errores al repetir lógica

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

        - GET (list, retrieve):
            → cualquier usuario autenticado

        - POST, PUT, PATCH, DELETE:
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

        Esto evita que:
        - El cliente envíe manualmente otra empresa
        - Se creen usuarios en empresas ajenas

        Es una capa clave de seguridad.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )

    # =========================================================
    # (OPCIONAL PERO RECOMENDADO) UPDATE SEGURO
    # =========================================================
    def perform_update(self, serializer):
        """
        Nos aseguramos de que la empresa NO se pueda modificar
        al actualizar un usuario.

        Aunque el campo sea read_only en el serializer,
        esto añade una capa extra de seguridad.
        """
        serializer.save(
            empresa=self.request.user.empresa
        )