from django.db import models

class PlantillaEmail(models.Model):
    nombre = models.CharField(max_length=255)
    asunto = models.CharField(max_length=255)
    cuerpo = models.TextField()

    def __str__(self):
        return self.nombre