# Aquí irá la lógica para que podamos filtrar automáticamente por empresa

from django.db import models


class TenantManager(models.Manager):

    def for_empresa(self, empresa):
        """
        Devuelve solo los registros que pertenecen a una empresa.
        """
        return self.get_queryset().filter(empresa=empresa)