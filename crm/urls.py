from rest_framework.routers import DefaultRouter

from crm.views import OportunidadViewSet

router = DefaultRouter()

router.register(r"oportunidades", OportunidadViewSet, basename="oportunidad")

urlpatterns = router.urls
