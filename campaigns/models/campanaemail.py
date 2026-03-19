from django.db import models
from .plantillaemail import PlantillaEmail

class CampanaEmail(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    plantilla = models.ForeignKey(PlantillaEmail, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre