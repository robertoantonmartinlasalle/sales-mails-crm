from rest_framework.routers import DefaultRouter

from clients.views.estado_cliente_viewset import EstadoClienteViewSet
from clients.views.cliente_viewset import ClienteViewSet

"""
Router de la app clients.

Aquí registramos todos los endpoints de la app.
DRF se encarga automáticamente de generar las URLs.
"""
router = DefaultRouter()

# Endpoint: /api/estado-clientes/
router.register(
    r"client-status",
    EstadoClienteViewSet,
    basename="estado-cliente"
)

# Endpoint: /api/clientes/
router.register(
    r"clients",
    ClienteViewSet,
    basename="cliente"
)

# Exponemos las rutas generadas
urlpatterns = router.urls