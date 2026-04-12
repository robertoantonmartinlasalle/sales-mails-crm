from rest_framework.test import APITestCase
from rest_framework import status

from core.tests_helpers import crear_empresa, crear_rol, crear_usuario


class LoginTests(APITestCase):
    """
    Tests del endpoint de autenticación JWT.

    Cubre:
    - Login con credenciales válidas
    - Login con credenciales incorrectas
    - Login con usuario inactivo
    - Contenido de la respuesta (access, refresh, user)
    - Renovación del token (refresh)
    """

    URL_LOGIN = "/api/auth/login/"
    URL_REFRESH = "/api/auth/refresh/"

    def setUp(self):
        self.empresa = crear_empresa()
        self.rol = crear_rol(self.empresa, nombre="Administrador")
        self.usuario = crear_usuario(
            self.empresa, self.rol,
            email="admin@test.com",
            password="testpass123",
        )

    # ----------------------------------------------------------
    # Login correcto
    # ----------------------------------------------------------

    def test_login_valido_devuelve_200(self):
        response = self.client.post(self.URL_LOGIN, {
            "email": "admin@test.com",
            "password": "testpass123",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_valido_devuelve_access_y_refresh(self):
        response = self.client.post(self.URL_LOGIN, {
            "email": "admin@test.com",
            "password": "testpass123",
        }, format="json")

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_respuesta_contiene_datos_usuario(self):
        response = self.client.post(self.URL_LOGIN, {
            "email": "admin@test.com",
            "password": "testpass123",
        }, format="json")

        self.assertIn("user", response.data)
        user_data = response.data["user"]
        self.assertEqual(user_data["email"], "admin@test.com")
        self.assertEqual(user_data["empresa_id"], str(self.empresa.id))
        self.assertEqual(user_data["rol"], "Administrador")

    # ----------------------------------------------------------
    # Login incorrecto
    # ----------------------------------------------------------

    def test_login_password_incorrecta_devuelve_400(self):
        response = self.client.post(self.URL_LOGIN, {
            "email": "admin@test.com",
            "password": "contraseña_incorrecta",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_email_inexistente_devuelve_400(self):
        response = self.client.post(self.URL_LOGIN, {
            "email": "noexiste@test.com",
            "password": "testpass123",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_sin_datos_devuelve_400(self):
        response = self.client.post(self.URL_LOGIN, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------
    # Usuario inactivo
    # ----------------------------------------------------------

    def test_login_usuario_inactivo_devuelve_400(self):
        self.usuario.is_active = False
        self.usuario.save()

        response = self.client.post(self.URL_LOGIN, {
            "email": "admin@test.com",
            "password": "testpass123",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------
    # Refresh token
    # ----------------------------------------------------------

    def test_refresh_token_devuelve_nuevo_access(self):
        login_response = self.client.post(self.URL_LOGIN, {
            "email": "admin@test.com",
            "password": "testpass123",
        }, format="json")

        refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post(self.URL_REFRESH, {
            "refresh": refresh_token,
        }, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_refresh_token_invalido_devuelve_401(self):
        response = self.client.post(self.URL_REFRESH, {
            "refresh": "token_invalido",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
