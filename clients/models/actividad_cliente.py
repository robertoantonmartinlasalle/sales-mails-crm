from django.db import models
from django.conf import settings

from core.models.tenant_model import TenantModel


class ActividadCliente(TenantModel):
    TIPO_CHOICES = [
        ("cliente_creado", "Cliente creado"),
        ("cliente_actualizado", "Cliente actualizado"),
        ("estado_cambiado", "Estado cambiado"),
        ("cliente_eliminado", "Cliente eliminado"),
        ("cliente_restaurado", "Cliente restaurado"),
        ("email_enviado", "Email enviado"),
    ]

    cliente = models.ForeignKey(
        "clients.Cliente",
        on_delete=models.CASCADE,
        related_name="historial_actividades",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades_cliente",
    )
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "actividad_cliente"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.tipo} - {self.cliente} ({self.fecha_creacion:%Y-%m-%d %H:%M})"
