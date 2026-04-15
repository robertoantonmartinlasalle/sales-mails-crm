import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Se ejecuta automáticamente cuando un usuario hace login.
    """

    logger.info(
        f"[LOGIN] Usuario {user.email} (ID={user.id}) ha iniciado sesión"
    )