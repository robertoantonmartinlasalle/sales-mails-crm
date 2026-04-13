from django.db import models

from core.models.tenant_model import TenantModel  # Importamos el modelo base multiempresa
from .campanaemail import CampanaEmail
from clients.models import Cliente


class CampaignSend(TenantModel):
    """
    Modelo que representa el envío de una campaña a un cliente.

    Hereda de TenantModel para ser multiempresa.

    Esto implica que automáticamente tenemos:

        empresa = ForeignKey(Empresa)

    y podremos aplicar filtros como:

        CampaignSend.objects.for_empresa(...)
    """

    """
    Relación con la campaña que se va a enviar.
    """
    campana = models.ForeignKey(
        CampanaEmail,
        on_delete=models.CASCADE
    )

    """
    Cliente al que se envía la campaña.

    Puede ser null porque en el futuro podríamos permitir
    envíos masivos o campañas sin cliente específico.
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    """
    Estado del envío.

    Ejemplos:
    - pendiente
    - enviado
    - error
    """
    estado = models.CharField(
        max_length=50,
        default="pendiente"
    )

    """
    Fecha en la que se realiza el envío.
    """
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True
    )

    """
    Mensaje de error en caso de fallo en el envío.

    Se rellena automáticamente cuando el envío falla,
    con el mensaje de la excepción capturada.
    Permite diagnosticar problemas sin necesidad de revisar logs.
    """
    error_mensaje = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.cliente.email} - {self.estado}"