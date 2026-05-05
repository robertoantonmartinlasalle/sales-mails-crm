from rest_framework.routers import DefaultRouter

from crm.views import OportunidadViewSet

from crm.views import OportunidadViewSet, ActividadViewSet

router = DefaultRouter()

router.register(r"oportunidades", OportunidadViewSet, basename="oportunidad")

router.register(r"actividades", ActividadViewSet, basename="actividad")

urlpatterns = router.urls
