from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('CHEF_FACTURATION', 'Chef Facturation'),  # Nouveau rôle
        ('AGENT_FACTURATION', 'Agent Facturation'),
        ('PAYEUR', 'Payeur'),
        ('EMPLOYE', 'Employé'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('SUSPENDU', 'Suspendu'),
        ('EN_ATTENTE', 'En attente'),
        ('BLOQUE', 'Bloqué'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYE')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIF')
    telephone = models.CharField(max_length=15, blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    
    # Permissions personnalisées (JSON)
    custom_permissions = models.JSONField(default=list, blank=True)
    
    # Gestion des statuts
    status_changed_at = models.DateTimeField(null=True, blank=True)
    status_changed_by = models.ForeignKey(
        'self', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='changed_statuses'
    )
    status_reason = models.TextField(blank=True)
    status_end_date = models.DateTimeField(null=True, blank=True)  # Réactivation auto
    
    # Traçabilité
    created_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_users'
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def has_permission(self, permission):
        """Vérifie si l'utilisateur a une permission spécifique"""
        if self.status != 'ACTIF':
            return False
        
        # Super admin a toutes les permissions
        if self.role == 'SUPER_ADMIN':
            return True
        
        # Permissions du rôle par défaut
        role_permissions = ROLE_PERMISSIONS.get(self.role, [])
        if permission in role_permissions or '*' in role_permissions:
            return True
        
        # Permissions personnalisées
        if permission in self.custom_permissions:
            return True
        
        return False
    
    def can_manage_user(self, target_user):
        """Vérifie si cet utilisateur peut gérer un autre utilisateur"""
        if self.role == 'SUPER_ADMIN':
            return True
        
        if self.role == 'CHEF_FACTURATION':
            # Un chef ne peut gérer que ses agents
            return (target_user.role == 'AGENT_FACTURATION' and 
                    target_user.created_by == self)
        
        return False


class StatusHistory(models.Model):
    """Historique des changements de statut"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes_made'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'status_history'
        ordering = ['-changed_at']
        verbose_name = 'Historique de statut'
        verbose_name_plural = 'Historiques de statuts'
    
    def __str__(self):
        return f"{self.user.email}: {self.old_status} → {self.new_status}"


# Permissions par rôle
ROLE_PERMISSIONS = {
    'SUPER_ADMIN': ['*'],  # Toutes les permissions
    
    'CHEF_FACTURATION': [
        'accounts.create_agent',
        'accounts.view_all',
        'accounts.edit_agents',
        'accounts.change_status_agents',
        'accounts.reset_password_agents',
        'billing.publish',
        'billing.cancel',
        'billing.view_all',
        'billing.export',
        'tarifs.create',
        'tarifs.edit',
        'tarifs.activate',
        'services.create',
        'services.edit',
        'services.activate',
        'reports.view_all',
        'reports.export',
        'system.view_logs',
    ],
    
    'AGENT_FACTURATION': [
        'billing.publish',
        'billing.view_all',
        'tarifs.create',
        'services.create',
        'reports.view_all',
    ],
    
    'PAYEUR': [
        'billing.view_own',
        'billing.export_own',
    ],
    
    'EMPLOYE': [
        'billing.view_own',
    ],
}
