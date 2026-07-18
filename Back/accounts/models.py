from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('AGENT_FACTURATION', 'Agent Facturation'),
        ('PAYEUR', 'Payeur'),
        ('EMPLOYE', 'Employé'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYE')
    telephone = models.CharField(max_length=15, blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.email} ({self.role})"
