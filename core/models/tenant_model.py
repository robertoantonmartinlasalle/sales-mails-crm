''' Aquí definiremos un modelo base reutilizable.

Si no usamos un modelo base tendríamos que repetir esto en cada modelo:
empresa = models.ForeignKey(
    Empresa,
    on_delete=models.CASCADE
)

'''

from django.db import models

from .tenant_manager import TenantManager


class TenantModel(models.Model):
    """
    Modelo base para todas las entidades multiempresa.
    """

    empresa = models.ForeignKey(
        "core.Empresa",
        on_delete=models.CASCADE,
        related_name="%(class)s_items",
        db_index=True # Para optimización
    )

    objects = TenantManager()

    class Meta:
        abstract = True # TenantModel NO crea tabla en la base de datos, solo sirve como base para otros modelos.