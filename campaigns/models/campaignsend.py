from django.db import models

from core.models.tenant_model import TenantModel  # Modelo base multiempresa
from .campanaemail import CampanaEmail
from clients.models import Cliente


class CampaignSend(TenantModel):
    """
    Modelo que representa el envío de una campaña a un cliente.

    Hereda de TenantModel, por lo que automáticamente dispone de:

        empresa = ForeignKey(Empresa)

    Esto permite:

    - Aislamiento de datos entre empresas (multi-tenant)
    - Filtrado automático mediante:
        CampaignSend.objects.for_empresa(empresa)
    """

    # =========================================================
    # RELACIONES
    # =========================================================

    """
    Relación con la campaña que se va a enviar.
    """
    campana = models.ForeignKey(
        CampanaEmail,
        on_delete=models.CASCADE
    )

    """
    Cliente al que se envía la campaña.

    Puede ser null porque:
    - Permitimos envíos masivos
    - En el futuro podríamos soportar campañas sin cliente específico
    """
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # =========================================================
    # ESTADO DEL ENVÍO (CONTROLADO CON CHOICES)
    # =========================================================

    """
    Definimos constantes para evitar errores por strings "hardcodeados"
    y mejorar la mantenibilidad del código.
    """
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_ENVIADO = "enviado"
    ESTADO_ERROR = "error"

    """
    Opciones válidas del estado.

    Esto evita que se puedan guardar valores incorrectos en la base de datos.
    """
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_ENVIADO, "Enviado"),
        (ESTADO_ERROR, "Error"),
    ]

    """
    Estado actual del envío.

    Valores posibles:
    - pendiente (por defecto)
    - enviado
    - error
    """
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default=ESTADO_PENDIENTE
    )

    # =========================================================
    # INFORMACIÓN DEL ENVÍO
    # =========================================================

    """
    Fecha en la que se realiza el envío.

    Se rellena automáticamente cuando el email se envía correctamente.
    """
    fecha_envio = models.DateTimeField(
        null=True,
        blank=True
    )

    """
    Mensaje de error en caso de fallo en el envío.

    Se utiliza para almacenar información útil cuando:
    - falla el envío del email
    - ocurre una excepción en el servicio de correo

    Esto permite diagnosticar problemas sin necesidad de revisar logs.
    """
    error_mensaje = models.TextField(
        null=True,
        blank=True
    )

    # =========================================================
    # REPRESENTACIÓN DEL MODELO
    # =========================================================

    def __str__(self):
        """
        Representación en texto del objeto.

        
        Evitamos errores cuando cliente es null.
        """
        return f"{self.cliente.email if self.cliente else 'Sin cliente'} - {self.estado}"