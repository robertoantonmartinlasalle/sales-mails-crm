from rest_framework.routers import DefaultRouter
from campaigns.views.plantilla_email_viewset import PlantillaEmailViewSet
from campaigns.views.campana_email_viewset import CampanaEmailViewSet
from campaigns.views.campaign_send_viewset import CampaignSendViewSet
router = DefaultRouter()
router.register(r"plantillas", PlantillaEmailViewSet, basename="plantilla")
router.register(r"campanas", CampanaEmailViewSet, basename="campana")
router.register(r"campaign-sends", CampaignSendViewSet, basename="campaign-send")
urlpatterns = router.urls


