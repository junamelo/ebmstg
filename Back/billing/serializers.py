"""
Serializers pour l'application billing
"""
from rest_framework import serializers
from .models import (
    Company, Line, Package, Service, TarifService,
    CategorieClient, CycleFacturation, TypeForfait, TypeService
)
from .models import Commercial, AuditContrat, ModeReglement, StatutFacturation
from accounts.models import User


class CommercialSerializer(serializers.ModelSerializer):
    nombre_contrats = serializers.SerializerMethodField()

    class Meta:
        model = Commercial
        fields = [
            'id', 'nom', 'prenom', 'matricule', 'telephone', 'email',
            'est_actif', 'nombre_contrats', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']

    def get_nombre_contrats(self, obj):
        return obj.contrats.count()


class CommercialCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commercial
        fields = ['nom', 'prenom', 'matricule', 'telephone', 'email']

    def validate_matricule(self, value):
        if Commercial.objects.filter(matricule=value).exists():
            raise serializers.ValidationError("Ce matricule est déjà utilisé.")
        return value


class AuditContratSerializer(serializers.ModelSerializer):
    utilisateur_nom = serializers.SerializerMethodField()

    class Meta:
        model = AuditContrat
        fields = [
            'id', 'company', 'utilisateur', 'utilisateur_nom',
            'type_action', 'description', 'anciennes_valeurs', 'nouvelles_valeurs', 'date_action'
        ]
        read_only_fields = ['id', 'date_action']

    def get_utilisateur_nom(self, obj):
        if obj.utilisateur:
            return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}".strip() or obj.utilisateur.email
        return "Système"


class TarifServiceSerializer(serializers.ModelSerializer):
    """Serializer pour les tarifs de services"""
    service_name = serializers.CharField(source='service.nom', read_only=True)
    
    class Meta:
        model = TarifService
        fields = [
            'id', 'service', 'service_name', 'nom_option', 'prix',
            'duree_validite_heures', 'description', 'est_actif',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']


class TarifServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un tarif de service"""
    
    class Meta:
        model = TarifService
        fields = ['service', 'nom_option', 'prix', 'duree_validite_heures', 'description']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer pour les services"""
    tarifs = TarifServiceSerializer(many=True, read_only=True)
    nombre_tarifs = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'nom', 'code', 'type_service', 'description',
            'est_actif', 'tarifs', 'nombre_tarifs',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']
    
    def get_nombre_tarifs(self, obj):
        return obj.tarifs.filter(est_actif=True).count()


class ServiceListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des services"""
    nombre_tarifs = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'nom', 'code', 'type_service', 'est_actif',
            'nombre_tarifs', 'date_creation'
        ]
    
    def get_nombre_tarifs(self, obj):
        return obj.tarifs.filter(est_actif=True).count()


class ServiceCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un service avec ses tarifs"""
    tarifs = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="Liste des tarifs à créer avec le service"
    )
    
    class Meta:
        model = Service
        fields = ['nom', 'code', 'type_service', 'description', 'tarifs']
    
    def validate_code(self, value):
        """Valider l'unicité du code"""
        if Service.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ce code de service existe déjà")
        return value
    
    def create(self, validated_data):
        tarifs_data = validated_data.pop('tarifs', [])
        service = Service.objects.create(**validated_data)
        
        # Créer les tarifs associés
        for tarif_data in tarifs_data:
            TarifService.objects.create(service=service, **tarif_data)
        
        return service


