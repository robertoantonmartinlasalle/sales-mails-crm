"""
Helpers compartidos para los tests del proyecto.

Centraliza la creación de objetos de prueba reutilizables
para evitar duplicar lógica en cada suite de tests.
"""

from core.models.empresa import Empresa
from users.models.usuario import Usuario
from users.models.rol import Rol


def crear_empresa(nombre="Empresa Test", cif=None):
    return Empresa.objects.create(
        nombre=nombre,
        cif=cif,
        telefono="600000000",
        direccion="Calle Test 1",
    )


def crear_rol(empresa, nombre="Administrador"):
    return Rol.objects.create(
        empresa=empresa,
        nombre=nombre,
        descripcion=f"Rol {nombre}",
    )


def crear_usuario(empresa, rol, email="admin@test.com", password="testpass123"):
    return Usuario.objects.create_user(
        email=email,
        password=password,
        empresa=empresa,
        rol=rol,
    )


def obtener_token(client, email, password):
    """
    Realiza el login y devuelve el access token JWT.
    """
    response = client.post(
        "/api/auth/login/",
        {"email": email, "password": password},
        format="json",
    )
    return response.data.get("access")


def autenticar(client, token):
    """
    Configura el cliente con el token Bearer.
    """
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
