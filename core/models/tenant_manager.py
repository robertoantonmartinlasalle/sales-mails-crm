# Aquí irá la lógica para que podamos filtrar automáticamente por empresa

from django.db import models
import logging

# Creamos un logger para este archivo
# __name__ hace que Django identifique de dónde viene el log (muy útil para depurar)
logger = logging.getLogger(__name__)


class TenantManager(models.Manager):
    """
    Nos permite centralizar el filtrado por empresa y añadir
    trazabilidad mediante logging.
    """

    def for_empresa(self, empresa):
        """
        Devuelve solo los registros que pertenecen a una empresa.

        Además, registramos en logs cuándo se realiza este filtrado
        para poder auditar y depurar el comportamiento del sistema.
        """

        # Logging informativo (nivel INFO)
        # Nos permite saber qué empresa está accediendo a los datos
        logger.info(f"[TenantManager] Filtrando registros para empresa ID={empresa.id}")

        # Devolvemos el queryset filtrado
        return self.get_queryset().filter(empresa=empresa)