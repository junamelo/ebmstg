"""
URLs pour l'application billing
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet, LineViewSet,
    PackageViewSet, ServiceViewSet, TarifServiceViewSet,
    InvoiceViewSet, PublicationViewSet, CommercialViewSet,
    SimulationViewSet
)
from .stats_views import (
    stats_admin, stats_chef_facturation, stats_agent_facturation,
    stats_payeur, stats_employe
)

# Router pour les endpoints RESTful
router = DefaultRouter()
# Phase 2
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'lines', LineViewSet, basename='line')
# Phase 3
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'tarifs', TarifServiceViewSet, basename='tarif')
# Phase 4
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'publications', PublicationViewSet, basename='publication')
# Phase 6 : Commerciaux
router.register(r'commerciaux', CommercialViewSet, basename='commercial')
# Phase 7 : Simulations
router.register(r'simulations', SimulationViewSet, basename='simulation')

urlpatterns = [
    path('', include(router.urls)),
    
    # Phase 5 : Statistiques par rôle
    path('stats/admin/', stats_admin, name='stats-admin'),
    path('stats/chef/', stats_chef_facturation, name='stats-chef'),
    path('stats/agent/', stats_agent_facturation, name='stats-agent'),
    path('stats/payeur/', stats_payeur, name='stats-payeur'),
    path('stats/employe/', stats_employe, name='stats-employe'),
]

