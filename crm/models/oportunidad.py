from django.db import models
from core.models.tenant_model import TenantModel
from clients.models import Cliente
from campaigns.models import CampaignSend
from users.models import Usuario


class Oportunidad(TenantModel):
    ESTADO_CHOICES = [
        ("abierta", "Abierta"),
        ("en_progreso", "En progreso"),
        ("ganada", "Ganada"),
        ("perdida", "Perdida"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="oportunidades"
    )

    campaign_send = models.ForeignKey(
        CampaignSend,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="oportunidades"
    )

    usuario_responsable = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="oportunidades_responsables"
    )

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="abierta"
    )
    probabilidad = models.IntegerField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre_prevista = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "oportunidad"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.titulo