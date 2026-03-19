from rest_framework.routers import DefaultRouter

from clients.views.estado_cliente_viewset import EstadoClienteViewSet


"""
Router de la app clients.

Aquí registramos todos los endpoints de la app.
DRF se encarga automáticamente de generar las URLs.
"""
router = DefaultRouter()

# Endpoint: /api/estado-clientes/
router.register(
    r"estado-clientes",
    EstadoClienteViewSet,
    basename="estado-cliente"
)

# Exponemos las rutas generadas
urlpatterns = router.urls