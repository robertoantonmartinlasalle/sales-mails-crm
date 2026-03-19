from rest_framework.routers import DefaultRouter
from campaigns.views.plantilla_email_viewset import PlantillaEmailViewSet

router = DefaultRouter()
router.register(r"plantillas", PlantillaEmailViewSet, basename="plantilla")

urlpatterns = router.urls