"""
Extraits des modèles Django de Moov e-Factures.
Ce fichier est destiné uniquement aux captures du mémoire.
Les modèles complets restent dans Back/accounts/models.py et Back/billing/models.py.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


# ---------------------------------------------------------------------------
# Modèle central des acteurs de l'application.
# Les rôles permettent de distinguer les droits de chaque utilisateur.
# Table PostgreSQL générée : users
# ---------------------------------------------------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ("SUPER_ADMIN", "Super administrateur"),
        ("CHEF_FACTURATION", "Chef de facturation"),
        ("AGENT_FACTURATION", "Agent de facturation"),
        ("COMMERCIAL", "Commercial"),
        ("PAYEUR", "Payeur"),
        ("EMPLOYE", "Employé"),
    ]

    STATUS_CHOICES = [
        ("ACTIF", "Actif"),
        ("INACTIF", "Inactif"),
        ("SUSPENDU", "Suspendu"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    telephone = models.CharField(max_length=8, blank=True, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"


# ---------------------------------------------------------------------------
# Profil complémentaire de l'acteur Commercial.
# Il est relié à son compte utilisateur et aux contrats qu'il soumet.
# Table PostgreSQL générée : commerciaux
# ---------------------------------------------------------------------------
class Commercial(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profil_commercial",
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    matricule = models.CharField(max_length=30, unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    est_actif = models.BooleanField(default=True)

    class Meta:
        db_table = "commerciaux"


# ---------------------------------------------------------------------------
# Modèle représentant l'entreprise cliente et son contrat postpayé.
# Table PostgreSQL générée : companies
# ---------------------------------------------------------------------------
class Company(models.Model):
    compte = models.CharField(max_length=20, unique=True)
    raison_sociale = models.CharField(max_length=200)
    categorie = models.CharField(max_length=5)
    date_effet = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    statut_factures = models.CharField(max_length=20, default="EN_ATTENTE")
    mode_reglement = models.CharField(max_length=20, default="VIREMENT")
    est_resilie = models.BooleanField(default=False)

    commercial = models.ForeignKey(
        "Commercial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contrats",
    )
    payeur = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )

    class Meta:
        db_table = "companies"
        ordering = ["raison_sociale"]


# ---------------------------------------------------------------------------
# Modèle représentant une ligne mobile rattachée à une entreprise.
# Table PostgreSQL générée : lines
# ---------------------------------------------------------------------------
class Line(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    msisdn = models.CharField(max_length=15, unique=True)
    utilisateur = models.CharField(max_length=100, blank=True, null=True)
    forfait = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cycle = models.CharField(max_length=10, default="HYB")
    statut = models.CharField(max_length=20, default="ACTIF")
    employe = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lines",
    )

    class Meta:
        db_table = "lines"
        ordering = ["msisdn"]


# ---------------------------------------------------------------------------
# Modèle représentant une facture globale ou sommaire.
# Table PostgreSQL générée : invoices
# ---------------------------------------------------------------------------
class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    line = models.ForeignKey(
        Line,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    numero_facture = models.CharField(max_length=50, unique=True)
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    montant_ttc = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, default="BROUILLON")
    fichier_pdf = models.FileField(upload_to="factures/", null=True, blank=True)

    class Meta:
        db_table = "invoices"
        ordering = ["-date_emission"]


# ---------------------------------------------------------------------------
# Modèle assurant le suivi du découpage asynchrone d'un bloc PDF.
# Table PostgreSQL générée : traitements_pdf
# ---------------------------------------------------------------------------
class TraitementPDF(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="traitements_pdf",
    )
    fichier_source = models.FileField(upload_to="imports_pdf/%Y/%m/")
    type_facture = models.CharField(max_length=3, default="SOM")
    periode_debut = models.DateField(null=True, blank=True)
    periode_fin = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, default="EN_ATTENTE")
    progression = models.PositiveSmallIntegerField(default=0)
    resultat = models.JSONField(default=dict, blank=True)
    erreur = models.TextField(blank=True)

    class Meta:
        db_table = "traitements_pdf"
        ordering = ["-date_creation"]
