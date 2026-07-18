from django.db import models
from accounts.models import User

class CategorieClient(models.TextChoices):
    GRANDE_ENTREPRISE = 'GE', 'Grande Entreprise'
    PETITE_ENTREPRISE = 'PE', 'Petite Entreprise'
    PARTICULIER = 'P', 'Particulier'
    ORGANISME_INTERNATIONAL = 'OI', 'Organisme International'
    ENTREPRISE_PUBLIQUE = 'EP', 'Entreprise Publique'
    ASSOCIATION = 'A', 'Association'
    NON_REVENU = 'NR', 'Non Revenu'

class CycleFacturation(models.TextChoices):
    HYB1 = 'HYB1', 'Hybride 1'
    HYB2 = 'HYB2', 'Hybride 2'
    MON1 = 'MON1', 'Mensuel 1'

class Company(models.Model):
    compte = models.CharField(max_length=20, unique=True, verbose_name='Compte')
    raison_sociale = models.CharField(max_length=200, verbose_name='Raison Sociale')
    code_commercial = models.CharField(max_length=10, blank=True, null=True, verbose_name='Code Commercial')
    nom_commercial = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nom Commercial')
    categorie = models.CharField(
        max_length=5, 
        choices=CategorieClient.choices,
        default=CategorieClient.PETITE_ENTREPRISE,
        verbose_name='Catégorie Client'
    )
    adresse = models.TextField(blank=True, null=True, verbose_name='Adresse')
    adresse2 = models.EmailField(blank=True, null=True, verbose_name='Email')
    statut = models.CharField(max_length=20, default='ACTIF', verbose_name='Statut')
    payeur = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='companies',
        verbose_name='Payeur'
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')
    
    class Meta:
        db_table = 'companies'
        verbose_name = 'Entreprise'
        verbose_name_plural = 'Entreprises'
        ordering = ['raison_sociale']
    
    def __str__(self):
        return f"{self.compte} - {self.raison_sociale}"

class Line(models.Model):
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='lines',
        verbose_name='Entreprise'
    )
    msisdn = models.CharField(max_length=15, unique=True, verbose_name='Numéro Mobile')
    utilisateur = models.CharField(max_length=100, blank=True, null=True, verbose_name='Utilisateur')
    forfait = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Forfait (FCFA)')
    cycle = models.CharField(
        max_length=10, 
        choices=CycleFacturation.choices,
        default=CycleFacturation.MON1,
        verbose_name='Cycle de Facturation'
    )
    option_blackberry = models.CharField(max_length=20, blank=True, null=True, verbose_name='Option BlackBerry')
    option_nolimit = models.CharField(max_length=20, blank=True, null=True, verbose_name='Option No Limit')
    est_incognito = models.BooleanField(default=False, verbose_name='Incognito')
    facture_detaillee = models.BooleanField(default=False, verbose_name='Facture Détaillée')
    est_non_revenu = models.BooleanField(default=False, verbose_name='Non Revenu')
    statut = models.CharField(max_length=20, default='ACTIF', verbose_name='Statut')
    employe = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lines',
        verbose_name='Employé'
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')
    
    class Meta:
        db_table = 'lines'
        verbose_name = 'Ligne'
        verbose_name_plural = 'Lignes'
        ordering = ['msisdn']
    
    def __str__(self):
        return f"{self.msisdn} - {self.utilisateur or 'N/A'}"
