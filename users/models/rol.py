import uuid
from django.db import models

from core.models.tenant_model import TenantModel  # Usamos nuestro modelo base multiempresa


class Rol(TenantModel):
    """
    Modelo de roles del sistema.

    Cada rol pertenece a una empresa (multiempresa) y define
    el nivel de permisos de un usuario dentro del CRM.

    Ejemplos de roles:
    - Administrador
    - Comercial
    - Lectura

    IMPORTANTE:
    Usamos constantes para evitar depender de strings en el código,
    lo que mejora la mantenibilidad y evita errores de escritura.
    """

    # =========================================================
    # IDENTIFICADOR ÚNICO (UUID)
    # =========================================================
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # =========================================================
    # CONSTANTES DE ROLES (USO INTERNO EN CÓDIGO)
    # =========================================================
    ADMIN = "ADMIN"
    COMERCIAL = "COMERCIAL"
    LECTURA = "LECTURA"

    TIPOS_ROL = [
        (ADMIN, "Administrador"),
        (COMERCIAL, "Comercial"),
        (LECTURA, "Lectura"),
    ]

    # =========================================================
    # NOMBRE DEL ROL
    # =========================================================
    nombre = models.CharField(
        max_length=100,
        choices=TIPOS_ROL
    )

    # =========================================================
    # DESCRIPCIÓN OPCIONAL
    # =========================================================
    descripcion = models.TextField(
        blank=True
    )

    # =========================================================
    # CONFIGURACIÓN DEL MODELO
    # =========================================================
    class Meta:
        # Evitamos que haya dos roles con el mismo nombre en una empresa
        unique_together = ["empresa", "nombre"]

        # Ordenamos los roles por nombre al consultarlos
        ordering = ["nombre"]

    # =========================================================
    # REPRESENTACIÓN EN TEXTO (ADMIN / DEBUG)
    # =========================================================
    def __str__(self):
        """
        Mostramos el nombre legible del rol en el admin.
        """
        return self.get_nombre_display()