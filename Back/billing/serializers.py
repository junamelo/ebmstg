from rest_framework import serializers
from .models import (
    Company, Line, CategorieClient, CycleFacturation,
    Package, Service, TarifService, Invoice, HistoriqueFacturation,
    Cycle, Simulation, Publication
)

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'compte', 'raison_sociale', 'code_commercial', 'nom_commercial', 
                  'categorie', 'adresse', 'adresse2', 'statut', 'payeur', 'date_creation', 'date_modification']
        read_only_fields = ['id', 'date_creation', 'date_modification']

class LineSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.raison_sociale', read_only=True)
    
    class Meta:
        model = Line
        fields = ['id', 'company', 'company_name', 'msisdn', 'utilisateur', 'forfait', 
                  'cycle', 'option_blackberry', 'option_nolimit', 'est_incognito', 
                  'facture_detaillee', 'est_non_revenu', 'statut', 'employe', 
                  'date_creation', 'date_modification']
        read_only_fields = ['id', 'date_creation', 'date_modification']

# ==================== NOUVEAUX SERIALIZERS ====================

class PackageSerializer(serializers.ModelSerializer):
    """Serializer pour les forfaits"""
    class Meta:
        model = Package
        fields = [
            'id', 'nom', 'code', 'type_forfait', 'prix_mensuel',
            'quota_data_mo', 'quota_minutes', 'quota_sms',
            'description', 'est_actif', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer pour les services"""
    nombre_tarifs = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'nom', 'code', 'type_service', 'description',
            'est_actif', 'nombre_tarifs', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']
    
    def get_nombre_tarifs(self, obj):
        return obj.tarifs.count()


class TarifServiceSerializer(serializers.ModelSerializer):
    """Serializer pour les tarifs des services"""
    service_nom = serializers.CharField(source='service.nom', read_only=True)
    
    class Meta:
        model = TarifService
        fields = [
            'id', 'service', 'service_nom', 'nom_option', 'prix',
            'duree_validite_heures', 'description', 'est_actif',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer pour les factures"""
    company_name = serializers.CharField(source='company.raison_sociale', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'company', 'company_name', 'numero_facture',
            'periode_debut', 'periode_fin', 'montant_ht', 'montant_tva',
            'montant_ttc', 'statut', 'date_emission', 'date_echeance',
            'fichier_pdf', 'commentaire', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_emission', 'date_creation', 'date_modification']


class HistoriqueFacturationSerializer(serializers.ModelSerializer):
    """Serializer pour l'historique de facturation"""
    invoice_numero = serializers.CharField(source='invoice.numero_facture', read_only=True)
    utilisateur_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = HistoriqueFacturation
        fields = [
            'id', 'invoice', 'invoice_numero', 'utilisateur', 'utilisateur_nom',
            'type_action', 'ancien_statut', 'nouveau_statut',
            'commentaire', 'date_action'
        ]
        read_only_fields = ['id', 'date_action']
    
    def get_utilisateur_nom(self, obj):
        if obj.utilisateur:
            return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}"
        return "Système"


class CycleSerializer(serializers.ModelSerializer):
    """Serializer pour les cycles (liaison ligne-service)"""
    line_msisdn = serializers.CharField(source='line.msisdn', read_only=True)
    service_nom = serializers.CharField(source='service.nom', read_only=True)
    
    class Meta:
        model = Cycle
        fields = [
            'id', 'line', 'line_msisdn', 'service', 'service_nom',
            'date_debut', 'date_fin', 'est_actif',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']


class SimulationSerializer(serializers.ModelSerializer):
    """Serializer pour les simulations"""
    utilisateur_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Simulation
        fields = [
            'id', 'utilisateur', 'utilisateur_nom', 'date_simulation',
            'montant_estime', 'services_selectionnes', 'resultat_detaille'
        ]
        read_only_fields = ['id', 'date_simulation']
    
    def get_utilisateur_nom(self, obj):
        return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}"


class PublicationSerializer(serializers.ModelSerializer):
    """Serializer pour les publications"""
    agent_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'agent', 'agent_nom', 'cycle_facturation',
            'periode_debut', 'periode_fin', 'date_publication',
            'statut', 'nombre_lignes_traitees', 'montant_total',
            'fichier_pdf', 'commentaire', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_publication', 'date_creation', 'date_modification']
    
    def get_agent_nom(self, obj):
        return f"{obj.agent.first_name} {obj.agent.last_name}"
