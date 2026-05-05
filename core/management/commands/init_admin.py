from django.core.management.base import BaseCommand
from core.models import Empresa
from users.models import Rol
from users.models.usuario import Usuario


class Command(BaseCommand):
    """
    Comando para inicializar el sistema.

    Se encarga de:

    - Crear o reutilizar la empresa "Sales Mails"
    - Crear o reutilizar el rol Administrador
    - Crear un superusuario por defecto

    Este comando permite levantar el sistema desde cero
    de forma automática sin necesidad de usar el shell.

    Uso:
        python manage.py init_admin
    """

    help = "Inicializa empresa, rol admin y superusuario"

    def handle(self, *args, **kwargs):

        # =========================================================
        # 1. OBTENER O CREAR EMPRESA
        # =========================================================
        """
        Intentamos obtener la empresa "Sales Mails".

        Si no existe, la creamos.
        Si ya existe, la reutilizamos para evitar duplicados.

        Esto es importante en entornos multiempresa, ya que no queremos
        crear varias empresas iguales cada vez que ejecutemos el comando.
        """
        empresa, creada = Empresa.objects.get_or_create(
            nombre="Sales Mails"
        )

        if creada:
            self.stdout.write(self.style.SUCCESS("Empresa creada: Sales Mails"))
        else:
            self.stdout.write(self.style.WARNING("Usando empresa existente: Sales Mails"))

        # =========================================================
        # 2. OBTENER O CREAR ROL ADMINISTRADOR
        # =========================================================
        """
        Creamos el rol administrador asociado a la empresa.

        IMPORTANTE:
        - Usamos Rol.ADMIN (constante) para evitar errores de escritura
        - El rol está ligado a la empresa (multiempresa)
        - Cada empresa tiene sus propios roles
        """
        rol_admin, creado = Rol.objects.get_or_create(
            nombre=Rol.ADMIN,
            empresa=empresa
        )

        if creado:
            self.stdout.write(self.style.SUCCESS("Rol administrador creado"))
        else:
            self.stdout.write(self.style.WARNING("Usando rol administrador existente"))

        # =========================================================
        # 3. CREAR SUPERUSUARIO
        # =========================================================
        """
        Creamos un superusuario si no existe.

        Datos por defecto:
        - Email: admin@crm.com
        - Password: administrator_55

        IMPORTANTE:
        - Asociamos empresa y rol al usuario
        - Esto es obligatorio en nuestro sistema multiempresa
        - Sin empresa y rol el usuario no tendría contexto dentro del CRM
        """
        if not Usuario.objects.filter(email="admin@crm.com").exists():

            Usuario.objects.create_superuser(
                email="admin@crm.com",
                password="administrator_55",
                empresa=empresa,
                rol=rol_admin
            )

            self.stdout.write(self.style.SUCCESS("Superusuario creado"))

        else:
            self.stdout.write(self.style.WARNING("El superusuario ya existe"))

        # =========================================================
        # FIN DEL PROCESO
        # =========================================================
        """
        Mensaje final indicando que el proceso ha terminado correctamente.
        """
        self.stdout.write(self.style.SUCCESS("Inicialización completada "))