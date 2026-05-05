import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError

from core.models import Empresa
from core.models.tenant_manager import TenantManager 
from users.models import Rol


class UsuarioManager(BaseUserManager, TenantManager):
    """
    Manager personalizado para Usuario.

    Aquí combinamos dos cosas:

    1. BaseUserManager:
       → necesario para create_user y create_superuser

    2. TenantManager:
       → nos da el método for_empresa()

    De esta forma tenemos:
    - creación de usuarios
    - autenticación por email
    - filtrado multiempresa reutilizable
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Método para crear usuarios normales.
        """

        if not email:
            raise ValueError("El email es obligatorio para crear un usuario")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Método para crear superusuarios (admin Django).
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado del sistema.
    """

    # =========================================================
    # MANAGER PERSONALIZADO (AHORA CON MULTIEMPRESA)
    # =========================================================
    objects = UsuarioManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="usuarios"
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name="usuarios"
    )

    username = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    email = models.EmailField(
        unique=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email

    # =========================================================
    # VALIDACIÓN MULTIEMPRESA (CRÍTICA)
    # =========================================================
    def clean(self):
        """
        Validación clave del sistema multiempresa.

        Garantiza que el rol asignado al usuario
        pertenece a la misma empresa.

        Esto evita:
        - Cruces de datos entre empresas
        - Problemas de permisos
        - Inconsistencias en el sistema
        """

        if self.rol and self.empresa:
            if self.rol.empresa != self.empresa:
                raise ValidationError(
                    "El rol asignado no pertenece a la misma empresa que el usuario"
                )

    # =========================================================
    # SOBRESCRITURA DE SAVE 
    # =========================================================
    def save(self, *args, **kwargs):
        """
        Forzamos validación completa antes de guardar.

        IMPORTANTE:
        Django NO ejecuta clean() automáticamente,
        por lo que debemos llamar a full_clean().

        Esto asegura que:
        - Admin esté protegido
        - API esté protegido
        - ORM directo esté protegido
        """

        self.full_clean()  
        super().save(*args, **kwargs)