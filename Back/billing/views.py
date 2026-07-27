from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Company, Line, Package, Service, TarifService,
    Invoice, HistoriqueFacturation, Cycle, Simulation, Publication
)
from .serializers import (
    CompanySerializer, LineSerializer, PackageSerializer,
    ServiceSerializer, TarifServiceSerializer, InvoiceSerializer,
    HistoriqueFacturationSerializer, CycleSerializer,
    SimulationSerializer, PublicationSerializer
)

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    serializer_class = LineSerializer
    permission_classes = [IsAuthenticated]

# ==================== NOUVEAUX VIEWSETS ====================

class PackageViewSet(viewsets.ModelViewSet):
    """ViewSet pour les forfaits"""
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['patch'])
    def toggle_actif(self, request, pk=None):
        """Active/désactive un forfait"""
        package = self.get_object()
        package.est_actif = not package.est_actif
        package.save()
        serializer = self.get_serializer(package)
        return Response(serializer.data)


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet pour les services"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['patch'])
    def toggle_actif(self, request, pk=None):
        """Active/désactive un service"""
        service = self.get_object()
        service.est_actif = not service.est_actif
        service.save()
        serializer = self.get_serializer(service)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def tarifs(self, request, pk=None):
        """Récupère les tarifs d'un service"""
        service = self.get_object()
        tarifs = service.tarifs.all()
        serializer = TarifServiceSerializer(tarifs, many=True)
        return Response(serializer.data)


class TarifServiceViewSet(viewsets.ModelViewSet):
    """ViewSet pour les tarifs des services"""
    queryset = TarifService.objects.all()
    serializer_class = TarifServiceSerializer
    permission_classes = [IsAuthenticated]


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet pour les factures"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def changer_statut(self, request, pk=None):
        """Change le statut d'une facture et enregistre l'historique"""
        invoice = self.get_object()
        nouveau_statut = request.data.get('statut')
        commentaire = request.data.get('commentaire', '')
        
        if not nouveau_statut:
            return Response(
                {'error': 'Le champ statut est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ancien_statut = invoice.statut
        invoice.statut = nouveau_statut
        invoice.save()
        
        # Enregistrer dans l'historique
        HistoriqueFacturation.objects.create(
            invoice=invoice,
            utilisateur=request.user,
            type_action='MODIFICATION',
            ancien_statut=ancien_statut,
            nouveau_statut=nouveau_statut,
            commentaire=commentaire
        )
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)


class HistoriqueFacturationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour l'historique de facturation (lecture seule)"""
    queryset = HistoriqueFacturation.objects.all()
    serializer_class = HistoriqueFacturationSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def par_facture(self, request):
        """Récupère l'historique d'une facture spécifique"""
        invoice_id = request.query_params.get('invoice_id')
        if not invoice_id:
            return Response(
                {'error': 'Le paramètre invoice_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        historique = self.queryset.filter(invoice_id=invoice_id)
        serializer = self.get_serializer(historique, many=True)
        return Response(serializer.data)


class CycleViewSet(viewsets.ModelViewSet):
    """ViewSet pour les cycles (liaison ligne-service)"""
    queryset = Cycle.objects.all()
    serializer_class = CycleSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def par_ligne(self, request):
        """Récupère les cycles d'une ligne spécifique"""
        line_id = request.query_params.get('line_id')
        if not line_id:
            return Response(
                {'error': 'Le paramètre line_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cycles = self.queryset.filter(line_id=line_id, est_actif=True)
        serializer = self.get_serializer(cycles, many=True)
        return Response(serializer.data)


class SimulationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les simulations"""
    queryset = Simulation.objects.all()
    serializer_class = SimulationSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Crée une nouvelle simulation"""
        data = request.data.copy()
        data['utilisateur'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mes_simulations(self, request):
        """Récupère les simulations de l'utilisateur connecté"""
        simulations = self.queryset.filter(utilisateur=request.user)
        serializer = self.get_serializer(simulations, many=True)
        return Response(serializer.data)


class PublicationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les publications"""
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Crée une nouvelle publication"""
        data = request.data.copy()
        data['agent'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mes_publications(self, request):
        """Récupère les publications de l'agent connecté"""
        publications = self.queryset.filter(agent=request.user)
        serializer = self.get_serializer(publications, many=True)
        return Response(serializer.data)
