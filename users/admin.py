from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Usuario, Rol


# =========================================================
# ADMIN DE ROL
# =========================================================
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """
    Administración del modelo Rol.

    Permite gestionar los roles asociados a cada empresa.
    """

    list_display = ("nombre", "empresa")
    search_fields = ("nombre",)
    list_filter = ("empresa",)
    ordering = ("nombre",)


# =========================================================
# ADMIN DE USUARIO
# =========================================================
@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Administración del modelo Usuario personalizado.

    Este admin extiende UserAdmin para:

    - Soportar autenticación por email
    - Permitir gestión correcta de contraseñas
    - Incluir empresa y rol
    - Adaptarse a la arquitectura multiempresa

    Es una pieza clave del sistema de seguridad del CRM.
    """

    # =========================================================
    # IDENTIFICACIÓN DEL USUARIO
    # =========================================================
    ordering = ("email",)
    list_display = (
        "email",
        "empresa",
        "rol",
        "is_staff",
        "is_active",
    )

    # =========================================================
    # BUSCADOR
    # =========================================================
    search_fields = ("email",)

    # =========================================================
    # FILTROS
    # =========================================================
    list_filter = ("empresa", "rol", "is_staff", "is_active")

    # =========================================================
    # CAMPOS DE SOLO LECTURA
    # =========================================================
    readonly_fields = ("id", "fecha_creacion")

    # =========================================================
    # FORMULARIO DE EDICIÓN (usuario existente)
    # =========================================================
    fieldsets = (
        ("Información de acceso", {
            "fields": ("email", "password")
        }),
        ("Información personal", {
            "fields": ("empresa", "rol")
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser")
        }),
        ("Fechas", {
            "fields": ("last_login", "fecha_creacion")
        }),
    )

    # =========================================================
    # FORMULARIO DE CREACIÓN (MUY IMPORTANTE)
    # =========================================================
    add_fieldsets = (
        ("Crear nuevo usuario", {
            "classes": ("wide",),
            "fields": (
                "email",
                "password1",
                "password2",
                "empresa",
                "rol",
                "is_active",
                "is_staff",
            ),
        }),
    )

    # =========================================================
    # CONFIGURACIÓN PARA USERNAME
    # =========================================================
    USERNAME_FIELD = "email"
    model = Usuario

    # =========================================================
    # FILTRADO DE ROLES POR EMPRESA (CLAVE DEL EJERCICIO)
    # =========================================================
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Personalizamos el comportamiento del campo ForeignKey 'rol'.

        Django por defecto mostraría TODOS los roles de la base de datos,
        lo que en un sistema multiempresa provoca:

        - Duplicados visuales (Comercial varias veces)
        - Posibilidad de asignar roles de otra empresa 

        Solución:
        Filtramos el queryset para que solo aparezcan los roles
        pertenecientes a la empresa del usuario autenticado.
        """

        if db_field.name == "rol":
            if request.user.is_superuser:
                # El superusuario puede ver todos los roles del sistema
                kwargs["queryset"] = Rol.objects.all()
            else:
                # SOLO mostramos los roles de su empresa
                kwargs["queryset"] = Rol.objects.filter(
                    empresa=request.user.empresa
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)