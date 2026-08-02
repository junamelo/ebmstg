from django.db import models
from accounts.models import User
import uuid

class CategorieClient(models.TextChoices):
    GRANDE_ENTREPRISE = 'GE', 'Grande Entreprise'
    PETITE_ENTREPRISE = 'PE', 'Petite Entreprise'
    PARTICULIER = 'P', 'Particulier'
    ORGANISME_INTERNATIONAL = 'OI', 'Organisme International'
    ENTREPRISE_PUBLIQUE = 'EP', 'Entreprise Publique'
    ASSOCIATION = 'A', 'Association'
    NON_REVENU = 'NR', 'Non Revenu'

class CycleFacturation(models.TextChoices):
    HYB = 'HYB', 'Hybride'
    OP = 'OP', 'Opérationnel'

class TypeForfait(models.TextChoices):
    DATA = 'DATA', 'Data'
    VOIX = 'VOIX', 'Voix'
    SMS = 'SMS', 'SMS'
    MIXTE = 'MIXTE', 'Mixte'

class TypeService(models.TextChoices):
    PASS = 'PASS', 'Pass'
    OPTION = 'OPTION', 'Option'
    PROMO = 'PROMO', 'Promotion'

class StatutFacture(models.TextChoices):
    BROUILLON = 'BROUILLON', 'Brouillon'
    EN_COURS = 'EN_COURS', 'En cours'
    VALIDEE = 'VALIDEE', 'Validée'
    PUBLIEE = 'PUBLIEE', 'Publiée'
    PAYEE = 'PAYEE', 'Payée'
    ANNULEE = 'ANNULEE', 'Annulée'

class TypeActionFacturation(models.TextChoices):
    CREATION = 'CREATION', 'Création'
    MODIFICATION = 'MODIFICATION', 'Modification'
    VALIDATION = 'VALIDATION', 'Validation'
    PUBLICATION = 'PUBLICATION', 'Publication'
    PAIEMENT = 'PAIEMENT', 'Paiement'
    ANNULATION = 'ANNULATION', 'Annulation'

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
        default=CycleFacturation.HYB,
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

# ==================== NOUVEAUX MODÈLES ====================

class Package(models.Model):
    """Modèle pour les forfaits (Package)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    nom = models.CharField(max_length=100, verbose_name='Nom du forfait')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    type_forfait = models.CharField(
        max_length=20,
        choices=TypeForfait.choices,
        default=TypeForfait.MIXTE,
        verbose_name='Type de forfait'
    )
    prix_mensuel = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix mensuel (FCFA)')
    quota_data_mo = models.IntegerField(null=True, blank=True, verbose_name='Quota Data (Mo)')
    quota_minutes = models.IntegerField(null=True, blank=True, verbose_name='Quota Minutes')
    quota_sms = models.IntegerField(null=True, blank=True, verbose_name='Quota SMS')
    description = models.TextField(blank=True, verbose_name='Description')
    est_actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')
    
    class Meta:
        db_table = 'packages'
        verbose_name = 'Forfait'
        verbose_name_plural = 'Forfaits'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"


class Service(models.Model):
    """Modèle pour les services optionnels"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    nom = models.CharField(max_length=100, verbose_name='Nom du service')
    code = models.CharField(max_length=20, unique=True, verbose_name='Code')
    type_service = models.CharField(
        max_length=20,
        choices=TypeService.choices,
        default=TypeService.OPTION,
        verbose_name='Type de service'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    est_actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')
    
    class Meta:
        db_table = 'services'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"


class TarifService(models.Model):
    """Modèle pour les options tarifaires des services"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='tarifs',
        verbose_name='Service'
    )
    nom_option = models.CharField(max_length=100, verbose_name='Nom de l\'option')
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix (FCFA)')
    duree_validite_heures = models.IntegerField(null=True, blank=True, verbose_name='Durée de validité (heures)')
    description = models.TextField(blank=True, verbose_name='Description')
    est_actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')
    
    class Meta:
        db_table = 'tarifs_services'
        verbose_name = 'Tarif Service'
        verbose_name_plural = 'Tarifs Services'
        ordering = ['service', 'nom_option']
    
    def __str__(self):
        return f"{self.service.nom} - {self.nom_option} ({self.prix} FCFA)"


class Invoice(models.Model):
    """Modèle pour les factures"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name='Entreprise'
    )
    # Renseignée uniquement pour une facture individuelle (SOM). Une facture
    # globale reste liée à l'entreprise sans être rattachée à une ligne.
    line = models.ForeignKey(
        Line,
        on_delete=models.SET_NULL,
        related_name='invoices',
        null=True,
        blank=True,
        verbose_name='Ligne concernée'
    )
    numero_facture = models.CharField(max_length=50, unique=True, verbose_name='Numéro de facture')
    periode_debut = models.DateField(verbose_name='Début de période')
    periode_fin = models.DateField(verbose_name='Fin de période')
    montant_ht = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Montant HT (FCFA)')
    montant_tva = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Montant TVA (FCFA)')
    montant_ttc = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Montant TTC (FCFA)')
    statut = models.CharField(
        max_length=20,
        choices=StatutFacture.choices,
        default=StatutFacture.BROUILLON,
        verbose_name='Statut'
    )
    date_emission = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'émission')
    date_echeance = models.DateField(verbose_name='Date d\'échéance')
    fichier_pdf = models.FileField(
        upload_to='factures/',
        null=True,
        blank=True,
        verbose_name='Fichier PDF'
    )
    commentaire = models.TextField(blank=True, verbose_name='Commentaire')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')
    
    class Meta:
        db_table = 'invoices'
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"{self.numero_facture} - {self.company.raison_sociale}"


