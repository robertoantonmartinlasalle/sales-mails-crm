from django.contrib import admin

from .models.plantillaemail import PlantillaEmail
from .models.campanaemail import CampanaEmail
from .models.campaignsend import CampaignSend


# =========================================================
# ADMIN DE PLANTILLA EMAIL
# =========================================================
@admin.register(PlantillaEmail)
class PlantillaEmailAdmin(admin.ModelAdmin):
    """
    Administración del modelo PlantillaEmail.

    Este modelo permite gestionar las plantillas reutilizables
    de email que serán utilizadas en las campañas.

    No es multiempresa, ya que las plantillas pueden ser globales.
    """

    # =========================================================
    # LISTADO
    # =========================================================
    list_display = (
        "nombre",
        "asunto",
    )

    # =========================================================
    # BUSCADOR
    # =========================================================
    search_fields = (
        "nombre",
        "asunto",
    )

    # =========================================================
    # FORMULARIO
    # =========================================================
    fieldsets = (
        ("Información de la plantilla", {
            "fields": (
                "nombre",
                "asunto",
                "cuerpo",
            )
        }),
    )


# =========================================================
# ADMIN DE CAMPAÑA EMAIL
# =========================================================
@admin.register(CampanaEmail)
class CampanaEmailAdmin(admin.ModelAdmin):
    """
    Administración del modelo CampanaEmail.

    Representa las campañas de email del sistema.

    Este modelo es multiempresa, por lo que cada campaña
    pertenece a una empresa concreta.

    Permite:

    - Gestionar campañas
    - Asociar plantillas
    - Ver fechas de creación
    """

    # =========================================================
    # LISTADO
    # =========================================================
    list_display = (
        "nombre",
        "empresa",
        "plantilla",
        "fecha_creacion",
    )

    # =========================================================
    # BUSCADOR
    # =========================================================
    search_fields = (
        "nombre",
    )

    # =========================================================
    # FILTROS
    # =========================================================
    list_filter = (
        "empresa",
        "plantilla",
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
    # FORMULARIO
    # =========================================================
    fieldsets = (
        ("Información de la campaña", {
            "fields": (
                "nombre",
                "descripcion",
                "plantilla",
            )
        }),
        ("Empresa", {
            "fields": (
                "empresa",
            )
        }),
        ("Auditoría", {
            "fields": (
                "fecha_creacion",
            )
        }),
    )


# =========================================================
# ADMIN DE ENVÍOS DE CAMPAÑA
# =========================================================
@admin.register(CampaignSend)
class CampaignSendAdmin(admin.ModelAdmin):
    """
    Administración del modelo CampaignSend.

    Representa el envío de campañas a clientes.

    Este modelo es clave para:

    - Controlar el estado de los envíos
    - Ver historial de campañas
    - Auditar errores o resultados

    Es multiempresa y está relacionado con cliente y campaña.
    """

    # =========================================================
    # LISTADO
    # =========================================================
    list_display = (
        "campana",
        "cliente",
        "estado",
        "fecha_envio",
        "empresa",
    )

    # =========================================================
    # BUSCADOR
    # =========================================================
    search_fields = (
        "campana__nombre",
        "cliente__nombre",
        "cliente__email",
    )

    # =========================================================
    # FILTROS
    # =========================================================
    list_filter = (
        "estado",
        "empresa",
        "fecha_envio",
    )

    # =========================================================
    # ORDENACIÓN
    # =========================================================
    ordering = ("-fecha_envio",)

    # =========================================================
    # CAMPOS SOLO LECTURA
    # =========================================================
    readonly_fields = ("fecha_envio",)

    # =========================================================
    # FORMULARIO
    # =========================================================
    fieldsets = (
        ("Información del envío", {
            "fields": (
                "campana",
                "cliente",
                "estado",
            )
        }),
        ("Empresa", {
            "fields": (
                "empresa",
            )
        }),
        ("Auditoría", {
            "fields": (
                "fecha_envio",
            )
        }),
    )