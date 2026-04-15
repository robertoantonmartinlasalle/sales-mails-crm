from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models.rol import Rol  # Importamos constantes de roles


class IsAdminEmpresa(BasePermission):
    """
    Permite el acceso únicamente a usuarios con rol de administrador.

    Se utiliza en operaciones críticas como:
    - Crear usuarios
    - Editar usuarios
    - Eliminar usuarios
    """

    def has_permission(self, request, view):

        # 1. El usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Validamos que el usuario tenga rol y que sea ADMIN
        return (
            request.user.rol and
            request.user.rol.nombre == Rol.ADMIN
        )


class PermisosPorRol(BasePermission):
    """
    Permisos basados en el rol del usuario dentro del CRM.

    Reglas:
    - Administrador → acceso total
    - Comercial → puede leer, crear y editar (no eliminar)
    - Otros → solo lectura

    IMPORTANTE:
    Usamos constantes del modelo Rol en lugar de strings
    para evitar errores y mejorar la mantenibilidad.
    """

    def has_permission(self, request, view):

        # 1. Usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Obtenemos el rol de forma segura
        rol = request.user.rol.nombre if request.user.rol else None

        # =========================================================
        # ADMIN → acceso total
        # =========================================================
        if rol == Rol.ADMIN:
            return True

        # =========================================================
        # COMERCIAL → lectura + escritura (sin delete)
        # =========================================================
        if rol == Rol.COMERCIAL:
            # Métodos seguros (GET, HEAD, OPTIONS)
            if request.method in SAFE_METHODS:
                return True

            # Métodos de escritura permitidos
            if request.method in ["POST", "PUT", "PATCH"]:
                return True

            # DELETE no permitido
            return False

        # =========================================================
        # OTROS ROLES → solo lectura
        # =========================================================
        return request.method in SAFE_METHODS