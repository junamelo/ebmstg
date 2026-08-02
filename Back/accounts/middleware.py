"""
Middleware personnalisés pour la sécurité et l'audit
"""
import logging
from django.utils import timezone
from django.db import models

logger = logging.getLogger('security')


class AuditLogMiddleware:
    """
    Middleware pour logger les actions sensibles
    """
    
    SENSITIVE_PATHS = [
        '/api/accounts/users/',
        '/api/accounts/change-password/',
        '/api/billing/invoices/',
        '/api/billing/publish/',
    ]
    
    SENSITIVE_ACTIONS = [
        'POST', 'PUT', 'PATCH', 'DELETE'
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Avant la requête
        start_time = timezone.now()
        
        # Traiter la requête
        response = self.get_response(request)
        
        # Après la requête - logger si action sensible
        if self._is_sensitive_action(request):
            self._log_action(request, response, start_time)
        
        return response
    
    def _is_sensitive_action(self, request):
        """Vérifie si l'action est sensible"""
        if request.method not in self.SENSITIVE_ACTIONS:
            return False
        
        for path in self.SENSITIVE_PATHS:
            if request.path.startswith(path):
                return True
        
        return False
    
    def _log_action(self, request, response, start_time):
        """Logger l'action"""
        duration = (timezone.now() - start_time).total_seconds()
        
        user = request.user if request.user.is_authenticated else 'Anonymous'
        
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'user': str(user),
            'user_id': getattr(request.user, 'id', None),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration': f'{duration:.3f}s',
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
        }
        
        if response.status_code >= 400:
            logger.warning(f'Sensitive action failed: {log_data}')
        else:
            logger.info(f'Sensitive action: {log_data}')
    
    def _get_client_ip(self, request):
        """Récupère l'IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CheckUserStatusMiddleware:
    """
    Middleware pour vérifier automatiquement le statut de l'utilisateur
    et réactiver si la date de fin est dépassée
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier le statut de l'utilisateur avant la requête
        if request.user.is_authenticated:
            self._check_user_status(request.user)
        
        response = self.get_response(request)
        return response
    
    def _check_user_status(self, user):
        """Vérifier et mettre à jour le statut si nécessaire"""
        if user.status == 'SUSPENDU' and user.status_end_date:
            if timezone.now() >= user.status_end_date:
                # Réactiver automatiquement
                from .models import StatusHistory
                
                StatusHistory.objects.create(
                    user=user,
                    old_status='SUSPENDU',
                    new_status='ACTIF',
                    changed_by=None,
                    reason='Réactivation automatique après expiration de la période de suspension'
                )
                
                user.status = 'ACTIF'
                user.status_changed_at = timezone.now()
                user.status_changed_by = None
                user.status_reason = 'Réactivation automatique'
                user.status_end_date = None
                user.save()
                
                logger.info(f'Auto-reactivated user {user.email} after suspension period')
