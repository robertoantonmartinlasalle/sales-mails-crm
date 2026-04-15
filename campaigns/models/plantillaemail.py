from django.db import models
from core.models.tenant_model import TenantModel


class PlantillaEmail(TenantModel):
    """
    Modelo de plantillas de email.

    Cada plantilla pertenece a una empresa (multi-tenant),
    evitando que otras empresas puedan acceder a ella.
    """

    nombre = models.CharField(max_length=255)
    asunto = models.CharField(max_length=255)
    cuerpo = models.TextField()

    def __str__(self):
        return self.nombre