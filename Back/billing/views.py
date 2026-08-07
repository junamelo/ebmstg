"""
Views pour l'application billing
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Company, Line, Package, Service, TarifService, Commercial, AuditContrat, Simulation
from .serializers import CommercialSerializer, CommercialCreateSerializer, AuditContratSerializer
from .serializers import (
    CompanySerializer, CompanyListSerializer, CompanyCreateSerializer,
    LineSerializer, LineListSerializer, LineCreateSerializer,
    CompanyStatsSerializer, ChangeStatutSerializer,
    PackageSerializer, PackageListSerializer, PackageCreateSerializer,
    ServiceSerializer, ServiceListSerializer, ServiceCreateSerializer,
    TarifServiceSerializer, TarifServiceCreateSerializer,
    InvoiceSerializer, InvoiceListSerializer, InvoiceCreateSerializer,
    GenerateInvoiceSerializer, CalculLineInvoiceSerializer,
    ValiderInvoiceSerializer, AnnulerInvoiceSerializer,
    HistoriqueFacturationSerializer, PublicationSerializer,
    PublicationListSerializer, PublicationCreateSerializer,
    PublishInvoicesSerializer, UploadPDFSerializer, BulkPDFUploadSerializer,
    InvoiceStatsSerializer,
    SimulationSerializer, SimulationCreateSerializer
)
from accounts.permissions import (
    IsAgentFacturation, CanManageUser, CanManageTarifs, CanManageServices,
    CanPublishInvoices, CanUploadPDF, CanValidateInvoices, CanGenerateInvoices
)


class CompanyViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des entreprises/contrats
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categorie', 'statut', 'payeur']
    search_fields = ['compte', 'raison_sociale', 'nom_commercial']
    ordering_fields = ['date_creation', 'raison_sociale', 'compte']
    ordering = ['-date_creation']
    
    def get_permissions(self):
        """Permissions selon l'action et le rôle"""
        # Lecture : Payeur peut lire ses entreprises (selon matrice d'accès)
        if self.action in ['list', 'retrieve', 'stats', 'lignes']:
            return [IsAuthenticated()]
        # Création/modification : Agents uniquement
        return [IsAuthenticated(), IsAgentFacturation()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        elif self.action == 'create':
            return CompanyCreateSerializer
        return CompanySerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle de l'utilisateur"""
        user = self.request.user
        
        # Super admin et chef voient tout
        if user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION']:
            return Company.objects.all().prefetch_related('lines')
        
        # Agent voit tout (peut gérer les contrats)
        if user.role == 'AGENT_FACTURATION':
            return Company.objects.all().prefetch_related('lines')
        
        # Payeur voit seulement ses entreprises
        if user.role == 'PAYEUR':
            return Company.objects.filter(payeur=user).prefetch_related('lines')
        
        # Employé ne voit rien (API contrats pas pour lui)
        return Company.objects.none()
    
    @extend_schema(
        summary="Créer un contrat",
        description="Créer un nouveau contrat avec possibilité d'ajouter des lignes",
        request=CompanyCreateSerializer,
        responses={201: CompanySerializer}
    )
    def create(self, request, *args, **kwargs):
        """Créer un contrat avec lignes optionnelles"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        AuditContrat.objects.create(
            company=company,
            utilisateur=request.user,
            type_action='CREATION',
            description=f"Contrat {company.compte} créé pour {company.raison_sociale}",
            nouvelles_valeurs={'compte': company.compte, 'raison_sociale': company.raison_sociale}
        )
        # Retourner le détail complet
        output_serializer = CompanySerializer(company)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Obtenir les statistiques d'un contrat",
        description="Statistiques détaillées : nombre de lignes, cycles, montants",
        responses={200: CompanyStatsSerializer}
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Statistiques d'un contrat"""
        company = self.get_object()
        
        # Compter les lignes par statut
        lines = company.lines.all()
        stats = {
            'company_id': company.id,
            'raison_sociale': company.raison_sociale,
            'nombre_lignes_total': lines.count(),
            'nombre_lignes_actives': lines.filter(statut='ACTIF').count(),
            'nombre_lignes_suspendues': lines.filter(statut='SUSPENDU').count(),
            'nombre_lignes_inactives': lines.filter(statut='INACTIF').count(),
            'lignes_par_cycle': {
                'HYB': lines.filter(cycle='HYB').count(),
                'OP': lines.filter(cycle='OP').count()
            },
            'montant_forfaits_total': lines.aggregate(total=Sum('forfait'))['total'] or 0
        }
        
        return Response(stats)
    
    @extend_schema(
        summary="Changer le statut d'un contrat",
        description="Activer, désactiver ou suspendre un contrat",
        request=ChangeStatutSerializer
    )
    @action(detail=True, methods=['post'])
    def change_statut(self, request, pk=None):
        """Changer le statut d'un contrat"""
        company = self.get_object()
        serializer = ChangeStatutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ancien_statut = company.statut
        nouveau_statut = serializer.validated_data['nouveau_statut']
        raison = serializer.validated_data['raison']
        
        company.statut = nouveau_statut
        company.save()
        
        # TODO: Logger le changement dans une table d'historique
        
        return Response({
            'message': f'Statut changé de {ancien_statut} à {nouveau_statut}',
            'company': CompanySerializer(company).data
        })
    
    @extend_schema(
        summary="Liste des lignes d'un contrat",
        description="Toutes les lignes téléphoniques associées au contrat",
        responses={200: LineListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def lignes(self, request, pk=None):
        """Liste des lignes d'un contrat"""
        company = self.get_object()
        lines = company.lines.all()
        
        # Filtres optionnels
        statut = request.query_params.get('statut')
        if statut:
            lines = lines.filter(statut=statut)
        
        cycle = request.query_params.get('cycle')
        if cycle:
            lines = lines.filter(cycle=cycle)
        
        serializer = LineListSerializer(lines, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        company = self.get_object()
        anciennes_valeurs = {
            'statut_factures': company.statut_factures,
            'commercial': company.commercial_id,
            'mode_reglement': company.mode_reglement,
        }
        response = super().update(request, *args, **kwargs)
        company.refresh_from_db()
        nouvelles_valeurs = {
            'statut_factures': company.statut_factures,
            'commercial': company.commercial_id,
            'mode_reglement': company.mode_reglement,
        }
        AuditContrat.objects.create(
            company=company,
            utilisateur=request.user,
            type_action='MODIFICATION',
            description="Informations du contrat modifiées",
            anciennes_valeurs=anciennes_valeurs,
            nouvelles_valeurs=nouvelles_valeurs
        )
        return response

    @action(detail=True, methods=['post'])
    def resilier(self, request, pk=None):
        """Résilier un contrat"""
        company = self.get_object()
        if company.est_resilie:
            return Response({'error': 'Ce contrat est déjà résilié.'}, status=status.HTTP_400_BAD_REQUEST)
        date_resiliation = request.data.get('date_resiliation')
        motif_resiliation = request.data.get('motif_resiliation')
        observation_resiliation = request.data.get('observation_resiliation', '')
        if not date_resiliation:
            return Response({'error': 'date_resiliation est obligatoire.'}, status=status.HTTP_400_BAD_REQUEST)
        if not motif_resiliation:
            return Response({'error': 'motif_resiliation est obligatoire.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            import datetime
            dr = datetime.date.fromisoformat(date_resiliation)
        except Exception:
            return Response({'error': 'Format de date invalide (YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)
        if company.date_effet and dr < company.date_effet:
            return Response({'error': "La date de résiliation ne peut pas être antérieure à la date d'effet."}, status=status.HTTP_400_BAD_REQUEST)
        anciennes_valeurs = {'est_resilie': False, 'statut_factures': company.statut_factures}
        company.est_resilie = True
        company.date_resiliation = date_resiliation
        company.motif_resiliation = motif_resiliation
        company.observation_resiliation = observation_resiliation
        company.statut_factures = 'CLOS'
        company.save()
        AuditContrat.objects.create(
            company=company,
            utilisateur=request.user,
            type_action='RESILIATION',
            description=f"Contrat résilié. Motif : {motif_resiliation}",
            anciennes_valeurs=anciennes_valeurs,
            nouvelles_valeurs={'est_resilie': True, 'date_resiliation': date_resiliation, 'motif_resiliation': motif_resiliation}
        )
        return Response(CompanySerializer(company).data)

    @action(detail=True, methods=['get'])
    def historique(self, request, pk=None):
        """Historique des actions sur un contrat"""
        company = self.get_object()
        audits = company.audit_log.all()
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        result = paginator.paginate_queryset(audits, request)
        serializer = AuditContratSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)


class LineViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des lignes téléphoniques
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'statut', 'cycle', 'employe']
    search_fields = ['msisdn', 'utilisateur']
    ordering_fields = ['date_creation', 'msisdn', 'utilisateur']
    ordering = ['-date_creation']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LineListSerializer
        elif self.action == 'create':
            return LineCreateSerializer
        return LineSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle de l'utilisateur"""
        user = self.request.user
        
        # Super admin, chef et agent voient tout
        if user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']:
            return Line.objects.all().select_related('company', 'employe')
        
        # Payeur voit les lignes de ses entreprises
        if user.role == 'PAYEUR':
            return Line.objects.filter(
                company__payeur=user
            ).select_related('company', 'employe')
        
        # Employé voit seulement sa ligne
        if user.role == 'EMPLOYE':
            return Line.objects.filter(employe=user).select_related('company')
        
        return Line.objects.none()
    
    @extend_schema(
        summary="Créer une ligne",
        description="Ajouter une nouvelle ligne téléphonique à un contrat",
        request=LineCreateSerializer,
        responses={201: LineSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Créer une ligne"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        line = serializer.save()
        # Journaliser dans l'audit du contrat
        AuditContrat.objects.create(
            company=line.company,
            utilisateur=request.user,
            type_action='AJOUT_LIGNE',
            description=f"Ligne {line.msisdn} ajoutée",
            nouvelles_valeurs={'msisdn': line.msisdn, 'cycle': line.cycle}
        )
        output_serializer = LineSerializer(line)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Assigner un employé à une ligne",
        description="Associer un compte employé à une ligne téléphonique",
        parameters=[
            OpenApiParameter(name='employe_id', type=int, description='ID du compte employé')
        ]
    )
    @action(detail=True, methods=['post'])
    def assigner_employe(self, request, pk=None):
        """Assigner un employé à une ligne"""
        line = self.get_object()
        employe_id = request.data.get('employe_id')
        
        if not employe_id:
            return Response(
                {'error': 'employe_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from accounts.models import User
            employe = User.objects.get(id=employe_id, role='EMPLOYE')
        except User.DoesNotExist:
            return Response(
                {'error': 'Employé non trouvé ou rôle incorrect'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérification : l'employé doit appartenir à la même entreprise que la ligne
        # Si l'employé a déjà des lignes, elles doivent être de la même entreprise
        lignes_existantes = Line.objects.filter(employe=employe).exclude(id=line.id)
        if lignes_existantes.exists():
            entreprise_employe = lignes_existantes.first().company
            if entreprise_employe != line.company:
                return Response(
                    {'error': f'Employé déjà affecté à une ligne de l\'entreprise {entreprise_employe.raison_sociale}. Affectation inter-entreprise refusée.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        line.employe = employe
        line.save()
        
        return Response({
            'message': 'Employé assigné avec succès',
            'line': LineSerializer(line).data
        })
    
    @extend_schema(
        summary="Retirer l'employé d'une ligne",
        description="Désassocier le compte employé d'une ligne"
    )
    @action(detail=True, methods=['post'])
    def retirer_employe(self, request, pk=None):
        """Retirer l'employé d'une ligne"""
        line = self.get_object()
        line.employe = None
        line.save()
        
        return Response({
            'message': 'Employé retiré avec succès',
            'line': LineSerializer(line).data
        })
    
    @extend_schema(
        summary="Changer le statut d'une ligne",
        description="Activer, désactiver ou suspendre une ligne",
        request=ChangeStatutSerializer
    )
    @action(detail=True, methods=['post'])
    def change_statut(self, request, pk=None):
        """Changer le statut d'une ligne"""
        line = self.get_object()
        serializer = ChangeStatutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ancien_statut = line.statut
        nouveau_statut = serializer.validated_data['nouveau_statut']
        raison = serializer.validated_data['raison']
        
        line.statut = nouveau_statut
        line.save()
        
        # TODO: Logger le changement
        
        return Response({
            'message': f'Statut changé de {ancien_statut} à {nouveau_statut}',
            'line': LineSerializer(line).data
        })
    
    @extend_schema(
        summary="Modifier le cycle de facturation",
        description="Changer entre HYB (Hybride) et OP (Opérationnel)"
    )
    @action(detail=True, methods=['post'])
    def change_cycle(self, request, pk=None):
        """Changer le cycle de facturation"""
        line = self.get_object()
        nouveau_cycle = request.data.get('cycle')
        
        if nouveau_cycle not in ['HYB', 'OP']:
            return Response(
                {'error': 'Cycle doit être HYB ou OP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ancien_cycle = line.cycle
        line.cycle = nouveau_cycle
        line.save()
        
        return Response({
            'message': f'Cycle changé de {ancien_cycle} à {nouveau_cycle}',
            'line': LineSerializer(line).data
        })


class PackageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des forfaits (packages)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type_forfait', 'est_actif']
    search_fields = ['nom', 'code']
    ordering_fields = ['date_creation', 'nom', 'prix_mensuel']
    ordering = ['nom']
    
    def get_permissions(self):
        """Lecture pour tous, écriture pour agents/chefs/admins uniquement"""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), CanManageTarifs()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PackageListSerializer
        elif self.action == 'create':
            return PackageCreateSerializer
        return PackageSerializer
    
    def get_queryset(self):
        """Tous les utilisateurs authentifiés peuvent voir les forfaits"""
        return Package.objects.all()
    
    @extend_schema(
        summary="Créer un forfait",
        description="Créer un nouveau forfait avec quotas DATA/VOIX/SMS",
        request=PackageCreateSerializer,
        responses={201: PackageSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Créer un forfait"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        package = serializer.save()
        
        output_serializer = PackageSerializer(package)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Activer/Désactiver un forfait",
        description="Rendre un forfait actif ou inactif"
    )
    @action(detail=True, methods=['post'])
    def toggle_actif(self, request, pk=None):
        """Activer/désactiver un forfait"""
        package = self.get_object()
        package.est_actif = not package.est_actif
        package.save()
        
        return Response({
            'message': f'Forfait {"activé" if package.est_actif else "désactivé"}',
            'package': PackageSerializer(package).data
        })


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des services
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type_service', 'est_actif']
    search_fields = ['nom', 'code']
    ordering_fields = ['date_creation', 'nom']
    ordering = ['nom']
    
    def get_permissions(self):
        """Lecture pour tous, écriture pour agents/chefs/admins uniquement"""
        if self.action in ['list', 'retrieve', 'tarifs']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), CanManageServices()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceCreateSerializer
        return ServiceSerializer
    
    def get_queryset(self):
        """Tous les utilisateurs authentifiés peuvent voir les services"""
        return Service.objects.all().prefetch_related('tarifs')
    
    @extend_schema(
        summary="Créer un service",
        description="Créer un nouveau service avec ses tarifs",
        request=ServiceCreateSerializer,
        responses={201: ServiceSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Créer un service avec tarifs"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = serializer.save()
        
        output_serializer = ServiceSerializer(service)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Activer/Désactiver un service",
        description="Rendre un service actif ou inactif"
    )
    @action(detail=True, methods=['post'])
    def toggle_actif(self, request, pk=None):
        """Activer/désactiver un service"""
        service = self.get_object()
        service.est_actif = not service.est_actif
        service.save()
        
        return Response({
            'message': f'Service {"activé" if service.est_actif else "désactivé"}',
            'service': ServiceSerializer(service).data
        })
    
    @extend_schema(
        summary="Liste des tarifs d'un service",
        description="Tous les tarifs (options) disponibles pour ce service",
        responses={200: TarifServiceSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def tarifs(self, request, pk=None):
        """Liste des tarifs d'un service"""
        service = self.get_object()
        tarifs = service.tarifs.all()
        
        # Filtre optionnel par statut actif
        actif_only = request.query_params.get('actif_only')
        if actif_only and actif_only.lower() == 'true':
            tarifs = tarifs.filter(est_actif=True)
        
        serializer = TarifServiceSerializer(tarifs, many=True)
        return Response(serializer.data)


class TarifServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des tarifs de services
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['service', 'est_actif']
    search_fields = ['nom_option']
    
    def get_permissions(self):
        """Lecture pour tous, écriture pour agents/chefs/admins uniquement"""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), CanManageTarifs()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TarifServiceCreateSerializer
        return TarifServiceSerializer
    
    def get_queryset(self):
        """Tous les utilisateurs authentifiés peuvent voir les tarifs"""
        return TarifService.objects.all().select_related('service')
    
    @extend_schema(
        summary="Activer/Désactiver un tarif",
        description="Rendre un tarif actif ou inactif"
    )
    @action(detail=True, methods=['post'])
    def toggle_actif(self, request, pk=None):
        """Activer/désactiver un tarif"""
        tarif = self.get_object()
        tarif.est_actif = not tarif.est_actif
        tarif.save()
        
        return Response({
            'message': f'Tarif {"activé" if tarif.est_actif else "désactivé"}',
            'tarif': TarifServiceSerializer(tarif).data
        })



class CommercialViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des commerciaux"""
    permission_classes = [IsAuthenticated, IsAgentFacturation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['est_actif']
    search_fields = ['nom', 'prenom', 'matricule', 'telephone']
    ordering_fields = ['nom', 'prenom', 'date_creation']
    ordering = ['nom']

    def get_serializer_class(self):
        if self.action == 'create':
            return CommercialCreateSerializer
        return CommercialSerializer

    def get_queryset(self):
        return Commercial.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        commercial = serializer.save()
        return Response(CommercialSerializer(commercial).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def toggle_actif(self, request, pk=None):
        commercial = self.get_object()
        # Empêcher la désactivation si lié à un contrat actif
        if commercial.est_actif and commercial.contrats.filter(est_resilie=False).exists():
            return Response(
                {'error': 'Ce commercial est lié à des contrats actifs. Transférez les contrats avant de le désactiver.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        commercial.est_actif = not commercial.est_actif
        commercial.save()
        return Response(CommercialSerializer(commercial).data)


# ==================== VIEWSETS PHASE 4 : FACTURATION ====================

from datetime import datetime, timedelta
from decimal import Decimal
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.core.files.base import ContentFile
import uuid

from .models import Invoice, HistoriqueFacturation, Publication
from .serializers import (
    InvoiceSerializer, InvoiceListSerializer, InvoiceCreateSerializer,
    GenerateInvoiceSerializer, CalculLineInvoiceSerializer,
    ValiderInvoiceSerializer, AnnulerInvoiceSerializer,
    HistoriqueFacturationSerializer, PublicationSerializer,
    PublicationListSerializer, PublicationCreateSerializer,
    PublishInvoicesSerializer, UploadPDFSerializer, InvoiceStatsSerializer
)
from .services.calcul_tarification import CalculateurTarification
from accounts.permissions import (
    CanGenerateInvoices, CanManageInvoices, CanUploadPDF, CanValidateInvoices
)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des factures
    """
    permission_classes = [IsAuthenticated, CanManageInvoices]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['company', 'statut', 'periode_debut', 'periode_fin']
    search_fields = ['numero_facture', 'company__raison_sociale', 'company__compte']
    ordering_fields = ['date_emission', 'montant_ttc', 'date_echeance']
    ordering = ['-date_emission']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        elif self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action == 'generate':
            return GenerateInvoiceSerializer
        elif self.action == 'calculate_line':
            return CalculLineInvoiceSerializer
        elif self.action == 'valider':
            return ValiderInvoiceSerializer
        elif self.action == 'annuler':
            return AnnulerInvoiceSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        """Filtrer selon le rôle de l'utilisateur"""
        user = self.request.user
        
        # Admin, Chef, Agent voient toutes les factures
        if user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']:
            return Invoice.objects.all().select_related('company', 'line', 'line__employe')
        
        # Payeur voit uniquement ses factures PUBLIEE
        if user.role == 'PAYEUR':
            return Invoice.objects.filter(
                company__payeur=user,
                statut='PUBLIEE'  # Sécurité : uniquement factures publiées
            ).select_related('company', 'line', 'line__employe')
        
        # Employé : uniquement les factures individuelles PUBLIEE de ses lignes
        if user.role == 'EMPLOYE':
            return Invoice.objects.filter(
                line__employe=user,
                statut='PUBLIEE'  # Sécurité : uniquement factures publiées
            ).select_related('company', 'line', 'line__employe')

        return Invoice.objects.none()
    
    def update(self, request, *args, **kwargs):
        """Empêcher modification des factures publiées ou payées"""
        invoice = self.get_object()
        if invoice.statut in ['PUBLIEE', 'PAYEE']:
            return Response(
                {'error': f'Impossible de modifier une facture au statut {invoice.statut}'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Empêcher modification partielle des factures publiées ou payées"""
        invoice = self.get_object()
        if invoice.statut in ['PUBLIEE', 'PAYEE']:
            return Response(
                {'error': f'Impossible de modifier une facture au statut {invoice.statut}'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Empêcher suppression des factures publiées ou payées"""
        invoice = self.get_object()
        if invoice.statut in ['PUBLIEE', 'PAYEE']:
            return Response(
                {'error': f'Impossible de supprimer une facture au statut {invoice.statut}'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='pdf-preview')
    def preview_pdf(self, request, pk=None):
        """Retourne le PDF encodé pour contourner les intercepteurs de téléchargements."""
        import base64
        import os

        invoice = self.get_object()
        if not invoice.fichier_pdf or not invoice.fichier_pdf.name:
            return Response({'error': 'Aucun PDF associé à cette facture'}, status=status.HTTP_404_NOT_FOUND)
        if not os.path.exists(invoice.fichier_pdf.path):
            return Response({'error': 'Le fichier PDF est introuvable sur le serveur'}, status=status.HTTP_404_NOT_FOUND)

        try:
            with invoice.fichier_pdf.open('rb') as pdf_file:
                contenu = base64.b64encode(pdf_file.read()).decode('ascii')
            return Response({
                'filename': f'{invoice.numero_facture}.pdf',
                'content_base64': contenu,
            })
        except OSError:
            return Response({'error': 'Erreur lors de la lecture du fichier PDF'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @extend_schema(
        summary="Télécharger le PDF d'une facture",
        description="Téléchargement sécurisé du PDF de la facture. Vérifie les droits d'accès.",
        responses={
            200: {'description': 'PDF de la facture', 'content': {'application/pdf': {}}},
            403: {'description': 'Accès interdit'},
            404: {'description': 'Facture ou PDF non trouvé'}
        }
    )
    @action(detail=True, methods=['get'], url_path='pdf')
    def download_pdf(self, request, pk=None):
        """
        Endpoint sécurisé pour télécharger le PDF d'une facture.
        Vérifie que l'utilisateur a le droit d'accéder à cette facture.
        """
        from django.http import FileResponse, Http404
        import os
        
        invoice = self.get_object()  # Utilise get_queryset() donc déjà filtré par rôle
        
        # Vérifier que le PDF existe
        if not invoice.fichier_pdf or not invoice.fichier_pdf.name:
            return Response(
                {'error': 'Aucun PDF associé à cette facture'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier que le fichier existe physiquement
        if not os.path.exists(invoice.fichier_pdf.path):
            return Response(
                {'error': 'Le fichier PDF est introuvable sur le serveur'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Retourner le PDF avec le bon Content-Type
        try:
            response = FileResponse(
                invoice.fichier_pdf.open('rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'inline; filename="{invoice.numero_facture}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la lecture du fichier : {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Générer des factures en masse",
        description="Générer des factures pour un cycle de facturation",
        request=GenerateInvoiceSerializer,
        responses={200: InvoiceListSerializer(many=True)}
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanGenerateInvoices])
    def generate(self, request):
        """Générer des factures en masse"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cycle = serializer.validated_data['cycle']
        periode_debut = serializer.validated_data['periode_debut']
        periode_fin = serializer.validated_data['periode_fin']
        company_ids = serializer.validated_data.get('company_ids', [])
        
        # Filtrer les entreprises à facturer
        companies_query = Company.objects.all()
        if company_ids:
            companies_query = companies_query.filter(id__in=company_ids)
        
        factures_creees = []
        erreurs = []
        
        with transaction.atomic():
            for company in companies_query:
                try:
                    # Filtrer les lignes par cycle
                    lignes = company.lines.filter(cycle=cycle, statut='ACTIF')
                    
                    if not lignes.exists():
                        continue
                    
                    # Générer numéro de facture unique
                    numero_facture = self._generer_numero_facture(company, periode_debut)
                    
                    # Calculer montants (simplifié pour l'instant)
                    # En prod, il faudrait récupérer les vraies consommations
                    montant_ht = Decimal('0')
                    for ligne in lignes:
                        montant_ht += ligne.forfait
                    
                    # TVA 18%
                    montant_tva = montant_ht * Decimal('0.18')
                    montant_ttc = montant_ht + montant_tva
                    
                    # Date d'échéance : 30 jours après fin période
                    date_echeance = periode_fin + timedelta(days=30)
                    
                    # Créer la facture
                    facture = Invoice.objects.create(
                        company=company,
                        numero_facture=numero_facture,
                        periode_debut=periode_debut,
                        periode_fin=periode_fin,
                        montant_ht=montant_ht,
                        montant_tva=montant_tva,
                        montant_ttc=montant_ttc,
                        date_echeance=date_echeance,
                        statut='BROUILLON'
                    )
                    
                    # Logger l'action
                    HistoriqueFacturation.objects.create(
                        invoice=facture,
                        utilisateur=request.user,
                        type_action='CREATION',
                        nouveau_statut='BROUILLON',
                        commentaire=f'Facture générée automatiquement pour cycle {cycle}'
                    )
                    
                    factures_creees.append(facture)
                    
                except Exception as e:
                    erreurs.append({
                        'company': company.raison_sociale,
                        'erreur': str(e)
                    })
        
        return Response({
            'message': f'{len(factures_creees)} facture(s) générée(s)',
            'factures': InvoiceListSerializer(factures_creees, many=True).data,
            'erreurs': erreurs
        })
    
    @extend_schema(
        summary="Calculer la facture d'une ligne",
        description="Calculer le montant détaillé d'une ligne avec consommations",
        request=CalculLineInvoiceSerializer
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanGenerateInvoices])
    def calculate_line(self, request):
        """Calculer la facture d'une ligne"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        line_id = serializer.validated_data['line_id']
        conso_data_mo = serializer.validated_data['conso_data_mo']
        conso_duree_secondes = serializer.validated_data['conso_duree_secondes']
        conso_sms = serializer.validated_data['conso_sms']
        services_supplementaires = serializer.validated_data.get('services_supplementaires', [])
        
        try:
            ligne = Line.objects.get(id=line_id)
        except Line.DoesNotExist:
            return Response(
                {'error': 'Ligne non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Récupérer les quotas du forfait (à améliorer avec vraie liaison Package)
        # Pour l'instant, on suppose pas de forfait DATA/VOIX/SMS
        forfait_data_mo = 0
        forfait_minutes = 0
        forfait_sms = 0
        
        # Calculer avec le service de tarification
        calcul = CalculateurTarification.calculer_facture_ligne(
            forfait_prix=ligne.forfait,
            forfait_data_mo=forfait_data_mo,
            forfait_minutes=forfait_minutes,
            forfait_sms=forfait_sms,
            conso_data_mo=conso_data_mo,
            conso_duree_secondes=conso_duree_secondes,
            conso_sms=conso_sms,
            services_supplementaires=services_supplementaires
        )
        
        return Response({
            'ligne': {
                'msisdn': ligne.msisdn,
                'utilisateur': ligne.utilisateur,
                'company': ligne.company.raison_sociale
            },
            'calcul': calcul
        })
    
    @extend_schema(
        summary="Valider une facture",
        description="Passer une facture de BROUILLON à EN_COURS",
        request=ValiderInvoiceSerializer
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanValidateInvoices])
    def valider(self, request, pk=None):
        """Valider une facture"""
        facture = self.get_object()
        
        if facture.statut != 'BROUILLON':
            return Response(
                {'error': f'Seules les factures BROUILLON peuvent être validées (statut actuel: {facture.statut})'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ancien_statut = facture.statut
        facture.statut = 'EN_COURS'
        facture.save()
        
        # Logger l'action
        HistoriqueFacturation.objects.create(
            invoice=facture,
            utilisateur=request.user,
            type_action='VALIDATION',
            ancien_statut=ancien_statut,
            nouveau_statut='EN_COURS',
            commentaire=serializer.validated_data.get('commentaire', '')
        )
        
        return Response({
            'message': 'Facture validée',
            'facture': InvoiceSerializer(facture).data
        })
    
    @extend_schema(
        summary="Annuler une facture",
        description="Annuler une facture",
        request=AnnulerInvoiceSerializer
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanValidateInvoices])
    def annuler(self, request, pk=None):
        """Annuler une facture"""
        facture = self.get_object()
        
        if facture.statut == 'ANNULEE':
            return Response(
                {'error': 'Cette facture est déjà annulée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ancien_statut = facture.statut
        facture.statut = 'ANNULEE'
        facture.save()
        
        # Logger l'action
        HistoriqueFacturation.objects.create(
            invoice=facture,
            utilisateur=request.user,
            type_action='ANNULATION',
            ancien_statut=ancien_statut,
            nouveau_statut='ANNULEE',
            commentaire=serializer.validated_data['raison']
        )
        
        return Response({
            'message': 'Facture annulée',
            'facture': InvoiceSerializer(facture).data
        })
    
    @extend_schema(
        summary="Attacher un PDF à une facture",
        description="Uploader et attacher un fichier PDF à une facture",
        request=UploadPDFSerializer
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanUploadPDF])
    def attach_pdf(self, request, pk=None):
        """Attacher un PDF à une facture"""
        facture = self.get_object()
        serializer = UploadPDFSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        fichier = serializer.validated_data['fichier']
        
        # Sauvegarder le fichier
        facture.fichier_pdf = fichier
        
        # Passer en VALIDEE si EN_COURS
        ancien_statut = facture.statut
        if facture.statut == 'EN_COURS':
            facture.statut = 'VALIDEE'
        
        facture.save()
        
        # Logger l'action
        HistoriqueFacturation.objects.create(
            invoice=facture,
            utilisateur=request.user,
            type_action='MODIFICATION',
            ancien_statut=ancien_statut,
            nouveau_statut=facture.statut,
            commentaire='PDF attaché à la facture'
        )
        
        return Response({
            'message': 'PDF attaché avec succès',
            'facture': InvoiceSerializer(facture).data
        })
    
    @extend_schema(
        summary="Statistiques des factures",
        description="Statistiques globales sur les factures"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des factures"""
        queryset = self.get_queryset()
        
        stats = {
            'total_factures': queryset.count(),
            'factures_par_statut': dict(
                queryset.values('statut').annotate(count=Count('id')).values_list('statut', 'count')
            ),
            'montant_total_ttc': queryset.aggregate(total=Sum('montant_ttc'))['total'] or Decimal('0'),
            'montant_par_statut': dict(
                queryset.values('statut').annotate(total=Sum('montant_ttc')).values_list('statut', 'total')
            )
        }
        
        return Response(stats)
    
    @extend_schema(
        summary="Liste des factures à publier",
        description="Récupérer la liste des factures VALIDEE prêtes à être publiées"
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, CanPublishInvoices])
    def factures_a_publier(self, request):
        """Liste des factures VALIDEE à publier"""
        factures = Invoice.objects.filter(statut='VALIDEE').select_related('company', 'line')
        
        # Filtres optionnels
        cycle = request.query_params.get('cycle')
        if cycle:
            factures = factures.filter(company__lines__cycle=cycle).distinct()
        
        periode = request.query_params.get('periode')  # Format: YYYY-MM
        if periode:
            factures = factures.filter(periode_debut__startswith=periode)
        
        serializer = InvoiceListSerializer(factures, many=True)
        
        # Stats rapides
        total_factures = factures.count()
        montant_total = factures.aggregate(total=Sum('montant_ttc'))['total'] or Decimal('0')
        
        return Response({
            'factures': serializer.data,
            'stats': {
                'total_factures': total_factures,
                'montant_total': float(montant_total)
            }
        })
    
    @extend_schema(
        summary="Publier des factures en masse",
        description="Publier plusieurs factures VALIDEE en une seule action"
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanPublishInvoices])
    def publier_masse(self, request):
        """
        Publier plusieurs factures en masse
        
        Workflow :
        1. Vérifie que toutes les factures existent et sont VALIDEE
        2. Vérifie que toutes ont un fichier PDF
        3. Vérifie que toutes ont le même cycle et la même période
        4. Change statut VALIDEE → PUBLIEE en transaction atomique
        5. Crée historique pour chaque facture
        6. Crée ou met à jour Publication
        """
        from django.db import transaction
        from decimal import Decimal
        
        invoice_ids = request.data.get('invoice_ids', [])
        notification_channels = request.data.get('notification_channels', [])
        if not isinstance(notification_channels, list) or any(channel not in ['EMAIL', 'SMS'] for channel in notification_channels):
            return Response({'error': 'Canaux de notification invalides'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not invoice_ids:
            return Response(
                {'error': 'Aucune facture sélectionnée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que toutes les factures existent
        factures = Invoice.objects.filter(id__in=invoice_ids).select_related('line')
        
        if factures.count() != len(invoice_ids):
            return Response(
                {'error': f'{len(invoice_ids) - factures.count()} facture(s) introuvable(s)'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier le statut, PDF, cycle et période de chaque facture
        factures_invalides = []
        cycles = set()
        periodes = set()
        
        for facture in factures:
            if facture.statut != 'VALIDEE':
                factures_invalides.append({
                    'id': str(facture.id),
                    'numero': facture.numero_facture,
                    'raison': f'Statut {facture.statut} au lieu de VALIDEE'
                })
            elif not facture.fichier_pdf:
                factures_invalides.append({
                    'id': str(facture.id),
                    'numero': facture.numero_facture,
                    'raison': 'Aucun fichier PDF attaché'
                })
            
            # Collecter cycles et périodes
            cycle = facture.line.cycle if facture.line else 'MIXTE'
            cycles.add(cycle)
            periodes.add((facture.periode_debut, facture.periode_fin))
        
        if factures_invalides:
            return Response(
                {
                    'error': 'Certaines factures ne peuvent pas être publiées',
                    'factures_invalides': factures_invalides,
                    'total_invalides': len(factures_invalides)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que toutes les factures ont le même cycle et la même période
        if len(cycles) > 1:
            return Response(
                {
                    'error': 'Toutes les factures doivent avoir le même cycle de facturation',
                    'cycles_detectes': list(cycles)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(periodes) > 1:
            return Response(
                {
                    'error': 'Toutes les factures doivent avoir la même période de facturation',
                    'periodes_detectees': [
                        {'debut': str(p[0]), 'fin': str(p[1])} for p in periodes
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Tout est OK, on peut publier
        factures_publiees_ids = []
        montant_total = Decimal('0')
        
        with transaction.atomic():
            # Récupérer cycle et période (tous identiques)
            premiere_facture = factures.first()
            cycle_facturation = premiere_facture.line.cycle if premiere_facture.line else 'MIXTE'
            periode_debut = premiere_facture.periode_debut
            periode_fin = premiere_facture.periode_fin
            
            for facture in factures:
                # Changer le statut
                facture.statut = 'PUBLIEE'
                facture.save()
                
                # Logger l'action
                HistoriqueFacturation.objects.create(
                    invoice=facture,
                    utilisateur=request.user,
                    type_action='PUBLICATION',
                    ancien_statut='VALIDEE',
                    nouveau_statut='PUBLIEE',
                    commentaire='Publication en masse'
                )
                
                factures_publiees_ids.append(str(facture.id))
                montant_total += facture.montant_ttc
            
            # Créer ou mettre à jour la Publication
            publication, created = Publication.objects.get_or_create(
                agent=request.user,
                cycle_facturation=cycle_facturation,
                periode_debut=periode_debut,
                periode_fin=periode_fin,
                defaults={
                    'statut': 'PUBLIEE',
                    'nombre_lignes_traitees': len(factures_publiees_ids),
                    'montant_total': montant_total,
                    'commentaire': f'Publication de {len(factures_publiees_ids)} facture(s)'
                }
            )
            
            if not created:
                # Mise à jour
                publication.nombre_lignes_traitees += len(factures_publiees_ids)
                publication.montant_total += montant_total
                publication.save()
        
        notifications = []
        if notification_channels:
            from .services.notification_service import notifier_facture
            for facture in factures:
                notifications.extend(notifier_facture(facture, notification_channels))

        return Response({
            'message': f'{len(factures_publiees_ids)} facture(s) publiée(s) avec succès',
            'factures_publiees': len(factures_publiees_ids),
            'factures_publiees_ids': factures_publiees_ids,
            'montant_total': float(montant_total),
            'publication_id': str(publication.id),
            'publication_created': created,
            'notifications': {
                'demandee': bool(notification_channels),
                'envoyees': sum(item.statut == 'ENVOYEE' for item in notifications),
                'non_configurees': sum(item.statut == 'NON_CONFIGUREE' for item in notifications),
                'echecs': sum(item.statut == 'ECHEC' for item in notifications),
            }
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary="Upload en masse d'un gros PDF et découpage automatique",
        description="Uploader un gros PDF Moov, le découper automatiquement par client et attacher aux factures",
        request=BulkPDFUploadSerializer
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanUploadPDF])
    def upload_bulk_pdf(self, request):
        """
        Upload et découpage automatique d'un gros PDF
        
        Workflow complet :
        1. Upload du gros PDF
        2. Validation du PDF (format, taille, protection, pages)
        3. Analyse et découpage en blocs par client (détection MSISDN/Compte)
        4. Génération de PDF individuels
        5. Matching automatique avec les factures existantes
        6. Attachement des PDF individuels aux factures
        7. Changement de statut EN_COURS → VALIDEE
        
        IMPORTANT: Les factures passent à VALIDEE, jamais PUBLIEE automatiquement.
        La publication doit être explicite via l'endpoint publier_masse.
        """
        serializer = BulkPDFUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        fichier = serializer.validated_data['fichier']
        auto_match = serializer.validated_data.get('auto_match', True)
        type_facture = serializer.validated_data.get('type_facture', 'SOM')
        cycle = serializer.validated_data.get('cycle')
        periode_debut = serializer.validated_data.get('periode_debut')
        periode_fin = serializer.validated_data.get('periode_fin')
        
        try:
            # Importer les services PDF
            from .services.pdf_processor import PDFProcessor, PDFMatcher
            
            # Vérifier que PyPDF2 est disponible
            PDFProcessor.check_dependencies()
            
            # 1. Traiter le PDF (découpage automatique)
            result = PDFProcessor.process_global_pdf(fichier) if type_facture == 'GLO' else PDFProcessor.process_bulk_pdf(fichier)
            
            if not result.get('success'):
                return Response(
                    {
                        'error': result.get('error', 'Erreur lors du traitement du PDF'),
                        'warnings': result.get('warnings', []),
                        'errors_per_page': result.get('errors_per_page', [])
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response_data = {
                'message': f'PDF traité avec succès',
                'summary': {
                    'total_pages': result['total_pages'],
                    'blocks_detected': result['total_blocks'],
                    'files_created': result['files_created']
                },
                'warnings': result.get('warnings', []),
                'errors_per_page': result.get('errors_per_page', []),
                'split_errors': result.get('split_errors', [])
            }
            
            # 2. Si auto_match activé, matcher avec les factures
            if auto_match:
                # Filtrer les factures candidates (EN_COURS uniquement)
                invoices_query = self.get_queryset().filter(statut='EN_COURS')
                # Factures déjà traitées (pour détecter les réimports)
                processed_invoices_query = self.get_queryset().exclude(statut='EN_COURS')
                if type_facture == 'GLO':
                    invoices_query = invoices_query.filter(line__isnull=True)
                    processed_invoices_query = processed_invoices_query.filter(line__isnull=True)
                
                if cycle and type_facture != 'GLO':
                    # Filtrer par cycle via les lignes
                    invoices_query = invoices_query.filter(
                        company__lines__cycle=cycle
                    ).distinct()
                    processed_invoices_query = processed_invoices_query.filter(
                        company__lines__cycle=cycle
                    ).distinct()
                
                if periode_debut and periode_fin:
                    invoices_query = invoices_query.filter(
                        periode_debut=periode_debut,
                        periode_fin=periode_fin
                    )
                    processed_invoices_query = processed_invoices_query.filter(
                        periode_debut=periode_debut,
                        periode_fin=periode_fin
                    )
                
                # Matcher et attacher automatiquement
                match_result = PDFMatcher.auto_attach_pdfs(
                    result['files'],
                    invoices_query,
                    processed_invoices_query, invoice_type=type_facture
                )
                
                response_data['matching'] = {
                    'total_files': match_result['total_files'],
                    'successfully_matched': match_result['matched'],
                    'not_matched': match_result['not_matched'],
                    'skipped_already_processed': len(match_result.get('skipped', [])),
                    'details': {
                        'attached': match_result['attached'],
                        'skipped': match_result['skipped'],
                        'errors': match_result['errors']
                    }
                }
                
                # Logger l'action dans l'historique pour chaque facture attachée
                for attached in match_result['attached']:
                    try:
                        invoice = Invoice.objects.get(id=attached['invoice_id'])
                        HistoriqueFacturation.objects.create(
                            invoice=invoice,
                            utilisateur=request.user,
                            type_action='MODIFICATION',
                            ancien_statut='EN_COURS',
                            nouveau_statut=invoice.statut,
                            commentaire=f'PDF attaché automatiquement : {attached["filename"]}'
                        )
                    except Invoice.DoesNotExist:
                        pass

                # Conserver une trace de l'upload dans l'historique.
                # IMPORTANT : les factures restent VALIDEE après l'upload.
                # La Publication créée ici sert uniquement à tracer l'import,
                # PAS la publication finale aux clients.
                if cycle and periode_debut and periode_fin and match_result['matched'] > 0:
                    attached_ids = [item['invoice_id'] for item in match_result['attached']]
                    montant_total = Invoice.objects.filter(id__in=attached_ids).aggregate(
                        total=Sum('montant_ttc')
                    )['total'] or Decimal('0')

                    publication = Publication.objects.create(
                        agent=request.user,
                        cycle_facturation=cycle,
                        periode_debut=periode_debut,
                        periode_fin=periode_fin,
                        statut='VALIDEE',  # Pas PUBLIEE ! Les factures sont seulement validées
                        nombre_lignes_traitees=match_result['matched'],
                        montant_total=montant_total,
                        commentaire=(
                            f"Import PDF : {result['files_created']} fichier(s) créé(s), "
                            f"{match_result['matched']} facture(s) associée(s), "
                            f"{match_result['not_matched']} sans correspondance."
                        )
                    )
                    response_data['import_trace'] = {
                        'id': str(publication.id),
                        'note': 'Cette trace documente l\'import, PAS la publication finale'
                    }
            else:
                # Juste retourner la liste des fichiers créés sans matching
                response_data['files_without_matching'] = [
                    {
                        'filename': f['filename'],
                        'identifiers': f['identifiers'],
                        'pages': f['pages']
                    }
                    for f in result['files']
                ]
                response_data['message'] += ' (Matching automatique désactivé)'
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ImportError as e:
            return Response(
                {
                    'error': 'PyPDF2 non installé',
                    'solution': 'Installer avec: pip install PyPDF2',
                    'details': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            import traceback
            return Response(
                {
                    'error': f'Erreur lors du traitement du PDF : {str(e)}',
                    'type': type(e).__name__,
                    'traceback': traceback.format_exc() if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generer_numero_facture(self, company, periode_debut):
        """Générer un numéro de facture unique"""
        # Format: FAC-{COMPTE}-{ANNEE}{MOIS}-{SEQUENCE}
        annee_mois = periode_debut.strftime('%Y%m')
        
        # Compter les factures existantes pour ce mois
        count = Invoice.objects.filter(
            company=company,
            numero_facture__startswith=f'FAC-{company.compte}-{annee_mois}'
        ).count()
        
        sequence = str(count + 1).zfill(3)
        return f'FAC-{company.compte}-{annee_mois}-{sequence}'


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour l'historique des publications (lecture seule)
    
    Les publications sont créées automatiquement par :
    - upload_bulk_pdf : trace l'import PDF (statut VALIDEE)
    - publier_masse : trace la publication finale (statut PUBLIEE)
    
    Ce ViewSet ne permet que la consultation de l'historique.
    """
    permission_classes = [IsAuthenticated, IsAgentFacturation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['agent', 'cycle_facturation', 'statut']
    search_fields = ['cycle_facturation']
    ordering_fields = ['date_publication', 'montant_total']
    ordering = ['-date_publication']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PublicationListSerializer
        return PublicationSerializer
    
    def get_queryset(self):
        """Tous les agents voient toutes les publications"""
        return Publication.objects.all().select_related('agent')
        """Créer une publication"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        publication = serializer.save(agent=request.user)
        
    
    @extend_schema(
        summary="Statistiques d'une publication",
        description="Stats détaillées d'une publication"
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Statistiques d'une publication"""
        publication = self.get_object()
        
        stats = {
            'publication_id': str(publication.id),
            'agent': f"{publication.agent.first_name} {publication.agent.last_name}",
            'cycle': publication.cycle_facturation,
            'periode': f"{publication.periode_debut} - {publication.periode_fin}",
            'nombre_lignes_traitees': publication.nombre_lignes_traitees,
            'montant_total': publication.montant_total,
            'date_publication': publication.date_publication
        }
        
        return Response(stats)


class SimulationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les simulations de facturation (Employé + Payeur)"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']  # Pas de PUT/PATCH/DELETE
    ordering = ['-date_simulation']

    def get_queryset(self):
        return Simulation.objects.filter(
            utilisateur=self.request.user
        ).order_by('-date_simulation')

    def get_serializer_class(self):
        if self.action == 'create':
            return SimulationCreateSerializer
        return SimulationSerializer

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
