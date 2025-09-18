from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileViewSet, AmbienteViewSet, AtivoViewSet,
    ChamadoViewSet, ChamadoStatusHistoryViewSet, AnexoViewSet
)

router = DefaultRouter()
router.register(r'users', UserProfileViewSet)
router.register(r'ambientes', AmbienteViewSet)
router.register(r'ativos', AtivoViewSet)
router.register(r'chamados', ChamadoViewSet)
router.register(r'historico', ChamadoStatusHistoryViewSet)
router.register(r'anexos', AnexoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]