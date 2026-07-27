from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet, LineViewSet, PackageViewSet,
    ServiceViewSet, TarifServiceViewSet, InvoiceViewSet,
    HistoriqueFacturationViewSet, CycleViewSet,
    SimulationViewSet, PublicationViewSet
)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'lines', LineViewSet)
router.register(r'packages', PackageViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'tarifs-services', TarifServiceViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'historique-facturation', HistoriqueFacturationViewSet)
router.register(r'cycles', CycleViewSet)
router.register(r'simulations', SimulationViewSet)
router.register(r'publications', PublicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
