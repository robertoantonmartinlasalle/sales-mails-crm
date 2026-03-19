from django.db import models
from core.models.tenant_model import TenantModel
from .estadoCliente import EstadoCliente


class Cliente(TenantModel):
    TIPO_CHOICES = [
        ("empresa", "Empresa"),
        ("persona", "Persona"),
    ]

    estado_cliente = models.ForeignKey(
        EstadoCliente,
        on_delete=models.PROTECT,
        related_name="clientes"
    )

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    nif = models.CharField(max_length=30, blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "cliente"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.nombre