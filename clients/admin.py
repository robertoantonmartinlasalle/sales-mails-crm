from django.contrib import admin

from .models import Cliente
from .models.estadoCliente import EstadoCliente


# =========================================================
# ADMIN DE ESTADO CLIENTE
# =========================================================
@admin.register(EstadoCliente)
class EstadoClienteAdmin(admin.ModelAdmin):
    """
    Administración del modelo EstadoCliente.

    Este modelo define los diferentes estados en los que puede
    encontrarse un cliente (activo, prospecto, inactivo, etc.).

    Está ligado a empresa (multiempresa), por lo que cada empresa
    puede tener sus propios estados personalizados.
    """

    # =========================================================
    # LISTADO
    # =========================================================
    list_display = (
        "nombre",
        "orden",
        "empresa",
    )

    # =========================================================
    # BUSCADOR
    # =========================================================
    search_fields = ("nombre",)

    # =========================================================
    # FILTROS
    # =========================================================
    list_filter = ("empresa",)

    # =========================================================
    # ORDENACIÓN
    # =========================================================
    ordering = ("orden", "nombre")

    # =========================================================
    # FORMULARIO
    # =========================================================
    fieldsets = (
        ("Información del estado", {
            "fields": (
                "nombre",
                "descripcion",
                "orden",
                "empresa",
            )
        }),
    )


# =========================================================
# ADMIN DE CLIENTE
# =========================================================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Administración del modelo Cliente.

    Este admin permite gestionar los clientes del CRM de forma visual,
    facilitando la consulta, filtrado y edición de datos.

    Incluye:

    - Información básica del cliente
    - Estado del cliente
    - Datos de contacto
    - Relación con empresa (multiempresa)

    Es una de las entidades principales del sistema.
    """

    # =========================================================
    # LISTADO PRINCIPAL
    # =========================================================
    list_display = (
        "nombre",
        "tipo",
        "estado_cliente",
        "email",
        "telefono",
        "empresa",
        "activo",
    )

    # =========================================================
    # BUSCADOR
    # =========================================================
    search_fields = (
        "nombre",
        "email",
        "telefono",
        "nif",
    )

    # =========================================================
    # FILTROS LATERALES
    # =========================================================
    list_filter = (
        "tipo",
        "estado_cliente",
        "empresa",
        "activo",
    )

    # =========================================================
    # ORDENACIÓN
    # =========================================================
    ordering = ("-fecha_creacion",)

    # =========================================================
    # CAMPOS SOLO LECTURA
    # =========================================================
    readonly_fields = ("fecha_creacion",)

    # =========================================================
    # FORMULARIO ORGANIZADO
    # =========================================================
    fieldsets = (
        ("Información básica", {
            "fields": (
                "nombre",
                "tipo",
                "estado_cliente",
                "activo",
            )
        }),
        ("Contacto", {
            "fields": (
                "email",
                "telefono",
            )
        }),
        ("Dirección", {
            "fields": (
                "direccion",
                "ciudad",
                "pais",
            )
        }),
        ("Información fiscal", {
            "fields": (
                "nif",
                "empresa",
            )
        }),
        ("Auditoría", {
            "fields": (
                "fecha_creacion",
            )
        }),
    )