class PackageSerializer(serializers.ModelSerializer):
    """Serializer pour les forfaits"""
    
    class Meta:
        model = Package
        fields = [
            'id', 'nom', 'code', 'type_forfait', 'prix_mensuel',
            'quota_data_mo', 'quota_minutes', 'quota_sms',
            'description', 'est_actif',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']


class PackageListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des forfaits"""
    
    class Meta:
        model = Package
        fields = [
            'id', 'nom', 'code', 'type_forfait', 'prix_mensuel',
            'est_actif', 'date_creation'
        ]


class PackageCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un forfait"""
    
    class Meta:
        model = Package
        fields = [
            'nom', 'code', 'type_forfait', 'prix_mensuel',
            'quota_data_mo', 'quota_minutes', 'quota_sms', 'description'
        ]
    
    def validate_code(self, value):
        """Valider l'unicité du code"""
        if Package.objects.filter(code=value).exists():
            raise serializers.ValidationError("Ce code de forfait existe déjà")
        return value


class LineSerializer(serializers.ModelSerializer):
    """Serializer pour les lignes téléphoniques"""
    employe_info = serializers.SerializerMethodField()
    company_name = serializers.CharField(source='company.raison_sociale', read_only=True)
    
    class Meta:
        model = Line
        fields = [
            'id', 'company', 'company_name', 'msisdn', 'utilisateur', 
            'forfait', 'cycle', 'option_blackberry', 'option_nolimit',
            'est_incognito', 'facture_detaillee', 'est_non_revenu',
            'est_roaming', 'est_internet', 'est_international',
            'statut', 'employe', 'employe_info',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']
    
    def get_employe_info(self, obj):
        if obj.employe:
            return {
                'id': obj.employe.id,
                'nom': f"{obj.employe.first_name} {obj.employe.last_name}",
                'email': obj.employe.email
            }
        return None


class LineListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des lignes"""
    company_name = serializers.CharField(source='company.raison_sociale', read_only=True)
    
    class Meta:
        model = Line
        fields = [
            'id', 'company', 'company_name', 'msisdn', 'utilisateur',
            'forfait', 'cycle', 'statut', 'date_creation'
        ]


class CompanySerializer(serializers.ModelSerializer):
    """Serializer pour les entreprises/contrats"""
    payeur_info = serializers.SerializerMethodField()
    commercial_info = serializers.SerializerMethodField()
    lines = LineListSerializer(many=True, read_only=True)
    nombre_lignes = serializers.SerializerMethodField()
    nombre_lignes_actives = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'compte', 'raison_sociale', 'code_commercial', 'nom_commercial',
            'categorie', 'adresse', 'adresse2', 'statut', 'payeur', 'payeur_info',
            'date_effet', 'est_exonere', 'facture_detaillee_defaut', 'option_nolimit_defaut',
            'option_blackberry_defaut', 'est_incognito_defaut', 'roaming_defaut', 'internet_defaut',
            'international_defaut', 'est_non_revenu_defaut',
            'lines', 'nombre_lignes', 'nombre_lignes_actives',
            'date_creation', 'date_modification',
            'commercial', 'commercial_info', 'statut_factures', 'email_facturation',
            'adresse_ligne2', 'date_fin', 'observation', 'type_revenu', 'motif_exoneration',
            'mode_reglement', 'est_resilie', 'date_resiliation', 'motif_resiliation', 'observation_resiliation',
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']
    
    def get_payeur_info(self, obj):
        if obj.payeur:
            return {
                'id': obj.payeur.id,
                'nom': f"{obj.payeur.first_name} {obj.payeur.last_name}",
                'email': obj.payeur.email,
                'username': obj.payeur.username
            }
        return None

    def get_commercial_info(self, obj):
        if obj.commercial:
            return {
                'id': obj.commercial.id,
                'nom': obj.commercial.nom,
                'prenom': obj.commercial.prenom,
                'matricule': obj.commercial.matricule,
                'telephone': obj.commercial.telephone,
            }
        return None
    
    def get_nombre_lignes(self, obj):
        return obj.lines.count()
    
    def get_nombre_lignes_actives(self, obj):
        return obj.lines.filter(statut='ACTIF').count()


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des entreprises"""
    payeur_name = serializers.SerializerMethodField()
    commercial_info = serializers.SerializerMethodField()
    nombre_lignes = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'compte', 'raison_sociale', 'categorie', 'statut',
            'payeur', 'payeur_name', 'commercial_info', 'nombre_lignes', 'date_creation',
            'statut_factures', 'est_resilie', 'mode_reglement',
        ]
    
    def get_payeur_name(self, obj):
        if obj.payeur:
            return f"{obj.payeur.first_name} {obj.payeur.last_name}"
        return None

    def get_commercial_info(self, obj):
        if obj.commercial:
            return {
                'id': obj.commercial.id,
                'nom': obj.commercial.nom,
                'prenom': obj.commercial.prenom,
                'matricule': obj.commercial.matricule,
                'telephone': obj.commercial.telephone,
            }
        return None
    
    def get_nombre_lignes(self, obj):
        return obj.lines.count()


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'entreprise avec lignes"""
    lignes = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="Liste des lignes à créer avec le contrat"
    )
    
    class Meta:
        model = Company
        fields = [
            'compte', 'raison_sociale', 'code_commercial', 'nom_commercial',
            'categorie', 'adresse', 'adresse2', 'payeur', 'lignes',
            'date_effet', 'est_exonere', 'facture_detaillee_defaut', 'option_nolimit_defaut',
            'option_blackberry_defaut', 'est_incognito_defaut', 'roaming_defaut', 'internet_defaut',
            'international_defaut', 'est_non_revenu_defaut',
            'commercial', 'statut_factures', 'email_facturation', 'adresse_ligne2', 'date_fin',
            'observation', 'type_revenu', 'motif_exoneration', 'mode_reglement',
            'est_resilie', 'date_resiliation', 'motif_resiliation', 'observation_resiliation',
        ]
    
    def validate_compte(self, value):
        """Valider le numéro de compte"""
        if Company.objects.filter(compte=value).exists():
            raise serializers.ValidationError("Ce numéro de compte existe déjà")
        return value
    
    def validate_payeur(self, value):
        """Valider que le payeur a le bon rôle"""
        if value and value.role != 'PAYEUR':
            raise serializers.ValidationError("L'utilisateur doit avoir le rôle PAYEUR")
        return value

    def validate(self, data):
        if data.get('est_resilie'):
            if not data.get('date_resiliation'):
                raise serializers.ValidationError({'date_resiliation': 'Obligatoire si le contrat est résilié.'})
            if not data.get('motif_resiliation'):
                raise serializers.ValidationError({'motif_resiliation': 'Obligatoire si le contrat est résilié.'})
            if data.get('date_effet') and data.get('date_resiliation') < data.get('date_effet'):
                raise serializers.ValidationError({'date_resiliation': "La date de résiliation ne peut pas être antérieure à la date d'effet."})
        return data
    
    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes', [])
        company = Company.objects.create(**validated_data)
        
        # Créer les lignes associées
        for ligne_data in lignes_data:
            Line.objects.create(company=company, **ligne_data)
        
        return company


class LineCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de ligne"""
    
    class Meta:
        model = Line
        fields = [
            'company', 'msisdn', 'utilisateur', 'forfait', 'cycle',
            'option_blackberry', 'option_nolimit', 'est_incognito',
            'facture_detaillee', 'est_non_revenu', 'employe'
            , 'est_roaming', 'est_internet', 'est_international'
        ]
    
    def validate_msisdn(self, value):
        """Valider l'unicité du MSISDN"""
        if Line.objects.filter(msisdn=value).exists():
            raise serializers.ValidationError("Ce numéro de ligne existe déjà")
        return value
    
    def validate_employe(self, value):
        """Valider que l'employé a le bon rôle"""
        if value and value.role != 'EMPLOYE':
            raise serializers.ValidationError("L'utilisateur doit avoir le rôle EMPLOYE")
        return value

    def create(self, validated_data):
        company = validated_data['company']
        defaults = {
            'option_blackberry': company.option_blackberry_defaut,
            'option_nolimit': company.option_nolimit_defaut,
            'est_incognito': company.est_incognito_defaut,
            'facture_detaillee': company.facture_detaillee_defaut,
            'est_non_revenu': company.est_non_revenu_defaut,
            'est_roaming': company.roaming_defaut,
            'est_internet': company.internet_defaut,
            'est_international': company.international_defaut,
        }
        for key, value in defaults.items():
            validated_data.setdefault(key, value)
        return super().create(validated_data)


class CompanyStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques d'un contrat"""
    company_id = serializers.IntegerField()
    raison_sociale = serializers.CharField()
    nombre_lignes_total = serializers.IntegerField()
    nombre_lignes_actives = serializers.IntegerField()
    nombre_lignes_suspendues = serializers.IntegerField()
    nombre_lignes_inactives = serializers.IntegerField()
    lignes_par_cycle = serializers.DictField()
    montant_forfaits_total = serializers.DecimalField(max_digits=15, decimal_places=2)


class ChangeStatutSerializer(serializers.Serializer):
    """Serializer pour changer le statut d'une entreprise ou ligne"""
    nouveau_statut = serializers.ChoiceField(choices=['ACTIF', 'INACTIF', 'SUSPENDU'])
    raison = serializers.CharField(required=True, max_length=500)


# ==================== SERIALIZERS PHASE 4 : FACTURATION ====================

