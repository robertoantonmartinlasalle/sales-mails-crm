from rest_framework.routers import DefaultRouter

from users.views.usuario_viewset import UsuarioViewSet

"""
Router de la app users.

Aquí registramos los endpoints relacionados con usuarios.

DRF generará automáticamente:
- GET     /api/usuarios/
- POST    /api/usuarios/
- GET     /api/usuarios/{id}/
- PUT     /api/usuarios/{id}/
- DELETE  /api/usuarios/{id}/
"""

router = DefaultRouter()

router.register(
    r"usuarios",
    UsuarioViewSet,
    basename="usuario"
)

urlpatterns = router.urls