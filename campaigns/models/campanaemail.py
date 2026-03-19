from django.db import models

from core.models.tenant_model import TenantModel  # Usamos TenantModel para multiempresa
from .plantillaemail import PlantillaEmail


class CampanaEmail(TenantModel):
    """
    Modelo de campañas de email.

    Ahora heredamos de TenantModel para convertir este modelo
    en multiempresa.

    Esto implica que automáticamente tenemos:

        empresa = ForeignKey(Empresa)

    y podremos aplicar filtros como:

        CampanaEmail.objects.for_empresa(...)
    """

    nombre = models.CharField(
        max_length=255
    )

    descripcion = models.TextField(
        null=True,
        blank=True
    )

    """
    Cada campaña utiliza una plantilla de email.

    Esta relación permite reutilizar plantillas
    en múltiples campañas.
    """
    plantilla = models.ForeignKey(
        PlantillaEmail,
        on_delete=models.CASCADE
    )

    """
    Fecha de creación automática.
    """
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nombre