# Aquí definiremos el modelo empresa

import uuid

from django.db import models


class Empresa(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    nombre = models.CharField(max_length=150)

    cif = models.CharField(
        max_length=20,
        unique=True,
        null=True, # hemos decidido permitir null porque algunas empresas no lo tienen registrado.
        blank=True
    )

    email_contacto = models.EmailField(
        null=True,
        blank=True
    )

    telefono = models.CharField(
        max_length=30,
        blank=True
    )

    direccion = models.TextField(
        blank=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    activa = models.BooleanField(
        default=True # lo hemos considerado interesante para poder desactivar una empresa sin borrar datos.
    )

    def __str__(self):
        return self.nombre