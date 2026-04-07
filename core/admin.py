from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para el modelo Empresa.

    Este admin representa el núcleo del sistema multiempresa del CRM.

    Permite:

    - Visualizar todas las empresas registradas
    - Buscar empresas por nombre o identificadores
    - Organizar los datos de forma clara en el formulario
    - Controlar acciones sensibles como la eliminación

    Dado que Empresa es la entidad central del sistema, es importante
    restringir ciertas acciones para evitar pérdida de datos.
    """

    # =========================================================
    # CAMPOS VISIBLES EN EL LISTADO
    # =========================================================
    # Define qué columnas se muestran en la tabla principal del admin
    list_display = (
        "nombre",
        "id",
    )

    # =========================================================
    # BUSCADOR
    # =========================================================
    # Permite buscar empresas desde la barra superior
    search_fields = (
        "nombre",
        "id",
    )

    # =========================================================
    # ORDENACIÓN
    # =========================================================
    # Ordenamos las empresas por nombre alfabéticamente
    ordering = ("nombre",)

    # =========================================================
    # CAMPOS SOLO LECTURA
    # =========================================================
    # El ID no debe modificarse manualmente desde el admin
    readonly_fields = ("id",)

    # =========================================================
    # ORGANIZACIÓN DEL FORMULARIO
    # =========================================================
    # Separamos los campos en bloques para mejorar la experiencia
    fieldsets = (
        ("Información básica", {
            "fields": (
                "id",
                "nombre",
            )
        }),
    )

    # =========================================================
    # CONTROL DE BORRADO (MUY IMPORTANTE)
    # =========================================================
    def has_delete_permission(self, request, obj=None):
        """
        Controla si un usuario puede eliminar una empresa.

        En este caso, restringimos la eliminación únicamente
        a usuarios con privilegios de superusuario.

        Esto es fundamental en un sistema multiempresa, ya que
        eliminar una empresa podría implicar la eliminación
        de todos los datos relacionados (usuarios, clientes,
        campañas, etc.).

        Parámetros:
        - request: contiene información del usuario que hace la petición
        - obj: instancia concreta que se quiere eliminar (opcional)

        Retorna:
        - True → permite borrar
        - False → bloquea la acción de borrado
        """

        return request.user.is_superuser