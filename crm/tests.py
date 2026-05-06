from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import (
    autenticar,
    crear_empresa,
    crear_rol,
    crear_usuario,
    obtener_token,
)
from clients.models.estadoCliente import EstadoCliente
from clients.models.cliente import Cliente
from crm.models import Oportunidad


class BaseOportunidadTest(APITestCase):
    """
    Base compartida: crea dos empresas con usuarios, estados y clientes.
    """

    URL = "/api/oportunidades/"

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

        self.estado = EstadoCliente.objects.create(
            empresa=self.empresa, nombre="Activo", orden=1,
        )
        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            estado_cliente=self.estado,
            nombre="Cliente A",
            tipo="empresa",
            email="clientea@test.com",
        )

        # Empresa B (para aislamiento)
        self.empresa_b = crear_empresa(nombre="Empresa B", cif="B12345678")
        self.rol_admin_b = crear_rol(self.empresa_b, nombre="ADMIN")
        self.admin_b = crear_usuario(
            self.empresa_b, self.rol_admin_b,
            email="admin@empresa-b.com", password="testpass123",
        )
        self.estado_b = EstadoCliente.objects.create(
            empresa=self.empresa_b, nombre="Activo", orden=1,
        )
        self.cliente_b = Cliente.objects.create(
            empresa=self.empresa_b,
            estado_cliente=self.estado_b,
            nombre="Cliente B",
            tipo="empresa",
            email="clienteb@test.com",
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

    def _crear_oportunidad(self, empresa=None, cliente=None, usuario=None, **kwargs):
        empresa = empresa or self.empresa
        cliente = cliente or self.cliente
        usuario = usuario or self.admin
        return Oportunidad.objects.create(
            empresa=empresa,
            cliente=cliente,
            usuario_responsable=usuario,
            titulo=kwargs.get("titulo", "Oportunidad Test"),
            estado=kwargs.get("estado", "abierta"),
            valor_estimado=kwargs.get("valor_estimado", None),
            probabilidad=kwargs.get("probabilidad", None),
        )


# ==============================================================
# LIST
# ==============================================================

class OportunidadListTests(BaseOportunidadTest):

    def test_admin_puede_listar_oportunidades(self):
        self._crear_oportunidad()
        self.autenticar_admin()
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_sin_autenticar_devuelve_401(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_aislamiento_no_ve_oportunidades_de_otra_empresa(self):
        self._crear_oportunidad()
        self._crear_oportunidad(
            empresa=self.empresa_b,
            cliente=self.cliente_b,
            usuario=self.admin_b,
        )
        self.autenticar_admin()
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_empresa_b_no_ve_oportunidades_de_empresa_a(self):
        self._crear_oportunidad()
        self.autenticar_admin_b()
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_filtro_por_cliente(self):
        op1 = self._crear_oportunidad(titulo="Op 1")
        cliente2 = Cliente.objects.create(
            empresa=self.empresa,
            estado_cliente=self.estado,
            nombre="Cliente 2",
            tipo="empresa",
            email="cliente2@test.com",
        )
        self._crear_oportunidad(cliente=cliente2, titulo="Op 2")

        self.autenticar_admin()
        response = self.client.get(self.URL, {"cliente": op1.cliente.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["titulo"], "Op 1")


# ==============================================================
# CREATE
# ==============================================================

class OportunidadCreateTests(BaseOportunidadTest):

    def _payload(self, **kwargs):
        return {
            "titulo": "Nueva oportunidad",
            "cliente": self.cliente.id,
            "estado": "abierta",
            **kwargs,
        }

    def test_admin_puede_crear_oportunidad(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["titulo"], "Nueva oportunidad")

    def test_oportunidad_creada_pertenece_a_la_empresa(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        op = Oportunidad.objects.get(id=response.data["id"])
        self.assertEqual(op.empresa, self.empresa)

    def test_comercial_puede_crear_oportunidad(self):
        self.autenticar_comercial()
        response = self.client.post(self.URL, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_sin_autenticar_no_puede_crear(self):
        response = self.client.post(self.URL, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_se_puede_crear_con_cliente_de_otra_empresa(self):
        self.autenticar_admin()
        response = self.client.post(
            self.URL,
            self._payload(cliente=self.cliente_b.id),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fecha_cierre_pasada_devuelve_400(self):
        self.autenticar_admin()
        ayer = (timezone.now() - timezone.timedelta(days=1)).date().isoformat()
        response = self.client.post(
            self.URL,
            self._payload(fecha_cierre_prevista=ayer),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ==============================================================
# UPDATE
# ==============================================================

class OportunidadUpdateTests(BaseOportunidadTest):

    def test_admin_puede_actualizar_titulo(self):
        op = self._crear_oportunidad()
        self.autenticar_admin()
        response = self.client.patch(
            f"{self.URL}{op.id}/",
            {"titulo": "Título actualizado"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], "Título actualizado")

    def test_no_se_puede_pasar_a_ganada_sin_valor_estimado(self):
        op = self._crear_oportunidad(probabilidad=80)
        self.autenticar_admin()
        response = self.client.patch(
            f"{self.URL}{op.id}/",
            {"estado": "ganada"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_se_puede_pasar_a_ganada_sin_probabilidad(self):
        op = self._crear_oportunidad(valor_estimado="5000.00")
        self.autenticar_admin()
        response = self.client.patch(
            f"{self.URL}{op.id}/",
            {"estado": "ganada"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_se_puede_pasar_a_ganada_con_valor_y_probabilidad(self):
        op = self._crear_oportunidad(valor_estimado="5000.00", probabilidad=90)
        self.autenticar_admin()
        response = self.client.patch(
            f"{self.URL}{op.id}/",
            {"estado": "ganada"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["estado"], "ganada")

    def test_no_se_puede_pasar_a_perdida_sin_valor_estimado(self):
        op = self._crear_oportunidad(probabilidad=10)
        self.autenticar_admin()
        response = self.client.patch(
            f"{self.URL}{op.id}/",
            {"estado": "perdida"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empresa_b_no_puede_actualizar_oportunidad_de_empresa_a(self):
        op = self._crear_oportunidad()
        self.autenticar_admin_b()
        response = self.client.patch(
            f"{self.URL}{op.id}/",
            {"titulo": "Hack"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ==============================================================
# DELETE
# ==============================================================

class OportunidadDeleteTests(BaseOportunidadTest):

    def test_admin_puede_eliminar_oportunidad(self):
        op = self._crear_oportunidad()
        self.autenticar_admin()
        response = self.client.delete(f"{self.URL}{op.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Oportunidad.objects.filter(id=op.id).exists())

    def test_comercial_puede_eliminar_oportunidad(self):
        op = self._crear_oportunidad()
        self.autenticar_comercial()
        response = self.client.delete(f"{self.URL}{op.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_empresa_b_no_puede_eliminar_oportunidad_de_empresa_a(self):
        op = self._crear_oportunidad()
        self.autenticar_admin_b()
        response = self.client.delete(f"{self.URL}{op.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

