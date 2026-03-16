import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

from core.models import Empresa
from users.models import Rol


class UsuarioManager(BaseUserManager):

    """
    Manager personalizado para el modelo Usuario.

    Cuando utilizamos email como campo de autenticación en lugar de username,
    Django ya no puede utilizar el UserManager estándar porque este espera
    recibir 'username' como argumento obligatorio.

    Por este motivo debemos redefinir cómo se crean los usuarios y superusuarios.
    """

    def create_user(self, email, password=None, **extra_fields):

        """
        Método utilizado para crear usuarios normales.

        Recibe el email como identificador principal del usuario.
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
        Método utilizado por el comando:

            python manage.py createsuperuser

        Un superusuario debe tener siempre permisos de administración.
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

    Decidimos extender AbstractUser en lugar de crear un modelo desde cero
    porque Django ya proporciona un sistema de autenticación robusto que incluye:

    - gestión segura de contraseñas (hashing)
    - sistema de permisos
    - integración con el admin
    - gestión de sesiones
    - autenticación y login

    Extender AbstractUser nos permite añadir nuestros campos propios
    sin perder estas funcionalidades.
    """

    """
    Utilizamos un manager personalizado para soportar autenticación mediante email.
    """
    objects = UsuarioManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    """
    Cada usuario pertenece obligatoriamente a una empresa.

    Esto es fundamental en una arquitectura multiempresa (multi-tenant),
    ya que permite aislar los datos entre organizaciones.

    Gracias a esta relación podremos aplicar filtros como:

        Model.objects.filter(empresa=request.user.empresa)

    evitando que usuarios de una empresa accedan a datos de otra.
    """
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="usuarios"
    )

    """
    Cada usuario tiene asignado un único rol.

    El rol define el nivel de permisos dentro de la empresa
    (administrador, comercial, marketing, etc.).

    Usamos PROTECT para evitar eliminar un rol que esté
    siendo utilizado por usuarios existentes.
    """
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name="usuarios"
    )

    """
    Django por defecto usa 'username' como campo de autenticación.

    En nuestro sistema decidimos usar el email como login porque:

    - es más natural para los usuarios
    - evita recordar nombres de usuario
    - es el estándar en la mayoría de aplicaciones SaaS modernas

    Por tanto redefinimos username para que sea opcional.
    """
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    """
    El email será el identificador único para autenticación.

    Usamos unique=True para evitar duplicados.
    """
    email = models.EmailField(
        unique=True
    )

    """
    Indicamos a Django que el campo utilizado para login es el email.
    """
    USERNAME_FIELD = "email"

    """
    Campos obligatorios cuando se crea un usuario mediante
    el comando createsuperuser.

    Como utilizamos email como identificador principal,
    no necesitamos pedir username.
    """
    REQUIRED_FIELDS = []

    """
    Fecha de creación del usuario.
    """
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email