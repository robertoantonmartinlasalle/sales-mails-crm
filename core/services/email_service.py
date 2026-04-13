from django.core.mail import send_mail
from django.conf import settings


def send_email(
    to,
    subject: str,
    message: str,
    from_email: str | None = None,
) -> tuple[bool, str | None]:

    """
    Servicio centralizado para el envío de emails dentro del sistema.

    Hemos decidido encapsular el uso de send_mail de Django en una función
    propia para desacoplar la lógica de envío del resto del proyecto.

    Esto nos permite:

    - Evitar duplicar código en diferentes partes del sistema
    - Centralizar la lógica de envío de emails
    - Facilitar futuras mejoras (logs, reintentos, plantillas HTML, etc.)
    - Poder cambiar el proveedor de email sin afectar al resto del código

    Además, esta función ya está preparada para soportar envíos a múltiples
    destinatarios, lo cual será clave en el módulo de campañas.

    Parámetros:
        to (str | list[str]):
            Puede ser un único email o una lista de emails.
            Esto nos da flexibilidad para usar la función en distintos contextos.

        subject (str):
            Asunto del correo.

        message (str):
            Contenido del mensaje en texto plano.

        from_email (str | None):
            Email del remitente.
            Si no se proporciona, se utilizará el configurado en settings
            (EMAIL_HOST_USER, cargado desde el archivo .env).

    Retorna:
        tuple[bool, str | None]:
            - (True, None) → el email se ha enviado correctamente
            - (False, "mensaje de error") → ha ocurrido algún error en el envío
    """

    """
    Determinamos el remitente del correo.

    Si no se pasa explícitamente un 'from_email', utilizamos el configurado
    en settings, lo que nos permite no hardcodear valores y mantener la
    configuración desacoplada del código.
    """
    sender = from_email or settings.EMAIL_HOST_USER

    """
    Normalización del parámetro 'to'.

    Permitimos dos formas de uso:

        1. Un único email (str)
            Ej: "usuario@gmail.com"

        2. Múltiples emails (list[str])
            Ej: ["user1@gmail.com", "user2@gmail.com"]

    Internamente convertimos siempre a lista para asegurarnos de que
    send_mail recibe el formato correcto y evitar errores como los que
    pueden surgir cuando una lista es interpretada como string.
    """
    if isinstance(to, str):
        to = [to]
    else:
        to = list(to)

    try:
        """
        Ejecutamos el envío utilizando la utilidad nativa de Django.

        - subject → asunto del email
        - message → contenido del email
        - from_email → remitente
        - recipient_list → lista de destinatarios
        - fail_silently=False → en desarrollo queremos ver los errores
        """
        send_mail(
            subject=subject,
            message=message,
            from_email=sender,
            recipient_list=to,
            fail_silently=False,
        )

        """
        Si no se produce ninguna excepción, consideramos que el envío
        se ha realizado correctamente.

        Devolvemos (True, None) → éxito, sin mensaje de error.
        """
        return True, None

    except Exception as e:
        """
        Capturamos cualquier error durante el envío.

        En una fase más avanzada del proyecto, este bloque debería evolucionar hacia:

        - Logging estructurado (por ejemplo con logging de Python)
        - Sistemas de reintento (colas como Celery)
        - Persistencia de errores en base de datos
        - Monitorización del estado de los envíos

        Devolvemos (False, mensaje) → fallo, con la causa del error.
        """
        print(f"Error enviando email: {e}")
        return False, str(e)