"""
Views pour les statistiques et dashboards par rôle
Phase 5 : Dashboards & Stats
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum, Q, Avg, Max, Min
from django.db.models.functions import TruncMonth, TruncDate
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Company, Line, Invoice, Publication, 
    HistoriqueFacturation, Simulation
)
from accounts.models import User
from accounts.permissions import (
    IsSuperAdmin, IsChefFacturation, IsAgentFacturation,
    IsPayeur, IsEmploye
)


# ============================================================
# STATS ADMIN
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def stats_admin(request):
    """
    Statistiques globales pour l'administrateur
    - Vue d'ensemble complète du système
    - Évolution de la facturation
    - Top entreprises et lignes
    """
    
    # Statistiques globales
    total_companies = Company.objects.count()
    total_lines = Line.objects.count()
    total_invoices = Invoice.objects.count()
    
    # Factures par statut
    invoices_by_status = dict(
        Invoice.objects.values('statut')
        .annotate(count=Count('id'))
        .values_list('statut', 'count')
    )
    
    # Montant total facturé
    total_amount = Invoice.objects.aggregate(
        total=Sum('montant_ttc')
    )['total'] or Decimal('0')
    
    # Montant par statut
    amount_by_status = dict(
        Invoice.objects.values('statut')
        .annotate(total=Sum('montant_ttc'))
        .values_list('statut', 'total')
    )
    
    # Évolution mensuelle (12 derniers mois)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    
    evolution_mensuelle = list(
        Invoice.objects
        .filter(date_emission__gte=start_date)
        .annotate(mois=TruncMonth('date_emission'))
        .values('mois')
        .annotate(
            nombre_factures=Count('id'),
            montant_total=Sum('montant_ttc')
        )
        .order_by('mois')
    )
    
    # Top 10 entreprises (par montant facturé)
    top_companies = list(
        Company.objects
        .annotate(
            total_facture=Sum('invoices__montant_ttc'),
            nombre_factures=Count('invoices')
        )
        .filter(total_facture__isnull=False)
        .order_by('-total_facture')[:10]
        .values(
            'id', 'compte', 'raison_sociale', 
            'total_facture', 'nombre_factures'
        )
    )
    
    # Top 10 lignes (par montant)
    top_lines = list(
        Line.objects
        .annotate(
            total_facture=Sum('company__invoices__montant_ttc')
        )
        .filter(total_facture__isnull=False)
        .order_by('-total_facture')[:10]
        .values(
            'id', 'msisdn', 'utilisateur', 
            'company__raison_sociale', 'total_facture'
        )
    )
    
    # Statistiques des agents
    stats_agents = {
        'total_agents': User.objects.filter(role='AGENT_FACTURATION').count(),
        'agents_actifs': User.objects.filter(
            role='AGENT_FACTURATION',
            is_active=True
        ).count(),
        'total_publications': Publication.objects.count(),
    }
    
    # Statistiques des utilisateurs
    stats_utilisateurs = {
        'total_payeurs': User.objects.filter(role='PAYEUR').count(),
        'total_employes': User.objects.filter(role='EMPLOYE').count(),
        'total_simulations': Simulation.objects.count(),
    }
    
    return Response({
        'statistiques_globales': {
            'total_entreprises': total_companies,
            'total_lignes': total_lines,
            'total_factures': total_invoices,
            'montant_total_facture': float(total_amount),
        },
        'factures_par_statut': invoices_by_status,
        'montant_par_statut': {
            k: float(v) for k, v in amount_by_status.items() if v
        },
        'evolution_mensuelle': [
            {
                'mois': item['mois'].strftime('%Y-%m'),
                'nombre_factures': item['nombre_factures'],
                'montant_total': float(item['montant_total'] or 0)
            }
            for item in evolution_mensuelle
        ],
        'top_entreprises': [
            {
                **company,
                'total_facture': float(company['total_facture'] or 0)
            }
            for company in top_companies
        ],
        'top_lignes': [
            {
                **line,
                'total_facture': float(line['total_facture'] or 0)
            }
            for line in top_lines
        ],
        'stats_agents': stats_agents,
        'stats_utilisateurs': stats_utilisateurs,
    })


# ============================================================
# STATS CHEF FACTURATION
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsChefFacturation])
def stats_chef_facturation(request):
    """
    Statistiques pour le chef facturation
    - Agents sous sa responsabilité
    - Publications par période
    - Performance des agents
    """
    
    chef = request.user
    
    # Agents sous responsabilité (créés par ce chef)
    agents = User.objects.filter(
        role='AGENT_FACTURATION',
        created_by=chef
    )
    
    agents_stats = []
    for agent in agents:
        publications = Publication.objects.filter(agent=agent)
        
        agents_stats.append({
            'id': str(agent.id),
            'email': agent.email,
            'nom_complet': agent.get_full_name(),
            'est_actif': agent.is_active,
            'nombre_publications': publications.count(),
            'montant_total_publie': float(
                publications.aggregate(total=Sum('montant_total'))['total'] or 0
            ),
            'lignes_traitees': publications.aggregate(
                total=Sum('nombre_lignes_traitees')
            )['total'] or 0,
        })
    
    # Publications par période (30 derniers jours)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    publications_periode = list(
        Publication.objects
        .filter(
            agent__in=agents,
            date_publication__gte=start_date
        )
        .annotate(jour=TruncDate('date_publication'))
        .values('jour')
        .annotate(
            nombre=Count('id'),
            montant=Sum('montant_total')
        )
        .order_by('jour')
    )
    
    # Performance globale de l'équipe
    total_publications = Publication.objects.filter(agent__in=agents).count()
    total_montant = Publication.objects.filter(agent__in=agents).aggregate(
        total=Sum('montant_total')
    )['total'] or Decimal('0')
    
    return Response({
        'agents': agents_stats,
        'performance_equipe': {
            'nombre_agents': agents.count(),
            'agents_actifs': agents.filter(is_active=True).count(),
            'total_publications': total_publications,
            'montant_total': float(total_montant),
            'moyenne_par_agent': float(total_montant / agents.count()) if agents.count() > 0 else 0,
        },
        'publications_periode': [
            {
                'date': item['jour'].strftime('%Y-%m-%d'),
                'nombre': item['nombre'],
                'montant': float(item['montant'] or 0)
            }
            for item in publications_periode
        ],
    })


# ============================================================
# STATS AGENT FACTURATION
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAgentFacturation])
def stats_agent_facturation(request):
    """
    Statistiques pour un agent de facturation
    - Mes publications
    - Mes stats de performance
    """
    
    agent = request.user
    
    # Mes publications
    mes_publications = Publication.objects.filter(agent=agent)
    
    # Stats globales
    total_publications = mes_publications.count()
    montant_total = mes_publications.aggregate(
        total=Sum('montant_total')
    )['total'] or Decimal('0')
    
    lignes_traitees = mes_publications.aggregate(
        total=Sum('nombre_lignes_traitees')
    )['total'] or 0
    
    # Publications par cycle
    publications_par_cycle = dict(
        mes_publications.values('cycle_facturation')
        .annotate(count=Count('id'))
        .values_list('cycle_facturation', 'count')
    )
    
    # Évolution sur 30 derniers jours
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    evolution_quotidienne = list(
        mes_publications
        .filter(date_publication__gte=start_date)
        .annotate(jour=TruncDate('date_publication'))
        .values('jour')
        .annotate(
            nombre=Count('id'),
            montant=Sum('montant_total'),
            lignes=Sum('nombre_lignes_traitees')
        )
        .order_by('jour')
    )
    
    # Dernières publications
    dernieres_publications = list(
        mes_publications
        .order_by('-date_publication')[:10]
        .values(
            'id', 'cycle_facturation', 'periode_debut', 
            'periode_fin', 'date_publication', 'nombre_lignes_traitees',
            'montant_total', 'statut'
        )
    )
    
    return Response({
        'statistiques': {
            'total_publications': total_publications,
            'montant_total': float(montant_total),
            'lignes_traitees': lignes_traitees,
            'moyenne_par_publication': float(montant_total / total_publications) if total_publications > 0 else 0,
        },
        'publications_par_cycle': publications_par_cycle,
        'evolution_quotidienne': [
            {
                'date': item['jour'].strftime('%Y-%m-%d'),
                'nombre': item['nombre'],
                'montant': float(item['montant'] or 0),
                'lignes': item['lignes'] or 0
            }
            for item in evolution_quotidienne
        ],
        'dernieres_publications': [
            {
                **pub,
                'montant_total': float(pub['montant_total'] or 0)
            }
            for pub in dernieres_publications
        ],
    })


# ============================================================
# STATS PAYEUR
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPayeur])
def stats_payeur(request):
    """
    Statistiques pour un payeur
    - Consommation de son contrat
    - Répartition par ligne
    - Lignes à surveiller (forte consommation)
    """
    
    payeur = request.user
    
    # Entreprises dont je suis payeur
    mes_companies = Company.objects.filter(payeur=payeur)
    
    # Factures de mes entreprises
    mes_factures = Invoice.objects.filter(company__in=mes_companies)
    
    # Statistiques globales
    total_factures = mes_factures.count()
    montant_total = mes_factures.aggregate(
        total=Sum('montant_ttc')
    )['total'] or Decimal('0')
    
    montant_paye = mes_factures.filter(statut='PAYEE').aggregate(
        total=Sum('montant_ttc')
    )['total'] or Decimal('0')
    
    montant_en_attente = mes_factures.filter(
        statut__in=['VALIDEE', 'PUBLIEE']
    ).aggregate(total=Sum('montant_ttc'))['total'] or Decimal('0')
    
    # Répartition par ligne
    mes_lignes = Line.objects.filter(company__in=mes_companies)
    
    repartition_lignes = list(
        mes_lignes
        .annotate(
            montant_facture=Sum('company__invoices__montant_ttc')
        )
        .values(
            'id', 'msisdn', 'utilisateur', 'cycle',
            'company__raison_sociale', 'montant_facture'
        )
        .order_by('-montant_facture')
    )
    
    # Lignes à surveiller (Top 10 consommation)
    lignes_a_surveiller = [
        {
            **ligne,
            'montant_facture': float(ligne['montant_facture'] or 0)
        }
        for ligne in repartition_lignes[:10]
    ]
    
    # Évolution mensuelle (6 derniers mois)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    
    evolution_mensuelle = list(
        mes_factures
        .filter(date_emission__gte=start_date)
        .annotate(mois=TruncMonth('date_emission'))
        .values('mois')
        .annotate(
            nombre=Count('id'),
            montant=Sum('montant_ttc')
        )
        .order_by('mois')
    )
    
    # Factures par statut
    factures_par_statut = dict(
        mes_factures.values('statut')
        .annotate(count=Count('id'))
        .values_list('statut', 'count')
    )
    
    return Response({
        'statistiques': {
            'nombre_entreprises': mes_companies.count(),
            'nombre_lignes': mes_lignes.count(),
            'total_factures': total_factures,
            'montant_total': float(montant_total),
            'montant_paye': float(montant_paye),
            'montant_en_attente': float(montant_en_attente),
        },
        'factures_par_statut': factures_par_statut,
        'evolution_mensuelle': [
            {
                'mois': item['mois'].strftime('%Y-%m'),
                'nombre': item['nombre'],
                'montant': float(item['montant'] or 0)
            }
            for item in evolution_mensuelle
        ],
        'lignes_a_surveiller': lignes_a_surveiller,
        'repartition_par_entreprise': list(
            mes_companies.annotate(
                montant_total=Sum('invoices__montant_ttc'),
                nombre_lignes=Count('lines')
            ).values(
                'id', 'raison_sociale', 'compte',
                'montant_total', 'nombre_lignes'
            )
        ),
    })


# ============================================================
# STATS EMPLOYÉ
# ============================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmploye])
def stats_employe(request):
    """
    Statistiques pour un employé
    - Ma consommation
    - Historique de mes factures
    """
    
    employe = request.user
    
    # Ma ligne
    ma_ligne = Line.objects.filter(employe=employe).first()
    
    if not ma_ligne:
        return Response({
            'error': 'Aucune ligne associée à cet employé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Factures de mon entreprise
    mes_factures = Invoice.objects.filter(company=ma_ligne.company)
    
    # Statistiques globales
    total_factures = mes_factures.count()
    montant_total = mes_factures.aggregate(
        total=Sum('montant_ttc')
    )['total'] or Decimal('0')
    
    # Historique des factures (12 dernières)
    historique_factures = list(
        mes_factures
        .order_by('-date_emission')[:12]
        .values(
            'id', 'numero_facture', 'periode_debut',
            'periode_fin', 'montant_ttc', 'statut',
            'date_emission', 'date_echeance'
        )
    )
    
    # Évolution mensuelle (6 derniers mois)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    
    evolution_mensuelle = list(
        mes_factures
        .filter(date_emission__gte=start_date)
        .annotate(mois=TruncMonth('date_emission'))
        .values('mois')
        .annotate(
            montant=Sum('montant_ttc')
        )
        .order_by('mois')
    )
    
    # Mes simulations
    mes_simulations = Simulation.objects.filter(utilisateur=employe)
    
    return Response({
        'ma_ligne': {
            'msisdn': ma_ligne.msisdn,
            'utilisateur': ma_ligne.utilisateur,
            'cycle': ma_ligne.cycle,
            'forfait': float(ma_ligne.forfait),
            'entreprise': ma_ligne.company.raison_sociale,
        },
        'statistiques': {
            'total_factures': total_factures,
            'montant_total': float(montant_total),
            'moyenne_mensuelle': float(montant_total / 6) if total_factures > 0 else 0,
        },
        'evolution_mensuelle': [
            {
                'mois': item['mois'].strftime('%Y-%m'),
                'montant': float(item['montant'] or 0)
            }
            for item in evolution_mensuelle
        ],
        'historique_factures': [
            {
                **facture,
                'montant_ttc': float(facture['montant_ttc'] or 0)
            }
            for facture in historique_factures
        ],
        'simulations': {
            'total': mes_simulations.count(),
            'dernieres': list(
                mes_simulations
                .order_by('-date_simulation')[:5]
                .values(
                    'id', 'date_simulation', 'montant_estime',
                    'services_selectionnes'
                )
            )
        },
    })
