from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, LineViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'lines', LineViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
