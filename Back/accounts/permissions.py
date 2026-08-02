"""
Permissions personnalisées pour l'application
"""
from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission pour les super administrateurs uniquement
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'SUPER_ADMIN'


class IsChefFacturation(permissions.BasePermission):
    """
    Permission pour les chefs de facturation
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION']


class IsAgentFacturation(permissions.BasePermission):
    """
    Permission pour les agents de facturation
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']


class IsPayeur(permissions.BasePermission):
    """
    Permission pour les payeurs
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'PAYEUR'


class IsEmploye(permissions.BasePermission):
    """
    Permission pour les employés
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'EMPLOYE'


class HasCustomPermission(permissions.BasePermission):
    """
    Permission basée sur les permissions personnalisées de l'utilisateur
    Usage: permission_classes = [HasCustomPermission]
    Doit définir permission_required dans la vue
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Vérifier si la vue définit une permission requise
        permission_required = getattr(view, 'permission_required', None)
        if not permission_required:
            return True  # Pas de permission spécifique requise
        
        return request.user.has_permission(permission_required)


class CanManageUser(permissions.BasePermission):
    """
    Permission pour gérer d'autres utilisateurs
    """
    def has_object_permission(self, request, view, obj):
        return request.user.can_manage_user(obj)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission pour l'utilisateur lui-même ou un admin
    """
    def has_object_permission(self, request, view, obj):
        # Super admin peut tout faire
        if request.user.role == 'SUPER_ADMIN':
            return True
        
        # Chef peut gérer ses agents
        if request.user.role == 'CHEF_FACTURATION':
            return request.user.can_manage_user(obj)
        
        # Utilisateur peut gérer son propre compte
        return obj.id == request.user.id


class IsActiveUser(permissions.BasePermission):
    """
    Permission pour les utilisateurs actifs uniquement
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.status == 'ACTIF' and 
            request.user.est_actif
        )


class CanCreateUser(permissions.BasePermission):
    """
    Permission pour créer des utilisateurs
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admin peut créer n'importe qui
        if request.user.role == 'SUPER_ADMIN':
            return True
        
        # Chef peut créer des agents
        if request.user.role == 'CHEF_FACTURATION':
            return True
        
        # Agent peut créer des payeurs et employés
        if request.user.role == 'AGENT_FACTURATION':
            return True
        
        return False


class CanPublishInvoices(permissions.BasePermission):
    """
    Permission pour publier des factures
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.has_permission('billing.publish')


class CanCancelInvoices(permissions.BasePermission):
    """
    Permission pour annuler des factures
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.has_permission('billing.cancel')


class CanManageTarifs(permissions.BasePermission):
    """
    Permission pour gérer les tarifs
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture nécessite permission
        return request.user.has_permission('tarifs.edit')


class CanManageServices(permissions.BasePermission):
    """
    Permission pour gérer les services
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture nécessite permission
        return request.user.has_permission('services.edit')


# ==================== PERMISSIONS PHASE 4 : FACTURATION ====================

class CanGenerateInvoices(permissions.BasePermission):
    """
    Permission pour générer des factures
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin, Chef, Agent peuvent générer
        return request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']


class CanManageInvoices(permissions.BasePermission):
    """
    Permission pour gérer les factures (CRUD)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Lecture : Admin, Chef, Agent, Payeur (ses factures)
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION', 'PAYEUR', 'EMPLOYE']
        
        # Écriture : Admin, Chef, Agent uniquement
        return request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']


class CanUploadPDF(permissions.BasePermission):
    """
    Permission pour uploader des PDF de factures
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin, Chef, Agent peuvent uploader
        return request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']


class CanValidateInvoices(permissions.BasePermission):
    """
    Permission pour valider des factures
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin, Chef, Agent peuvent valider
        return request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']