from .models import Invoice, HistoriqueFacturation, Publication


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer pour les factures"""
    company_name = serializers.CharField(source='company.raison_sociale', read_only=True)
    company_compte = serializers.CharField(source='company.compte', read_only=True)
    line_msisdn = serializers.CharField(source='line.msisdn', read_only=True)
    employe_info = serializers.SerializerMethodField()
    historique = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'company', 'company_name', 'company_compte', 'line', 'line_msisdn', 'employe_info',
            'numero_facture', 'periode_debut', 'periode_fin',
            'montant_ht', 'montant_tva', 'montant_ttc',
            'statut', 'date_emission', 'date_echeance',
            'fichier_pdf', 'commentaire', 'historique',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_emission', 'date_creation', 'date_modification']
    
    def get_historique(self, obj):
        """Retourner les 5 dernières actions sur cette facture"""
        historique = obj.historique.all()[:5]
        return HistoriqueFacturationSerializer(historique, many=True).data

    def get_employe_info(self, obj):
        if obj.line and obj.line.employe:
            return {
                'id': obj.line.employe.id,
                'nom': f"{obj.line.employe.first_name} {obj.line.employe.last_name}".strip(),
                'email': obj.line.employe.email,
            }
        return None


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des factures"""
    company_name = serializers.CharField(source='company.raison_sociale', read_only=True)
    company_compte = serializers.CharField(source='company.compte', read_only=True)
    line_msisdn = serializers.CharField(source='line.msisdn', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'company', 'company_name', 'company_compte', 'line', 'line_msisdn',
            'numero_facture', 'periode_debut', 'periode_fin',
            'montant_ttc', 'statut', 'date_emission', 'date_echeance'
        ]


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une facture"""
    
    class Meta:
        model = Invoice
        fields = [
            'company', 'line', 'numero_facture', 'periode_debut', 'periode_fin',
            'montant_ht', 'montant_tva', 'montant_ttc',
            'date_echeance', 'commentaire'
        ]
    
    def validate_numero_facture(self, value):
        """Valider l'unicité du numéro de facture"""
        if Invoice.objects.filter(numero_facture=value).exists():
            raise serializers.ValidationError("Ce numéro de facture existe déjà")
        return value
    
    def validate(self, data):
        """Valider les périodes"""
        if data['periode_debut'] >= data['periode_fin']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin"
            )
        line = data.get('line')
        if line and line.company_id != data['company'].id:
            raise serializers.ValidationError("La ligne doit appartenir à l'entreprise sélectionnée")
        return data


class GenerateInvoiceSerializer(serializers.Serializer):
    """Serializer pour la génération de factures"""
    cycle = serializers.ChoiceField(
        choices=['HYB', 'OP'],
        required=True,
        help_text="Cycle de facturation (HYB ou OP)"
    )
    periode_debut = serializers.DateField(required=True)
    periode_fin = serializers.DateField(required=True)
    company_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="IDs des entreprises à facturer (vide = toutes)"
    )
    
    def validate(self, data):
        """Valider les périodes"""
        if data['periode_debut'] >= data['periode_fin']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin"
            )
        return data


class CalculLineInvoiceSerializer(serializers.Serializer):
    """Serializer pour calculer la facture d'une ligne"""
    line_id = serializers.IntegerField(required=True)
    periode_debut = serializers.DateField(required=True)
    periode_fin = serializers.DateField(required=True)
    
    # Consommations
    conso_data_mo = serializers.IntegerField(default=0, min_value=0)
    conso_duree_secondes = serializers.IntegerField(default=0, min_value=0)
    conso_sms = serializers.IntegerField(default=0, min_value=0)
    
    # Services supplémentaires (optionnel)
    services_supplementaires = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Liste des services avec nom et prix"
    )


class ValiderInvoiceSerializer(serializers.Serializer):
    """Serializer pour valider une facture"""
    commentaire = serializers.CharField(required=False, allow_blank=True)


class AnnulerInvoiceSerializer(serializers.Serializer):
    """Serializer pour annuler une facture"""
    raison = serializers.CharField(required=True, max_length=500)


class HistoriqueFacturationSerializer(serializers.ModelSerializer):
    """Serializer pour l'historique de facturation"""
    utilisateur_name = serializers.SerializerMethodField()
    invoice_numero = serializers.CharField(source='invoice.numero_facture', read_only=True)
    
    class Meta:
        model = HistoriqueFacturation
        fields = [
            'id', 'invoice', 'invoice_numero', 'utilisateur', 'utilisateur_name',
            'type_action', 'ancien_statut', 'nouveau_statut',
            'commentaire', 'date_action'
        ]
        read_only_fields = ['id', 'date_action']
    
    def get_utilisateur_name(self, obj):
        if obj.utilisateur:
            return f"{obj.utilisateur.first_name} {obj.utilisateur.last_name}"
        return "Système"


