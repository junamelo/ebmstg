from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from decimal import Decimal
import uuid

class ModeReglement(models.TextChoices):
    CHEQUE = 'CHEQUE', 'Chèque'
    VIREMENT = 'VIREMENT', 'Virement'
    ESPECES = 'ESPECES', 'Espèces'

class StatutFacturation(models.TextChoices):
    ACTIF = 'ACTIF', 'Actif'
    SUSPENDU = 'SUSPENDU', 'Suspendu'
    CLOS = 'CLOS', 'Clos'
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'

class TypeAction(models.TextChoices):
    CREATION = 'CREATION', 'Création du contrat'
    MODIFICATION = 'MODIFICATION', 'Modification'
    CHANGEMENT_STATUT = 'CHANGEMENT_STATUT', 'Changement de statut de facturation'
    CHANGEMENT_COMMERCIAL = 'CHANGEMENT_COMMERCIAL', 'Changement de commercial'
    CHANGEMENT_SERVICES = 'CHANGEMENT_SERVICES', 'Changement des services par défaut'
    RESILIATION = 'RESILIATION', 'Résiliation'
    MODIFICATION_RESILIATION = 'MODIFICATION_RESILIATION', 'Modification résiliation'
    AJOUT_LIGNE = 'AJOUT_LIGNE', 'Ajout de ligne'
    MODIFICATION_LIGNE = 'MODIFICATION_LIGNE', 'Modification services ligne'

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

class Commercial(models.Model):
    """Représente un commercial Moov Africa"""
    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    matricule = models.CharField(max_length=30, unique=True, verbose_name='Matricule / Code commercial')
    telephone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    email = models.EmailField(blank=True, verbose_name='Email')
    est_actif = models.BooleanField(default=True, verbose_name='Actif')
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date Création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date Modification')

    class Meta:
        db_table = 'commerciaux'
        verbose_name = 'Commercial'
        verbose_name_plural = 'Commerciaux'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.matricule})"


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
    date_effet = models.DateField(null=True, blank=True, verbose_name='Date effet')
    est_exonere = models.BooleanField(default=False, verbose_name='Exonéré')
    # Services par défaut du contrat, hérités par les nouvelles lignes.
    facture_detaillee_defaut = models.BooleanField(default=False)
    option_nolimit_defaut = models.CharField(max_length=20, blank=True, default='')
    option_blackberry_defaut = models.CharField(max_length=20, blank=True, default='')
    est_incognito_defaut = models.BooleanField(default=False)
    roaming_defaut = models.BooleanField(default=False)
    internet_defaut = models.BooleanField(default=False)
    international_defaut = models.BooleanField(default=False)
    est_non_revenu_defaut = models.BooleanField(default=False)
    commercial = models.ForeignKey(
        'Commercial',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contrats',
        verbose_name='Commercial'
    )
    statut_factures = models.CharField(
        max_length=20,
        choices=StatutFacturation.choices,
        default=StatutFacturation.EN_ATTENTE,
        verbose_name='Statut de facturation'
    )
    email_facturation = models.EmailField(blank=True, verbose_name='Email de facturation')
    adresse_ligne2 = models.TextField(blank=True, verbose_name='Adresse ligne 2')
    date_fin = models.DateField(null=True, blank=True, verbose_name='Date de fin')
    observation = models.TextField(blank=True, verbose_name='Observation')
    type_revenu = models.CharField(max_length=50, blank=True, verbose_name='Type de revenu')
    motif_exoneration = models.TextField(blank=True, verbose_name="Motif d'exonération")
    mode_reglement = models.CharField(
        max_length=20,
        choices=ModeReglement.choices,
        default=ModeReglement.VIREMENT,
        verbose_name='Mode de règlement'
    )
    est_resilie = models.BooleanField(default=False, verbose_name='Résilié')
    date_resiliation = models.DateField(null=True, blank=True, verbose_name='Date de résiliation')
    motif_resiliation = models.TextField(blank=True, verbose_name='Motif de résiliation')
    observation_resiliation = models.TextField(blank=True, verbose_name='Observation résiliation')
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
    forfait = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Forfait (FCFA)'
    )
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
    est_roaming = models.BooleanField(default=False, verbose_name='Roaming')
    est_internet = models.BooleanField(default=False, verbose_name='Internet')
    est_international = models.BooleanField(default=False, verbose_name='International')
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


class AuditContrat(models.Model):
    """Journalisation de toutes les actions sur un contrat"""
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='audit_log',
        verbose_name='Contrat'
    )
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audits_contrats',
        verbose_name='Utilisateur'
    )
    type_action = models.CharField(
        max_length=50,
        choices=TypeAction.choices,
        verbose_name="Type d'action"
    )
    description = models.TextField(verbose_name='Description')
    anciennes_valeurs = models.JSONField(default=dict, blank=True, verbose_name='Anciennes valeurs')
    nouvelles_valeurs = models.JSONField(default=dict, blank=True, verbose_name='Nouvelles valeurs')
    date_action = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'action")

    class Meta:
        db_table = 'audit_contrats'
        verbose_name = 'Audit Contrat'
        verbose_name_plural = 'Audits Contrats'
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.type_action} — {self.company} — {self.date_action.strftime('%d/%m/%Y %H:%M')}"


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
    prix_mensuel = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Prix mensuel (FCFA)'
    )
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
    prix = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Prix (FCFA)'
    )
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
    numero_facture_pdf = models.CharField(max_length=100, blank=True, default='', verbose_name='Numéro facture PDF')
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
    date_emission_pdf = models.DateField(null=True, blank=True, verbose_name='Date édition PDF')
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


class NotificationFacture(models.Model):
    """Trace les notifications de disponibilité envoyées pour une facture."""
    class Canal(models.TextChoices):
        EMAIL = 'EMAIL', 'E-mail'
        SMS = 'SMS', 'SMS'

    class Statut(models.TextChoices):
        ENVOYEE = 'ENVOYEE', 'Envoyée'
        ECHEC = 'ECHEC', 'Échec'
        NON_CONFIGUREE = 'NON_CONFIGUREE', 'Service non configuré'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='notifications')
    canal = models.CharField(max_length=10, choices=Canal.choices)
    destinataire = models.CharField(max_length=254)
    statut = models.CharField(max_length=20, choices=Statut.choices)
    detail = models.TextField(blank=True)
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_factures'
        ordering = ['-date_envoi']


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
