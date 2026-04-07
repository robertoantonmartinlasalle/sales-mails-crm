from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminEmpresa(BasePermission):
    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        return (
            request.user.rol and
            request.user.rol.nombre == "Administrador"
        )



class PermisosPorRol(BasePermission):
    """
    Permisos basados en el rol del usuario dentro del CRM.

    - Administrador → acceso total
    - Comercial → puede leer, crear y editar (no eliminar)
    - Otros → solo lectura
    """

    def has_permission(self, request, view):

        # 1. Usuario debe estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Obtener rol de forma segura
        rol = request.user.rol.nombre if request.user.rol else None

        # 3. Administrador → todo permitido
        if rol == "Administrador":
            return True

        # 4. Comercial → lectura + escritura (sin delete)
        if rol == "Comercial":
            if request.method in SAFE_METHODS:
                return True
            if request.method in ["POST", "PUT", "PATCH"]:
                return True
            return False

        # 5. Otros → solo lectura
        return request.method in SAFE_METHODS