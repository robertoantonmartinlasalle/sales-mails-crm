from rest_framework.routers import DefaultRouter

from campaigns.views.plantilla_email_viewset import PlantillaEmailViewSet
from campaigns.views.campana_email_viewset import CampanaEmailViewSet
from campaigns.views.campaign_send_viewset import CampaignSendViewSet

"""
Router principal de la app de campañas.

Aquí registramos todos los ViewSets para que Django REST
genere automáticamente las URLs.

Esto nos evita definir manualmente cada endpoint.
"""
router = DefaultRouter()

"""
Plantillas de email.

Endpoints generados:
- GET     /api/templates/
- POST    /api/templates/
- GET     /api/templates/{id}/
- PUT     /api/templates/{id}/
- DELETE  /api/templates/{id}/
"""
router.register(r"templates", PlantillaEmailViewSet, basename="plantilla")

"""
Campañas de email.

Endpoints generados:
- GET     /api/campaigns/
- POST    /api/campaigns/
- GET     /api/campaigns/{id}/
- PUT     /api/campaigns/{id}/
- DELETE  /api/campaigns/{id}/
"""
router.register(r"campaigns", CampanaEmailViewSet, basename="campana")

"""
Envíos de campañas.

Endpoints generados:
- GET     /api/campaign-sends/
- POST    /api/campaign-sends/
- GET     /api/campaign-sends/{id}/
- PUT     /api/campaign-sends/{id}/
- DELETE  /api/campaign-sends/{id}/

Acciones personalizadas:
- POST /api/campaign-sends/{id}/enviar/
- POST /api/campaign-sends/enviar-masivo/
"""
router.register(r"campaign-sends", CampaignSendViewSet, basename="campaign-send")

"""
Exportamos las URLs generadas por el router.
"""
urlpatterns = router.urls