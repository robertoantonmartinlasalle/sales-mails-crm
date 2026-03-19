from django.db import models
from core.models.tenant_model import TenantModel
from clients.models import Cliente
from users.models import Usuario
from .oportunidad import Oportunidad


class Actividad(TenantModel):
    TIPO_CHOICES = [
        ("llamada", "Llamada"),
        ("email", "Email"),
        ("reunion", "Reunión"),
        ("tarea", "Tarea"),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name="actividades"
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades"
    )

    oportunidad = models.ForeignKey(
        Oportunidad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actividades"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default="tarea"
    )
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField()
    completada = models.BooleanField(default=False)

    class Meta:
        db_table = "actividad"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.tipo} - {self.fecha}"