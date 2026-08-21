"""
Views pour l'application billing
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from django.db import transaction
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Company, Line, Package, Service, TarifService, Commercial, ContractRequest, AuditContrat, Simulation
from .serializers import CommercialSerializer, CommercialCreateSerializer, ContractRequestSerializer, ContractRequestCreateSerializer, AuditContratSerializer
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
from accounts.models import User
from io import BytesIO


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

        # Commercial voit uniquement les contrats qu'il a prospectés
        if user.role == 'COMMERCIAL':
            return Company.objects.filter(
                commercial__user=user
            ).select_related('commercial', 'payeur').prefetch_related('lines')
        
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

    @action(detail=True, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request, pk=None):
        """GÃ©nÃ¨re un document PDF du contrat et de ses lignes."""
        company = self.get_object()
        from .services.contract_pdf import generer_pdf_contrat
        contenu = generer_pdf_contrat(company)
        nom_fichier = f"contrat_{company.compte}.pdf".replace('/', '_').replace('\\', '_')
        return FileResponse(contenu, as_attachment=True, filename=nom_fichier, content_type='application/pdf')

    @action(detail=True, methods=['get'], url_path='export-excel')
    def export_excel(self, request, pk=None):
        """Génère un fichier Excel de synthèse du contrat et de ses lignes."""
        company = self.get_object()
        try:
            from .services.contract_excel import generer_excel_contrat
        except ImportError:
            return Response(
                {'error': "L'export Excel n'est pas disponible. Installez la dépendance openpyxl."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        contenu = generer_excel_contrat(company)
        nom_fichier = f"contrat_{company.compte}.xlsx".replace('/', '_').replace('\\', '_')
        return FileResponse(
            contenu,
            as_attachment=True,
            filename=nom_fichier,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.pdfgen import canvas
        except ImportError:
            return Response(
                {'error': 'La gÃ©nÃ©ration PDF n’est pas disponible sur le serveur.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        contenu = BytesIO()
        pdf = canvas.Canvas(contenu, pagesize=A4)
        largeur, hauteur = A4
        y = hauteur - 2 * cm

        def nouvelle_page():
            nonlocal y
            pdf.showPage()
            y = hauteur - 2 * cm

        def ligne(texte='', gras=False, retrait=0):
            nonlocal y
            if y < 2 * cm:
                nouvelle_page()
            pdf.setFont('Helvetica-Bold' if gras else 'Helvetica', 10)
            # ReportLab ne fait pas le retour automatique sur canvas : limiter
            # les lignes longues du commentaire et des adresses.
            texte = str(texte or '-').replace('\n', ' ')
            while texte:
                morceau, texte = texte[:105], texte[105:]
                pdf.drawString(2 * cm + retrait, y, morceau)
                y -= 0.55 * cm
                if texte and y < 2 * cm:
                    nouvelle_page()

        pdf.setTitle(f'Contrat {company.compte}')
        pdf.setFont('Helvetica-Bold', 18)
        pdf.drawString(2 * cm, y, 'MOOV AFRICA - CONTRAT CLIENT')
        y -= 1.1 * cm
        ligne(f'Code contrat : {company.compte}', gras=True)
        ligne(f'Raison sociale : {company.raison_sociale}')
        ligne(f'Categorie : {company.get_categorie_display()}')
        ligne(f'Statut : {company.statut}')
        ligne(f'Statut factures : {company.statut_factures}')
        ligne(f'Date effet : {company.date_effet or "-"}')
        ligne(f'Date fin : {company.date_fin or "-"}')
        ligne(f'Mode reglement : {company.get_mode_reglement_display()}')
        ligne(f'Exonere TVA : {"Oui" if company.est_exonere else "Non"}')
        ligne(f'Adresse 1 : {company.adresse or "-"}')
        ligne(f'Adresse 2 : {company.adresse_ligne2 or "-"}')
        ligne(f'Observation : {company.observation or "-"}')
        ligne(f'Revenu : {company.type_revenu or "-"}')
        if company.commercial:
            ligne(f'Commercial : {company.commercial.prenom} {company.commercial.nom}')
        if company.payeur:
            ligne(f'Payeur : {company.payeur.first_name} {company.payeur.last_name} ({company.payeur.email})')
        if company.est_resilie:
            ligne('CONTRAT RESILIE', gras=True)
            ligne(f'Date resiliation : {company.date_resiliation or "-"}')
            ligne(f'Motif : {company.motif_resiliation or "-"}')

        y -= 0.25 * cm
        ligne(f'LIGNES TELEPHONIQUES ({company.lines.count()})', gras=True)
        for index, item in enumerate(company.lines.select_related('employe').order_by('msisdn'), start=1):
            titulaire = '-'
            if item.employe:
                titulaire = f'{item.employe.first_name} {item.employe.last_name}'.strip() or item.employe.username
            services = []
            if item.facture_detaillee:
                services.append('Fact. detaillee')
            if item.option_nolimit:
                services.append(f'No Limit {item.option_nolimit}')
            if item.est_incognito:
                services.append('Incognito')
            if item.est_roaming:
                services.append('Roaming')
            if item.est_internet:
                services.append('Internet')
            if item.est_international:
                services.append('International')
            if item.est_non_revenu:
                services.append('Non revenu')
            ligne(f'{index}. {item.msisdn} | {item.statut} | {item.cycle} | {titulaire}', retrait=0.25 * cm)
            ligne(f'Services : {", ".join(services) if services else "Aucun"}', retrait=0.7 * cm)

        pdf.setFont('Helvetica-Oblique', 8)
        pdf.drawRightString(largeur - 2 * cm, 1.2 * cm, 'Document genere par le Portail Moov Africa')
        pdf.save()
        contenu.seek(0)
        nom_fichier = f"contrat_{company.compte}.pdf".replace('/', '_').replace('\\', '_')
        return FileResponse(contenu, as_attachment=True, filename=nom_fichier, content_type='application/pdf')


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

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        """Crée plusieurs lignes d'un même contrat de manière atomique."""
        if request.user.role not in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']:
            return Response({'error': 'Seuls les agents habilités peuvent ajouter des lignes.'}, status=status.HTTP_403_FORBIDDEN)
        company_id = request.data.get('company')
        lignes = request.data.get('lignes')
        if not company_id or not isinstance(lignes, list) or not lignes:
            return Response(
                {'error': 'company et une liste non vide de lignes sont obligatoires.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(lignes) > 100:
            return Response({'error': '100 lignes maximum par ajout.'}, status=status.HTTP_400_BAD_REQUEST)

        erreurs, serializers_lignes, numeros = [], [], set()
        for index, ligne in enumerate(lignes, start=1):
            serializer = LineCreateSerializer(data={**ligne, 'company': company_id})
            if not serializer.is_valid():
                erreurs.append({'ligne': index, 'erreurs': serializer.errors})
                continue
            numero = serializer.validated_data['msisdn']
            if numero in numeros:
                erreurs.append({'ligne': index, 'erreurs': {'msisdn': ['Numéro dupliqué dans cet ajout.']}})
                continue
            numeros.add(numero)
            serializers_lignes.append(serializer)

        if erreurs:
            return Response(
                {'error': "Aucune ligne n'a été ajoutée. Corrigez les erreurs indiquées.", 'erreurs': erreurs},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.db import transaction
        with transaction.atomic():
            nouvelles_lignes = [serializer.save() for serializer in serializers_lignes]
            company = nouvelles_lignes[0].company
            AuditContrat.objects.create(
                company=company,
                utilisateur=request.user,
                type_action='AJOUT_LIGNE',
                description=f'{len(nouvelles_lignes)} lignes ajoutées en lot',
                nouvelles_valeurs={'msisdn': [ligne.msisdn for ligne in nouvelles_lignes]},
            )
        return Response(LineSerializer(nouvelles_lignes, many=True).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='available-employees')
    def available_employees(self, request):
        """Employés disposant d'un MSISDN et encore sans ligne associée."""
        if request.user.role not in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']:
            return Response({'error': 'Accès réservé aux agents habilités.'}, status=status.HTTP_403_FORBIDDEN)

        employees = User.objects.filter(
            role='EMPLOYE',
            telephone__isnull=False,
        ).exclude(telephone='').exclude(lines__isnull=False).order_by('first_name', 'last_name', 'id')

        numeros_deja_utilises = set(Line.objects.values_list('msisdn', flat=True))
        disponibles, numeros_vus = [], set()
        for employee in employees:
            numero = ''.join(ch for ch in str(employee.telephone or '') if ch.isdigit())
            if len(numero) != 8 or numero in numeros_vus or numero in numeros_deja_utilises:
                continue
            numeros_vus.add(numero)
            nom = f'{employee.first_name} {employee.last_name}'.strip() or employee.username
            disponibles.append({
                'id': employee.id,
                'numero': numero,
                'nom': nom,
                'email': employee.email,
            })
        return Response(disponibles)

    def _create_employee_for_line(self, request, line, payload):
        """Crée le compte employé et l'attache de façon atomique à une ligne."""
        if line.employe_id:
            return None, Response(
                {'error': 'Cette ligne est déjà associée à un employé. Retirez d’abord cet employé si vous devez le remplacer.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        first_name = str(payload.get('first_name', '')).strip()
        last_name = str(payload.get('last_name', '')).strip()
        email = str(payload.get('email', '')).strip()
        password = payload.get('password', '')
        errors = {}
        if not first_name:
            errors['first_name'] = ['Le prénom est obligatoire.']
        if not last_name:
            errors['last_name'] = ['Le nom est obligatoire.']
        if not email:
            errors['email'] = ["L'e-mail est obligatoire."]
        if not password:
            errors['password'] = ['Le mot de passe temporaire est obligatoire.']
        if errors:
            return None, Response(errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password)
        except DjangoValidationError as error:
            return None, Response({'password': list(error.messages)}, status=status.HTTP_400_BAD_REQUEST)

        numero = line.msisdn
        if User.objects.filter(Q(username=numero) | Q(telephone=numero)).exists():
            return None, Response(
                {'error': 'Un compte utilisateur utilise déjà ce numéro. Utilisez une autre ligne ou corrigez le compte existant.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            employe = User.objects.create_user(
                username=numero,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                telephone=numero,
                role='EMPLOYE',
                status='ACTIF',
                created_by=request.user,
            )
            line.employe = employe
            line.utilisateur = f'{first_name} {last_name}'.strip()
            line.save(update_fields=['employe', 'utilisateur', 'date_modification'])
            AuditContrat.objects.create(
                company=line.company,
                utilisateur=request.user,
                type_action='MODIFICATION_LIGNE',
                description=f'Compte employé créé et affecté à la ligne {line.msisdn}',
                nouvelles_valeurs={
                    'line_id': line.id,
                    'msisdn': line.msisdn,
                    'employe_id': employe.id,
                    'employe': line.utilisateur,
                },
            )
        return employe, None

    @action(detail=True, methods=['post'], url_path='create-employee')
    def create_employee(self, request, pk=None):
        """Crée un employé pour une ligne existante du contrat affiché."""
        if request.user.role not in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']:
            return Response({'error': 'Accès réservé aux agents habilités.'}, status=status.HTTP_403_FORBIDDEN)
        line = self.get_object()
        employe, error_response = self._create_employee_for_line(request, line, request.data)
        if error_response:
            return error_response
        return Response({
            'message': 'Employé créé et affecté à la ligne avec succès.',
            'employee': {
                'id': employe.id,
                'first_name': employe.first_name,
                'last_name': employe.last_name,
                'email': employe.email,
                'telephone': employe.telephone,
            },
            'line': LineSerializer(line).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='create-employee-with-line')
    def create_employee_with_line(self, request):
        """Crée une ligne dans l'entreprise choisie puis le compte employé lié."""
        if request.user.role not in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']:
            return Response({'error': 'Accès réservé aux agents habilités.'}, status=status.HTTP_403_FORBIDDEN)

        company_id = request.data.get('company')
        try:
            company = Company.objects.get(pk=company_id)
        except (Company.DoesNotExist, ValueError, TypeError):
            return Response({'company': ['Veuillez choisir une entreprise valide.']}, status=status.HTTP_400_BAD_REQUEST)

        line_serializer = LineCreateSerializer(data={
            'company': company.id,
            'msisdn': request.data.get('msisdn', ''),
            'cycle': request.data.get('cycle', 'HYB'),
            'forfait': request.data.get('forfait', '0'),
        })
        line_serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            line = line_serializer.save()
            employe, error_response = self._create_employee_for_line(request, line, request.data)
            if error_response:
                transaction.set_rollback(True)
                return error_response
            AuditContrat.objects.create(
                company=company,
                utilisateur=request.user,
                type_action='AJOUT_LIGNE',
                description=f'Ligne {line.msisdn} créée avec son compte employé',
                nouvelles_valeurs={'msisdn': line.msisdn, 'employe_id': employe.id},
            )
        return Response({
            'message': 'Employé et ligne créés puis liés au contrat avec succès.',
            'employee': {'id': employe.id, 'first_name': employe.first_name, 'last_name': employe.last_name, 'email': employe.email, 'telephone': employe.telephone},
            'line': LineSerializer(line).data,
        }, status=status.HTTP_201_CREATED)
    
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


class ContractRequestViewSet(viewsets.ModelViewSet):
    """Soumission commerciale puis validation opérationnelle d'un contrat."""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'COMMERCIAL':
            return ContractRequest.objects.filter(submitted_by=user).select_related('commercial', 'decision_by', 'company')
        if user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']:
            return ContractRequest.objects.all().select_related('commercial', 'submitted_by', 'decision_by', 'company')
        return ContractRequest.objects.none()

    def get_serializer_class(self):
        return ContractRequestCreateSerializer if self.action == 'create' else ContractRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        demande = serializer.save()
        return Response(ContractRequestSerializer(demande).data, status=status.HTTP_201_CREATED)

    def _can_decide(self, request):
        return request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if not self._can_decide(request):
            return Response({'error': 'Seuls les agents habilités peuvent valider une demande.'}, status=status.HTTP_403_FORBIDDEN)
        demande = self.get_object()
        if demande.statut != ContractRequest.Status.PENDING:
            return Response({'error': 'Cette demande a déjà été traitée.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.db import transaction
        from django.utils import timezone

        try:
            with transaction.atomic():
                payeur_data = demande.payload.get('payeur', {})
                contrat_data = demande.payload.get('contrat', {})
                username = str(payeur_data.get('username') or payeur_data.get('telephone')).strip()
                if User.objects.filter(username=username).exists():
                    raise ValueError('L’identifiant du payeur est déjà utilisé.')
                email = str(payeur_data.get('email') or '').strip()
                if email and User.objects.filter(email=email).exists():
                    raise ValueError('L’e-mail du payeur est déjà utilisé.')

                payeur = User(
                    username=username,
                    email=email,
                    first_name=payeur_data.get('first_name', ''),
                    last_name=payeur_data.get('last_name', ''),
                    telephone=payeur_data.get('telephone', ''),
                    role='PAYEUR', status='ACTIF', est_actif=True,
                    created_by=request.user,
                )
                payeur.password = demande.password_payeur_hash
                payeur.save()

                allowed = {field.name for field in Company._meta.fields} - {
                    'id', 'payeur', 'commercial', 'date_creation', 'date_modification'
                }
                company_data = {key: value for key, value in contrat_data.items() if key in allowed}
                company_data['compte'] = demande.compte_propose
                company_data['payeur'] = payeur
                company_data['commercial'] = demande.commercial
                company_data['statut_factures'] = 'EN_ATTENTE'
                company = Company.objects.create(**company_data)

                demande.statut = ContractRequest.Status.APPROVED
                demande.company = company
                demande.decision_by = request.user
                demande.decision_comment = request.data.get('commentaire', '')
                demande.date_decision = timezone.now()
                demande.save()
                AuditContrat.objects.create(
                    company=company, utilisateur=request.user, type_action='CREATION',
                    description=f'Contrat créé après validation de la demande commerciale {demande.id}',
                    nouvelles_valeurs={'compte': company.compte, 'commercial': demande.commercial.matricule},
                )
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(ContractRequestSerializer(demande).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        if not self._can_decide(request):
            return Response({'error': 'Seuls les agents habilités peuvent rejeter une demande.'}, status=status.HTTP_403_FORBIDDEN)
        demande = self.get_object()
        commentaire = str(request.data.get('commentaire', '')).strip()
        if demande.statut != ContractRequest.Status.PENDING:
            return Response({'error': 'Cette demande a déjà été traitée.'}, status=status.HTTP_400_BAD_REQUEST)
        if not commentaire:
            return Response({'error': 'Un motif de rejet est obligatoire.'}, status=status.HTTP_400_BAD_REQUEST)
        from django.utils import timezone
        demande.statut = ContractRequest.Status.REJECTED
        demande.decision_by = request.user
        demande.decision_comment = commentaire
        demande.date_decision = timezone.now()
        demande.save()
        return Response(ContractRequestSerializer(demande).data)


# ==================== VIEWSETS PHASE 4 : FACTURATION ====================

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import Q, Sum, Count
from django.core.files.base import ContentFile
import uuid
from types import SimpleNamespace

from .models import Invoice, HistoriqueFacturation, Publication, TraitementPDF, BlocFacturesTest
from .serializers import (
    InvoiceSerializer, InvoiceListSerializer, InvoiceCreateSerializer,
    GenerateInvoiceSerializer, CalculLineInvoiceSerializer,
    GenerateTestBlockSerializer, BlocFacturesTestSerializer,
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
        elif self.action == 'generate_test_block':
            return GenerateTestBlockSerializer
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

    def _generer_numero_facture_test(self, type_facture, periode_debut):
        """Produit un numéro reconnu par l'extracteur et unique en base."""
        prefix = f'FAC-TEST-{type_facture}-{periode_debut:%Y%m}-'
        sequence = Invoice.objects.filter(numero_facture__startswith=prefix).count() + 1
        while True:
            numero = f'{prefix}{sequence:04d}'
            if not Invoice.objects.filter(numero_facture=numero).exists():
                return numero
            sequence += 1

    @extend_schema(
        summary='Générer un bloc PDF de test',
        description=(
            'Crée un unique PDF multi-pages de factures de test, crée les factures '
            'EN_COURS correspondantes et lance le même découpage Celery que pour un import PDF.'
        ),
        request=GenerateTestBlockSerializer,
    )
    @action(
        detail=False,
        methods=['post'],
        url_path='generate-test-block',
        permission_classes=[IsAuthenticated, CanGenerateInvoices],
    )
    def generate_test_block(self, request):
        """Crée un bloc de test téléchargeable sans le soumettre au découpage."""
        serializer = GenerateTestBlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        type_facture = data['type_facture']
        periode_debut = data['periode_debut']
        periode_fin = data['periode_fin']
        date_emission = data.get('date_emission') or datetime.now().date()
        date_echeance = date_emission + timedelta(days=data['delai_echeance_jours'])
        libelle = data.get('libelle') or 'Services postpayés de test'
        taux_tva = data['taux_tva']
        company_ids = {item['company_id'] for item in data['items']}
        line_ids = {item['line_id'] for item in data['items'] if item.get('line_id')}
        companies = Company.objects.in_bulk(company_ids)
        lines = Line.objects.select_related('company').in_bulk(line_ids)
        invoices = []
        bloc = None

        try:
            with transaction.atomic():
                for item in data['items']:
                    company = companies[item['company_id']]
                    line = lines.get(item.get('line_id'))
                    montant_ttc = item['montant_ttc']
                    if company.est_exonere:
                        montant_ht = montant_ttc
                        montant_tva = Decimal('0.00')
                    else:
                        divisor = Decimal('1.00') + (taux_tva / Decimal('100.00'))
                        montant_ht = (montant_ttc / divisor).quantize(
                            Decimal('0.01'), rounding=ROUND_HALF_UP
                        )
                        montant_tva = montant_ttc - montant_ht

                    invoice = Invoice.objects.create(
                        company=company,
                        line=line,
                        numero_facture=self._generer_numero_facture_test(type_facture, periode_debut),
                        periode_debut=periode_debut,
                        periode_fin=periode_fin,
                        montant_ht=montant_ht,
                        montant_tva=montant_tva,
                        montant_ttc=montant_ttc,
                        statut='BROUILLON',
                        date_emission_pdf=date_emission,
                        date_echeance=date_echeance,
                        commentaire=(
                            'Facture de test préparée par le portail. '
                            'Elle sera validée seulement après import et découpage du bloc PDF.'
                        ),
                    )
                    HistoriqueFacturation.objects.create(
                        invoice=invoice,
                        utilisateur=request.user,
                        type_action='CREATION',
                        nouveau_statut='BROUILLON',
                        commentaire='Facture de test préparée dans un bloc PDF à importer ultérieurement.',
                    )
                    invoices.append(invoice)

                from .services.test_block_pdf import generate_test_invoice_block
                source_pdf = generate_test_invoice_block(invoices, type_facture, libelle)
                filename = f'bloc_test_{type_facture.lower()}_{periode_debut:%Y%m}_{uuid.uuid4().hex[:8]}.pdf'
                bloc = BlocFacturesTest(
                    createur=request.user,
                    nom_fichier=filename,
                    type_facture=type_facture,
                    periode_debut=periode_debut,
                    periode_fin=periode_fin,
                    date_emission=date_emission,
                    nombre_factures=len(invoices),
                    montant_total_ttc=sum((invoice.montant_ttc for invoice in invoices), Decimal('0.00')),
                    libelle=libelle,
                )
                bloc.fichier_pdf.save(filename, ContentFile(source_pdf.getvalue()), save=False)
                bloc.save()
        except Exception as exc:
            if bloc and bloc.fichier_pdf:
                bloc.fichier_pdf.delete(save=False)
            return Response(
                {'error': 'Impossible de générer le bloc PDF de test.', 'details': str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            from .tasks import traiter_import_pdf
            async_result = traiter_import_pdf.delay(str(traitement.id))
            traitement.task_id = async_result.id
            traitement.save(update_fields=['task_id'])
        except Exception as exc:
            # Ne pas conserver des factures de test impossibles à traiter.
            traitement.fichier_source.delete(save=False)
            traitement.delete()
            Invoice.objects.filter(id__in=[invoice.id for invoice in invoices]).delete()
            return Response(
                {
                    'error': 'Le bloc a été généré mais le service Celery est indisponible.',
                    'details': str(exc),
                    'solution': 'Démarrez Garnet et le worker Celery, puis réessayez.',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                'message': (
                    f'Bloc PDF de test généré avec {len(invoices)} facture(s). '
                    'Le découpage et le rapprochement sont en attente.'
                ),
                'test_block': {
                    'filename': filename,
                    'type_facture': type_facture,
                    'factures_creees': len(invoices),
                    'invoice_ids': [str(invoice.id) for invoice in invoices],
                    'download_url': f'/api/billing/invoices/test-blocks/{traitement.id}/download/',
                },
                'job': {
                    'id': str(traitement.id),
                    'statut': traitement.statut,
                    'progression': traitement.progression,
                    'date_creation': traitement.date_creation.isoformat(),
                },
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(
        detail=False,
        methods=['get'],
        url_path=r'test-blocks/(?P<job_id>[^/.]+)/download',
        permission_classes=[IsAuthenticated, CanGenerateInvoices],
    )
    def download_test_block(self, request, job_id=None):
        """Télécharge le PDF source d'un bloc de test généré par la plateforme."""
        traitement = TraitementPDF.objects.filter(id=job_id, cycle='TEST').first()
        if not traitement:
            return Response({'error': 'Bloc PDF de test introuvable.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role == 'AGENT_FACTURATION' and traitement.agent_id != request.user.id:
            return Response({'error': 'Accès non autorisé à ce bloc PDF.'}, status=status.HTTP_403_FORBIDDEN)
        if not traitement.fichier_source or not traitement.fichier_source.storage.exists(traitement.fichier_source.name):
            return Response({'error': 'Le fichier PDF source est introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            traitement.fichier_source.open('rb'),
            as_attachment=True,
            filename=traitement.fichier_source.name.rsplit('/', 1)[-1],
            content_type='application/pdf',
        )
    
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
        if not isinstance(notification_channels, list):
            return Response({'error': 'Canaux de notification invalides'}, status=status.HTTP_400_BAD_REQUEST)

        notification_channels = list(dict.fromkeys(
            str(channel).upper() for channel in notification_channels
        ))
        canaux_autorises = {'EMAIL', 'SMS'}
        if any(channel not in canaux_autorises for channel in notification_channels):
            return Response(
                {
                    'error': 'Canaux de notification invalides',
                    'canaux_autorises': sorted(canaux_autorises),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        
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
        
        notifications = {
            'demandee': bool(notification_channels),
            'canaux': notification_channels,
            'en_attente': 0,
            'envoyees': 0,
            'non_configurees': 0,
            'echecs': 0,
        }
        if notification_channels:
            try:
                from .tasks import envoyer_notifications_factures
                envoyer_notifications_factures.delay(
                    factures_publiees_ids,
                    notification_channels,
                )
                notifications['en_attente'] = (
                    len(factures_publiees_ids) * len(notification_channels)
                )
            except Exception as exc:
                # La publication reste valide : l'Ã©chec d'un e-mail ne doit pas
                # annuler la mise Ã  disposition des factures dans le portail.
                notifications['echecs'] = len(factures_publiees_ids)
                notifications['detail'] = f'Notification non planifiÃ©e : {exc}'

        return Response({
            'message': f'{len(factures_publiees_ids)} facture(s) publiée(s) avec succès',
            'factures_publiees': len(factures_publiees_ids),
            'factures_publiees_ids': factures_publiees_ids,
            'montant_total': float(montant_total),
            'publication_id': str(publication.id),
            'publication_created': created,
            'notifications': notifications
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

        # Le fichier est d'abord persisté, puis le worker Celery le traite hors
        # de la requête HTTP. L'interface peut ainsi suivre un statut fiable.
        traitement = TraitementPDF.objects.create(
            agent=request.user,
            fichier_source=fichier,
            auto_match=auto_match,
            type_facture=type_facture,
            cycle=cycle or '',
            periode_debut=periode_debut,
            periode_fin=periode_fin,
        )
        try:
            from .tasks import traiter_import_pdf
            async_result = traiter_import_pdf.delay(str(traitement.id))
            traitement.task_id = async_result.id
            traitement.save(update_fields=['task_id'])
        except Exception as exc:
            # Ne pas laisser une fausse tâche en attente si le broker est arrêté.
            traitement.fichier_source.delete(save=False)
            traitement.delete()
            return Response(
                {
                    'error': 'Le service de traitement asynchrone est indisponible.',
                    'details': str(exc),
                    'solution': 'Démarrez Garnet et le worker Celery puis réessayez.',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {
                'message': 'PDF reçu. Le découpage et le rapprochement sont en attente.',
                'job': {
                    'id': str(traitement.id),
                    'statut': traitement.statut,
                    'progression': traitement.progression,
                    'date_creation': traitement.date_creation.isoformat(),
                },
            },
            status=status.HTTP_202_ACCEPTED,
        )
        
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

    @action(
        detail=False,
        methods=['get'],
        url_path=r'pdf-jobs/(?P<job_id>[^/.]+)',
        permission_classes=[IsAuthenticated, CanUploadPDF],
    )
    def pdf_job(self, request, job_id=None):
        """Retourne l'état persistant d'un import PDF asynchrone."""
        traitement = TraitementPDF.objects.filter(id=job_id).select_related('agent').first()
        if not traitement:
            return Response({'error': 'Traitement PDF introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        # Un agent ne voit que ses propres imports. Chef et administrateur peuvent
        # consulter les imports de leur équipe.
        if request.user.role == 'AGENT_FACTURATION' and traitement.agent_id != request.user.id:
            return Response({'error': 'Accès non autorisé à ce traitement.'}, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'id': str(traitement.id),
            'task_id': traitement.task_id,
            'statut': traitement.statut,
            'progression': traitement.progression,
            'resultat': traitement.resultat,
            'erreur': traitement.erreur if traitement.statut == TraitementPDF.Statut.ECHEC else '',
            'date_creation': traitement.date_creation,
            'date_debut': traitement.date_debut,
            'date_fin': traitement.date_fin,
        })
    
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
