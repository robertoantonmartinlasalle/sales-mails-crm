from django.db import models
from .campanaemail import CampanaEmail
from clients.models import Cliente

class CampaignSend(models.Model):
    campana = models.ForeignKey(CampanaEmail, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.CharField(max_length=50, default="pendiente")
    fecha_envio = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.cliente.email} - {self.estado}"