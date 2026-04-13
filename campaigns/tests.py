from unittest.mock import patch

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
from campaigns.models.plantillaemail import PlantillaEmail
from campaigns.models.campanaemail import CampanaEmail
from campaigns.models.campaignsend import CampaignSend


class BaseCampanasTest(APITestCase):
    """
    Base compartida para los tests de campañas.
    Crea empresas, roles, usuarios, plantilla y campaña de prueba.
    """

    def setUp(self):
        # Empresa A
        self.empresa = crear_empresa(nombre="Empresa A")
        self.rol_admin = crear_rol(self.empresa, nombre="Administrador")
        self.rol_comercial = crear_rol(self.empresa, nombre="Comercial")

        self.admin = crear_usuario(
            self.empresa, self.rol_admin,
            email="admin@empresa-a.com", password="testpass123",
        )
        self.comercial = crear_usuario(
            self.empresa, self.rol_comercial,
            email="comercial@empresa-a.com", password="testpass123",
        )

        # Empresa B (para aislamiento)
        self.empresa_b = crear_empresa(nombre="Empresa B", cif="B12345678")
        self.rol_admin_b = crear_rol(self.empresa_b, nombre="Administrador")
        self.admin_b = crear_usuario(
            self.empresa_b, self.rol_admin_b,
            email="admin@empresa-b.com", password="testpass123",
        )

        # Plantilla compartida
        self.plantilla = PlantillaEmail.objects.create(
            nombre="Plantilla Test",
            asunto="Asunto de prueba",
            cuerpo="Hola {{nombre}}, este es un email de prueba.",
        )

        # Campaña empresa A
        self.campana = CampanaEmail.objects.create(
            empresa=self.empresa,
            nombre="Campaña Test A",
            plantilla=self.plantilla,
        )

        # Campaña empresa B
        self.campana_b = CampanaEmail.objects.create(
            empresa=self.empresa_b,
            nombre="Campaña Test B",
            plantilla=self.plantilla,
        )

        # Cliente y estado para envíos
        self.estado = EstadoCliente.objects.create(
            empresa=self.empresa, nombre="Activo", orden=1,
        )
        self.cliente = Cliente.objects.create(
            empresa=self.empresa,
            estado_cliente=self.estado,
            nombre="Cliente Campaña",
            tipo="empresa",
            email="cliente@campaña.com",
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
# PLANTILLA EMAIL
# ==============================================================

class PlantillaEmailListTests(BaseCampanasTest):

    URL = "/api/plantillas/"

    def test_admin_puede_listar_plantillas(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_sin_autenticar_devuelve_401(self):
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PlantillaEmailCreateTests(BaseCampanasTest):

    URL = "/api/plantillas/"

    def _payload(self, nombre="Nueva Plantilla"):
        return {
            "nombre": nombre,
            "asunto": "Asunto nuevo",
            "cuerpo": "Contenido del email",
        }

    def test_admin_puede_crear_plantilla(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombre"], "Nueva Plantilla")

    def test_no_se_puede_crear_plantilla_con_nombre_vacio(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, {
            "nombre": "",
            "asunto": "Asunto",
            "cuerpo": "Contenido",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_create_plantillas(self):
        self.autenticar_admin()
        payload = [
            {"nombre": "Plantilla Bulk 1", "asunto": "Asunto 1", "cuerpo": "Cuerpo 1"},
            {"nombre": "Plantilla Bulk 2", "asunto": "Asunto 2", "cuerpo": "Cuerpo 2"},
        ]

        response = self.client.post(self.URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)

    def test_comercial_no_puede_eliminar_plantilla(self):
        self.autenticar_comercial()
        response = self.client.delete(f"/api/plantillas/{self.plantilla.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_eliminar_plantilla(self):
        self.autenticar_admin()
        response = self.client.delete(f"/api/plantillas/{self.plantilla.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# ==============================================================
# CAMPAÑA EMAIL
# ==============================================================

class CampanaEmailListTests(BaseCampanasTest):

    URL = "/api/campaigns/"

    def test_admin_lista_sus_campanas(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [str(c["id"]) for c in response.data]
        self.assertIn(str(self.campana.id), ids)

    def test_aislamiento_no_ve_campanas_de_otra_empresa(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        ids = [str(c["id"]) for c in response.data]
        self.assertNotIn(str(self.campana_b.id), ids)

    def test_empresa_b_no_ve_campanas_de_empresa_a(self):
        self.autenticar_admin_b()
        response = self.client.get(self.URL)

        ids = [str(c["id"]) for c in response.data]
        self.assertNotIn(str(self.campana.id), ids)


class CampanaEmailCreateTests(BaseCampanasTest):

    URL = "/api/campaigns/"

    def test_admin_puede_crear_campana(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, {
            "nombre": "Nueva Campaña",
            "plantilla": str(self.plantilla.id),
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombre"], "Nueva Campaña")

    def test_campana_creada_pertenece_a_la_empresa(self):
        self.autenticar_admin()
        self.client.post(self.URL, {
            "nombre": "Campaña Empresa",
            "plantilla": str(self.plantilla.id),
        }, format="json")

        campana = CampanaEmail.objects.get(nombre="Campaña Empresa")
        self.assertEqual(campana.empresa, self.empresa)

    def test_comercial_puede_crear_campana(self):
        self.autenticar_comercial()
        response = self.client.post(self.URL, {
            "nombre": "Campaña Comercial",
            "plantilla": str(self.plantilla.id),
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comercial_no_puede_eliminar_campana(self):
        self.autenticar_comercial()
        response = self.client.delete(f"/api/campaigns/{self.campana.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ==============================================================
# CAMPAIGN SEND
# ==============================================================

class CampaignSendListTests(BaseCampanasTest):

    URL = "/api/campaign-sends/"

    def setUp(self):
        super().setUp()
        self.envio_a = CampaignSend.objects.create(
            empresa=self.empresa,
            campana=self.campana,
            cliente=self.cliente,
            estado="pendiente",
        )

        estado_b = EstadoCliente.objects.create(empresa=self.empresa_b, nombre="Activo", orden=1)
        cliente_b = Cliente.objects.create(
            empresa=self.empresa_b,
            estado_cliente=estado_b,
            nombre="Cliente B",
            tipo="empresa",
            email="b@b.com",
        )
        self.envio_b = CampaignSend.objects.create(
            empresa=self.empresa_b,
            campana=self.campana_b,
            cliente=cliente_b,
            estado="pendiente",
        )

    def test_admin_lista_sus_envios(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [str(e["id"]) for e in response.data]
        self.assertIn(str(self.envio_a.id), ids)

    def test_aislamiento_no_ve_envios_de_otra_empresa(self):
        self.autenticar_admin()
        response = self.client.get(self.URL)

        ids = [str(e["id"]) for e in response.data]
        self.assertNotIn(str(self.envio_b.id), ids)


class CampaignSendCreateTests(BaseCampanasTest):

    URL = "/api/campaign-sends/"

    def test_admin_puede_crear_envio(self):
        self.autenticar_admin()
        response = self.client.post(self.URL, {
            "campana": str(self.campana.id),
            "cliente": str(self.cliente.id),
            "estado": "pendiente",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["estado"], "pendiente")

    def test_envio_creado_pertenece_a_la_empresa(self):
        self.autenticar_admin()
        self.client.post(self.URL, {
            "campana": str(self.campana.id),
            "cliente": str(self.cliente.id),
        }, format="json")

        envio = CampaignSend.objects.filter(campana=self.campana).first()
        self.assertEqual(envio.empresa, self.empresa)


class CampaignSendEnviarTests(BaseCampanasTest):

    def setUp(self):
        super().setUp()
        self.envio = CampaignSend.objects.create(
            empresa=self.empresa,
            campana=self.campana,
            cliente=self.cliente,
            estado="pendiente",
        )

    def _url_enviar(self):
        return f"/api/campaign-sends/{self.envio.id}/enviar/"

    @patch("campaigns.views.campaign_send_viewset.send_email", return_value=(True, None))
    def test_enviar_email_exitoso(self, mock_send):
        self.autenticar_admin()
        response = self.client.post(self._url_enviar(), format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.envio.refresh_from_db()
        self.assertEqual(self.envio.estado, "enviado")
        self.assertIsNotNone(self.envio.fecha_envio)
        self.assertIsNone(self.envio.error_mensaje)
        mock_send.assert_called_once()

    @patch("campaigns.views.campaign_send_viewset.send_email", return_value=(False, "Connection refused"))
    def test_enviar_email_con_error_de_envio(self, mock_send):
        self.autenticar_admin()
        response = self.client.post(self._url_enviar(), format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.envio.refresh_from_db()
        self.assertEqual(self.envio.estado, "error")
        self.assertEqual(self.envio.error_mensaje, "Connection refused")

    @patch("campaigns.views.campaign_send_viewset.send_email", return_value=(True, None))
    def test_no_se_puede_reenviar_email_ya_enviado(self, mock_send):
        self.envio.estado = "enviado"
        self.envio.save()

        self.autenticar_admin()
        response = self.client.post(self._url_enviar(), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_send.assert_not_called()


class CampaignSendEnviarMasivoTests(BaseCampanasTest):

    URL_MASIVO = "/api/campaign-sends/enviar-masivo/"

    def setUp(self):
        super().setUp()
        # Crear un segundo cliente y dos envíos pendientes
        self.cliente2 = Cliente.objects.create(
            empresa=self.empresa,
            estado_cliente=self.estado,
            nombre="Cliente Masivo 2",
            tipo="persona",
            email="masivo2@test.com",
        )
        self.envio1 = CampaignSend.objects.create(
            empresa=self.empresa,
            campana=self.campana,
            cliente=self.cliente,
            estado="pendiente",
        )
        self.envio2 = CampaignSend.objects.create(
            empresa=self.empresa,
            campana=self.campana,
            cliente=self.cliente2,
            estado="pendiente",
        )

    @patch("campaigns.views.campaign_send_viewset.send_email", return_value=(True, None))
    def test_enviar_masivo_marca_todos_como_enviados(self, mock_send):
        self.autenticar_admin()
        response = self.client.post(self.URL_MASIVO, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.envio1.refresh_from_db()
        self.envio2.refresh_from_db()
        self.assertEqual(self.envio1.estado, "enviado")
        self.assertEqual(self.envio2.estado, "enviado")

    @patch("campaigns.views.campaign_send_viewset.send_email", return_value=(True, None))
    def test_enviar_masivo_no_procesa_envios_ya_enviados(self, mock_send):
        self.envio1.estado = "enviado"
        self.envio1.save()

        self.autenticar_admin()
        self.client.post(self.URL_MASIVO, format="json")

        # Solo debe haberse llamado para el envio2
        self.assertEqual(mock_send.call_count, 1)
