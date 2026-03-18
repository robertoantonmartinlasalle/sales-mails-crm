from django.db import models
from core.models.tenant_model import TenantModel


class EstadoCliente(TenantModel):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = "estado_cliente"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre