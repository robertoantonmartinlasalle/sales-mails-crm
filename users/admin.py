from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Usuario, Rol


# =========================================================
# FORMULARIO DE CREACIÓN PERSONALIZADO
# =========================================================
class UsuarioCreationForm(UserCreationForm):
    """
    Formulario para CREAR usuarios en el admin.

    IMPORTANTE:
    Usamos UserCreationForm porque incluye:
    - password1
    - password2

    Aquí NO complicamos lógica:
    La seguridad real está en el modelo.
    """

    class Meta:
        model = Usuario
        fields = ("email", "empresa", "rol")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # UX básica
        self.fields["rol"].required = True
        self.fields["rol"].empty_label = None


# =========================================================
# FORMULARIO DE EDICIÓN PERSONALIZADO
# =========================================================
class UsuarioChangeForm(UserChangeForm):
    """
    Formulario para EDITAR usuarios en el admin.

    Aquí sí filtramos correctamente por empresa.
    """

    class Meta:
        model = Usuario
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 CLAVE: filtrado correcto
        if self.instance and self.instance.empresa:
            self.fields["rol"].queryset = Rol.objects.filter(
                empresa=self.instance.empresa
            )

        self.fields["rol"].required = True
        self.fields["rol"].empty_label = None


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
    # FORMULARIOS PERSONALIZADOS
    # =========================================================
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm

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
    # FORMULARIO DE EDICIÓN
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
    # FORMULARIO DE CREACIÓN
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
    # SEGURIDAD EXTRA (opcional pero recomendable)
    # =========================================================
    def get_queryset(self, request):
        """
        Limitamos los usuarios visibles en el admin.
        """
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(empresa=request.user.empresa)