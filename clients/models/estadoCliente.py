from django.db import models
from core.models.tenant_model import TenantModel


class EstadoCliente(TenantModel):
    """
    Modelo de estados de cliente.

    Cada estado pertenece a una empresa (multi-tenant),
    por lo que no pueden existir duplicados de nombre
    dentro de la misma empresa.
    """

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = "estado_cliente"
        ordering = ["orden", "nombre"]

        # Restricción a nivel de base de datos
        unique_together = ["empresa", "nombre"]

    def __str__(self):
        return self.nombre