from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, LogoutView, RefreshTokenView,
    ProfileView, ChangePasswordView, UserManagementViewSet,
    TwoFactorStatusView, TwoFactorSetupView, TwoFactorConfirmView, TwoFactorDisableView
)

# Router pour les endpoints RESTful
router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user')

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('two-factor/status/', TwoFactorStatusView.as_view(), name='two-factor-status'),
    path('two-factor/setup/', TwoFactorSetupView.as_view(), name='two-factor-setup'),
    path('two-factor/confirm/', TwoFactorConfirmView.as_view(), name='two-factor-confirm'),
    path('two-factor/disable/', TwoFactorDisableView.as_view(), name='two-factor-disable'),
    
    # Gestion des utilisateurs
    path('', include(router.urls)),
]