class HistoriqueFacturation(models.Model):
    """Modèle pour l'historique des modifications de facturation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='historique',
        verbose_name='Facture'
    )
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actions_facturation',
        verbose_name='Utilisateur'
    )
    type_action = models.CharField(
        max_length=50,
        choices=TypeActionFacturation.choices,
        verbose_name='Type d\'action'
    )
    ancien_statut = models.CharField(max_length=20, blank=True, verbose_name='Ancien statut')
    nouveau_statut = models.CharField(max_length=20, verbose_name='Nouveau statut')
    commentaire = models.TextField(blank=True, verbose_name='Commentaire')
    date_action = models.DateTimeField(auto_now_add=True, verbose_name='Date de l\'action')
    
    class Meta:
        db_table = 'historique_facturation'
        verbose_name = 'Historique Facturation'
        verbose_name_plural = 'Historiques Facturation'
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.type_action} - {self.invoice.numero_facture} - {self.date_action.strftime('%d/%m/%Y %H:%M')}"


class Cycle(models.Model):
    """Modèle pour le cycle de service d'une ligne (table de liaison Line-Service)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    line = models.ForeignKey(
        Line,
        on_delete=models.CASCADE,
        related_name='cycles_services',
        verbose_name='Ligne'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='cycles_lignes',
        verbose_name='Service'
    )
    date_debut = models.DateTimeField(verbose_name='Date de début')
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name='Date de fin')
    est_actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')
    
    class Meta:
        db_table = 'cycles'
        verbose_name = 'Cycle Service'
        verbose_name_plural = 'Cycles Services'
        ordering = ['-date_debut']
        unique_together = [['line', 'service', 'date_debut']]
    
    def __str__(self):
        return f"{self.line.msisdn} - {self.service.nom} - {self.date_debut.strftime('%d/%m/%Y')}"


class Simulation(models.Model):
    """Modèle pour l'historique des simulations de facturation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='simulations',
        verbose_name='Utilisateur'
    )
    date_simulation = models.DateTimeField(auto_now_add=True, verbose_name='Date de simulation')
    montant_estime = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Montant estimé (FCFA)')
    services_selectionnes = models.JSONField(default=list, verbose_name='Services sélectionnés')
    resultat_detaille = models.JSONField(default=dict, verbose_name='Résultat détaillé')
    
    class Meta:
        db_table = 'simulations'
        verbose_name = 'Simulation'
        verbose_name_plural = 'Simulations'
        ordering = ['-date_simulation']
    
    def __str__(self):
        return f"Simulation {self.utilisateur.email} - {self.date_simulation.strftime('%d/%m/%Y %H:%M')}"


class Publication(models.Model):
    """Modèle pour l'historique des publications d'agent"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='ID')
    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='publications',
        verbose_name='Agent'
    )
    cycle_facturation = models.CharField(max_length=20, verbose_name='Cycle de facturation')
    periode_debut = models.DateField(verbose_name='Début de période')
    periode_fin = models.DateField(verbose_name='Fin de période')
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name='Date de publication')
    statut = models.CharField(
        max_length=20,
        choices=StatutFacture.choices,
        default=StatutFacture.PUBLIEE,
        verbose_name='Statut'
    )
    nombre_lignes_traitees = models.IntegerField(default=0, verbose_name='Nombre de lignes traitées')
    montant_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Montant total (FCFA)')
    fichier_pdf = models.FileField(
        upload_to='publications/',
        null=True,
        blank=True,
        verbose_name='Fichier PDF'
    )
    commentaire = models.TextField(blank=True, verbose_name='Commentaire')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')
    
    class Meta:
        db_table = 'publications'
        verbose_name = 'Publication'
        verbose_name_plural = 'Publications'
        ordering = ['-date_publication']
    
    def __str__(self):
        return f"Publication {self.cycle_facturation} - {self.date_publication.strftime('%d/%m/%Y')}"
