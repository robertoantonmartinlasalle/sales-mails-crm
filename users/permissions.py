from rest_framework.permissions import BasePermission


class IsAdminEmpresa(BasePermission):
    """
    Permiso para permitir solo administradores de empresa.
    """

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        # Versión segura (evita crash si rol es None)
        return (
            request.user.rol and
            request.user.rol.nombre == "Administrador"
        )