import uuid

from django.db import models

from core.models.tenant_model import TenantModel # Usamos nuestro modelo tenant


class Rol(TenantModel):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True
    )

    class Meta:
        unique_together = ["empresa", "nombre"]
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre