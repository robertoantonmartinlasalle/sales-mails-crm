from rest_framework.test import APITestCase
from rest_framework import status

from core.tests_helpers import (
    crear_empresa,
    crear_rol,
    crear_usuario,
    obtener_token,
    autenticar,
)
from clients.models.estadoCliente import EstadoCliente
from clients.models.cliente import Cliente


class BaseClientesTest(APITestCase):
    """
    Base compartida: crea dos empresas con usuarios y estados de cliente.
    """

    def setUp(self):
        # Empresa A
        self.empresa = crear_empresa(nombre="Empresa A")
        self.rol_admin = crear_rol(self.empresa, nombre="ADMIN")
        self.rol_comercial = crear_rol(self.empresa, nombre="COMERCIAL")

        self.admin = crear_usuario(
            self.empresa, self.rol_admin,
            email="admin@empresa-a.com", password="testpass123",
        )
        self.comercial = crear_usuario(
            self.empresa, self.rol_comercial,
            email="comercial@empresa-a.com", password="testpass123",
        )

        # Estado de cliente propio
        self.estado = EstadoCliente.objects.create(
            empresa=self.empresa,
            nombre="Activo",
            orden=1,
        )

        # Empresa B (para aislamiento)
        self.empresa_b = crear_empresa(nombre="Empresa B", cif="B12345678")
        self.rol_admin_b = crear_rol(self.empresa_b, nombre="ADMIN")
        self.admin_b = crear_usuario(
            self.empresa_b, self.rol_admin_b,
            email="admin@empresa-b.com", password="testpass123",
        )
        self.estado_b = EstadoCliente.objects.create(
            empresa=self.empresa_b,
            nombre="Activo",
            orden=1,
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


# ==============================================================
# ESTADO CLIENTE
# ==============================================================

class EstadoClienteListTests(BaseClientesTest):

    URL = "/api/client-status/"

    def test_admin_puede_listar_estados(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sin_autenticar_devuelve_401(self):
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_aislamiento_solo_ve_estados_propios(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        nombres = [e["nombre"] for e in response.data]
        self.assertIn("Activo", nombres)
        # Verificamos que solo devuelve los de su empresa
        ids = [str(e["id"]) for e in response.data]
        self.assertNotIn(str(self.estado_b.id), ids)


class EstadoClienteCreateTests(BaseClientesTest):

    URL = "/api/client-status/"

    def test_admin_puede_crear_estado(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, {
            "nombre": "Prospecto",
            "descripcion": "Nuevo prospecto",
            "orden": 2,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombre"], "Prospecto")

    def test_estado_creado_pertenece_a_empresa_del_admin(self):
        self.autenticar_admin()
        self.client.post(self.URL, {
            "nombre": "Prospecto",
            "orden": 2,
        }, format="json")

        estado = EstadoCliente.objects.get(nombre="Prospecto")
        self.assertEqual(estado.empresa, self.empresa)

    def test_no_se_puede_crear_nombre_duplicado_en_misma_empresa(self):
        self.autenticar_admin()
        # "Activo" ya existe en empresa A
        response = self.client.post(self.URL, {
            "nombre": "Activo",
            "orden": 99,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comercial_puede_crear_estado(self):
        self.autenticar_comercial()
        response = self.client.post(self.URL, {
            "nombre": "Inactivo",
            "orden": 3,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EstadoClienteDeleteTests(BaseClientesTest):

    def _url(self):
        return f"/api/client-status/{self.estado.id}/"

    def test_admin_puede_eliminar_estado(self):
        self.autenticar_admin()
        response = self.client.delete(self._url())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comercial_no_puede_eliminar_estado(self):
        self.autenticar_comercial()
        response = self.client.delete(self._url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ==============================================================
# CLIENTE
# ==============================================================

class ClienteListTests(BaseClientesTest):

    URL = "/api/clients/"

    def _crear_cliente(self, empresa, estado, nombre="Cliente Test", email="cliente@test.com"):
        return Cliente.objects.create(
            empresa=empresa,
            estado_cliente=estado,
            nombre=nombre,
            tipo="empresa",
            email=email,
        )

    def setUp(self):
        super().setUp()
        self.cliente_a = self._crear_cliente(self.empresa, self.estado)
        self.cliente_b = self._crear_cliente(
            self.empresa_b, self.estado_b,
            nombre="Cliente Empresa B",
            email="clienteb@test.com",
        )

    def test_admin_lista_sus_clientes(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [str(c["id"]) for c in response.data]
        self.assertIn(str(self.cliente_a.id), ids)

    def test_aislamiento_no_ve_clientes_de_otra_empresa(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        ids = [str(c["id"]) for c in response.data]
        self.assertNotIn(str(self.cliente_b.id), ids)

    def test_empresa_b_no_ve_clientes_de_empresa_a(self):
        self.autenticar_admin_b()
        response = self.client.get(self.URL)

        ids = [str(c["id"]) for c in response.data]
        self.assertNotIn(str(self.cliente_a.id), ids)


class ClienteCreateTests(BaseClientesTest):

    URL = "/api/clients/"

    def _payload(self, nombre="Nuevo Cliente"):
        return {
            "nombre": nombre,
            "tipo": "empresa",
            "email": "nuevo@cliente.com",
            "estado_cliente": str(self.estado.id),
        }

    def test_admin_puede_crear_cliente(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombre"], "Nuevo Cliente")

    def test_cliente_creado_pertenece_a_la_empresa(self):
        self.autenticar_admin()
        self.client.post(self.URL, self._payload(), format="json")

        cliente = Cliente.objects.get(nombre="Nuevo Cliente")
        self.assertEqual(cliente.empresa, self.empresa)

    def test_no_se_puede_crear_cliente_con_estado_de_otra_empresa(self):
        """
        Validación crítica de seguridad multiempresa.
        """
        self.autenticar_admin()
        payload = self._payload()
        payload["estado_cliente"] = str(self.estado_b.id)  # Estado de empresa B

        response = self.client.post(self.URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_create_clientes(self):
        self.autenticar_admin()
        payload = [
            {
                "nombre": "Bulk Cliente 1",
                "tipo": "empresa",
                "estado_cliente": str(self.estado.id),
            },
            {
                "nombre": "Bulk Cliente 2",
                "tipo": "persona",
                "estado_cliente": str(self.estado.id),
            },
        ]

        response = self.client.post(self.URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)

    def test_comercial_puede_crear_cliente(self):
        self.autenticar_comercial()
        response = self.client.post(self.URL, self._payload(nombre="Cliente Comercial"), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sin_autenticar_devuelve_401(self):
        response = self.client.post(self.URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ClienteUpdateTests(BaseClientesTest):

    def setUp(self):
        super().setUp()
        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            estado_cliente=self.estado,
            nombre="Cliente Editable",
            tipo="empresa",
        )

    def _url(self):
        return f"/api/clients/{self.cliente.id}/"

    def test_admin_puede_actualizar_cliente(self):
        self.autenticar_admin()
        response = self.client.patch(self._url(), {
            "nombre": "Cliente Actualizado",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nombre"], "Cliente Actualizado")

    def test_comercial_puede_actualizar_cliente(self):
        self.autenticar_comercial()
        response = self.client.patch(self._url(), {
            "nombre": "Actualizado por Comercial",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comercial_no_puede_eliminar_cliente(self):
        self.autenticar_comercial()
        response = self.client.delete(self._url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_eliminar_cliente(self):
        self.autenticar_admin()
        response = self.client.delete(self._url())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