class PublicationSerializer(serializers.ModelSerializer):
    """Serializer pour les publications"""
    agent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'agent', 'agent_name', 'cycle_facturation',
            'periode_debut', 'periode_fin', 'date_publication',
            'statut', 'nombre_lignes_traitees', 'montant_total',
            'fichier_pdf', 'commentaire',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'date_publication', 'date_creation', 'date_modification']
    
    def get_agent_name(self, obj):
        return f"{obj.agent.first_name} {obj.agent.last_name}"


class PublicationListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des publications"""
    agent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'agent', 'agent_name', 'cycle_facturation',
            'periode_debut', 'periode_fin', 'date_publication',
            'statut', 'nombre_lignes_traitees', 'montant_total'
        ]
    
    def get_agent_name(self, obj):
        return f"{obj.agent.first_name} {obj.agent.last_name}"


class PublicationCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une publication"""
    
    class Meta:
        model = Publication
        fields = [
            'cycle_facturation', 'periode_debut', 'periode_fin', 'commentaire'
        ]
    
    def validate(self, data):
        """Valider les périodes"""
        if data['periode_debut'] >= data['periode_fin']:
            raise serializers.ValidationError(
                "La date de début doit être antérieure à la date de fin"
            )
        return data


class PublishInvoicesSerializer(serializers.Serializer):
    """Serializer pour publier des factures en masse"""
    invoice_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        help_text="Liste des IDs de factures à publier"
    )
    commentaire = serializers.CharField(required=False, allow_blank=True)


class UploadPDFSerializer(serializers.Serializer):
    """Serializer pour uploader un PDF"""
    fichier = serializers.FileField(required=True)
    invoice_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_fichier(self, value):
        """Valider que c'est bien un PDF"""
        # Vérifier l'extension
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Le fichier doit avoir l'extension .pdf")
        
        # Vérifier la taille (max 50 Mo)
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Le fichier ne doit pas dépasser 50 Mo (taille: {value.size / (1024 * 1024):.1f} Mo)"
            )
        
        # Vérifier que ce n'est pas un fichier vide
        if value.size == 0:
            raise serializers.ValidationError("Le fichier PDF est vide")
        
        # Vérifier le header PDF basique
        value.seek(0)
        header = value.read(8)
        value.seek(0)  # Remettre au début
        
        if not header.startswith(b'%PDF'):
            raise serializers.ValidationError(
                "Le fichier ne semble pas être un PDF valide (header manquant)"
            )
        
        return value


class BulkPDFUploadSerializer(serializers.Serializer):
    """Serializer pour upload en masse d'un gros PDF"""
    fichier = serializers.FileField(required=True)
    auto_match = serializers.BooleanField(
        default=True,
        help_text="Matcher automatiquement les PDF découpés aux factures"
    )
    type_facture = serializers.ChoiceField(
        choices=['SOM', 'GLO'],
        default='SOM',
        help_text="Format du PDF : SOM (individuel) ou GLO (global)"
    )
    cycle = serializers.ChoiceField(
        choices=['HYB', 'OP'],
        required=False,
        help_text="Filtrer les factures par cycle"
    )
    periode_debut = serializers.DateField(required=False)
    periode_fin = serializers.DateField(required=False)
    
    def validate_fichier(self, value):
        """Valider que c'est bien un PDF"""
        # Vérifier l'extension
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Le fichier doit avoir l'extension .pdf")
        
        # Vérifier la taille (max 50 Mo)
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Le fichier ne doit pas dépasser 50 Mo (taille: {value.size / (1024 * 1024):.1f} Mo)"
            )
        
        # Vérifier que ce n'est pas un fichier vide
        if value.size == 0:
            raise serializers.ValidationError("Le fichier PDF est vide")
        
        # Vérifier le header PDF basique
        value.seek(0)
        header = value.read(8)
        value.seek(0)  # Remettre au début
        
        if not header.startswith(b'%PDF'):
            raise serializers.ValidationError(
                "Le fichier ne semble pas être un PDF valide (header manquant)"
            )
        
        return value


class InvoiceStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques des factures"""
    total_factures = serializers.IntegerField()
    factures_par_statut = serializers.DictField()
    montant_total_ttc = serializers.DecimalField(max_digits=15, decimal_places=2)
    montant_par_statut = serializers.DictField()
