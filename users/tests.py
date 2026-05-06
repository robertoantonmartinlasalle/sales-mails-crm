from rest_framework.test import APITestCase
from rest_framework import status

from core.tests_helpers import (
    crear_empresa,
    crear_rol,
    crear_usuario,
    obtener_token,
    autenticar,
)


class BaseUsuariosTest(APITestCase):
    """
    Base compartida: crea empresa, roles y usuarios de prueba.
    """

    def setUp(self):
        # Empresa y roles propios
        self.empresa = crear_empresa(nombre="Empresa A")
        self.rol_admin = crear_rol(self.empresa, nombre="ADMIN")
        self.rol_comercial = crear_rol(self.empresa, nombre="COMERCIAL")

        self.admin = crear_usuario(
            self.empresa, self.rol_admin,
            email="admin@empresa-a.com",
            password="testpass123",
        )
        self.comercial = crear_usuario(
            self.empresa, self.rol_comercial,
            email="comercial@empresa-a.com",
            password="testpass123",
        )

        # Segunda empresa para pruebas de aislamiento
        self.empresa_b = crear_empresa(nombre="Empresa B", cif="B12345678")
        self.rol_admin_b = crear_rol(self.empresa_b, nombre="ADMIN")
        self.admin_b = crear_usuario(
            self.empresa_b, self.rol_admin_b,
            email="admin@empresa-b.com",
            password="testpass123",
        )

    def autenticar_admin(self):
        token = obtener_token(self.client, "admin@empresa-a.com", "testpass123")
        autenticar(self.client, token)

    def autenticar_comercial(self):
        token = obtener_token(self.client, "comercial@empresa-a.com", "testpass123")
        autenticar(self.client, token)

    def autenticar_admin_b(self):
        token = obtener_token(self.client, "admin@empresa-b.com", "testpass123")
        autenticar(self.client, token)


class UsuarioListTests(BaseUsuariosTest):
    """
    Tests de listado de usuarios.
    """

    URL = "/api/users/"

    def test_admin_puede_listar_usuarios(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comercial_puede_listar_usuarios(self):
        self.autenticar_comercial()
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sin_autenticar_devuelve_401(self):
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_aislamiento_multiempresa_no_ve_usuarios_de_otra_empresa(self):
        """
        Un admin de empresa A solo debe ver sus propios usuarios,
        nunca los de empresa B.
        """
        self.autenticar_admin()
        response = self.client.get(self.URL)

        emails = [u["email"] for u in response.data]

        self.assertIn("admin@empresa-a.com", emails)
        self.assertIn("comercial@empresa-a.com", emails)
        self.assertNotIn("admin@empresa-b.com", emails)

    def test_admin_b_no_ve_usuarios_de_empresa_a(self):
        self.autenticar_admin_b()
        response = self.client.get(self.URL)

        emails = [u["email"] for u in response.data]

        self.assertNotIn("admin@empresa-a.com", emails)
        self.assertNotIn("comercial@empresa-a.com", emails)


class UsuarioCreateTests(BaseUsuariosTest):
    """
    Tests de creación de usuarios.
    """

    URL = "/api/users/"

    def _payload(self, email="nuevo@empresa-a.com"):
        return {
            "email": email,
            "password": "nuevapass123",
            "rol": str(self.rol_admin.id),
        }

    def test_admin_puede_crear_usuario(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "nuevo@empresa-a.com")

    def test_usuario_creado_pertenece_a_empresa_del_admin(self):
        self.autenticar_admin()
        self.client.post(self.URL, self._payload(), format="json")

        from users.models.usuario import Usuario
        nuevo = Usuario.objects.get(email="nuevo@empresa-a.com")
        self.assertEqual(nuevo.empresa, self.empresa)

    def test_comercial_no_puede_crear_usuario(self):
        self.autenticar_comercial()
        response = self.client.post(self.URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_sin_autenticar_no_puede_crear_usuario(self):
        response = self.client.post(self.URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_se_puede_crear_usuario_con_email_duplicado(self):
        self.autenticar_admin()
        # El email ya existe (admin@empresa-a.com)
        response = self.client.post(self.URL, self._payload(
            email="admin@empresa-a.com"
        ), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UsuarioUpdateTests(BaseUsuariosTest):
    """
    Tests de actualización de usuarios.
    """

    def _url(self):
        return f"/api/users/{self.comercial.id}/"

    def test_admin_puede_actualizar_usuario(self):
        self.autenticar_admin()
        response = self.client.patch(self._url(), {
            "username": "nuevo_username",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comercial_no_puede_actualizar_usuario(self):
        self.autenticar_comercial()
        response = self.client.patch(self._url(), {
            "username": "intento_comercial",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UsuarioDeleteTests(BaseUsuariosTest):
    """
    Tests de eliminación de usuarios.
    """

    def _url(self):
        return f"/api/users/{self.comercial.id}/"

    def test_admin_puede_eliminar_usuario(self):
        self.autenticar_admin()
        response = self.client.delete(self._url())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comercial_no_puede_eliminar_usuario(self):
        self.autenticar_comercial()
        response = self.client.delete(self._url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
