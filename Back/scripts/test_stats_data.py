"""
Test simple pour vérifier que les stats peuvent accéder aux données
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Company, Line, Invoice, Publication
from accounts.models import User
from django.db.models import Count, Sum

print("🔍 VÉRIFICATION DE L'ACCÈS AUX DONNÉES POUR LES STATS\n")
print("="*70)

# Test 1 : Données de base
print("1. DONNÉES DE BASE")
print("-"*70)
total_companies = Company.objects.count()
total_lines = Line.objects.count()
total_invoices = Invoice.objects.count()
total_publications = Publication.objects.count()

print(f"✅ Entreprises      : {total_companies}")
print(f"✅ Lignes           : {total_lines}")
print(f"✅ Factures         : {total_invoices}")
print(f"✅ Publications     : {total_publications}")
print()

# Test 2 : Agrégations
print("2. AGRÉGATIONS")
print("-"*70)
factures_par_statut = dict(
    Invoice.objects.values('statut')
    .annotate(count=Count('id'))
    .values_list('statut', 'count')
)
print(f"✅ Factures par statut : {factures_par_statut}")

montant_total = Invoice.objects.aggregate(total=Sum('montant_ttc'))['total'] or 0
print(f"✅ Montant total       : {float(montant_total):,.2f} FCFA")
print()

# Test 3 : Top entreprises
print("3. TOP 5 ENTREPRISES")
print("-"*70)
top_companies = list(
    Company.objects
    .annotate(
        total_facture=Sum('invoices__montant_ttc'),
        nombre_factures=Count('invoices')
    )
    .filter(total_facture__isnull=False)
    .order_by('-total_facture')[:5]
    .values('compte', 'raison_sociale', 'total_facture', 'nombre_factures')
)

if top_companies:
    for company in top_companies:
        print(f"✅ {company['raison_sociale'][:30]:30} | {company['compte']:10} | {float(company['total_facture'] or 0):>12,.0f} FCFA | {company['nombre_factures']:2} factures")
else:
    print("⚠️  Aucune entreprise avec factures")
print()

# Test 4 : Utilisateurs par rôle
print("4. UTILISATEURS PAR RÔLE")
print("-"*70)
for role in ['ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION', 'PAYEUR', 'EMPLOYE']:
    count = User.objects.filter(role=role).count()
    if count > 0:
        print(f"✅ {role:20} : {count} utilisateur(s)")
    else:
        print(f"⚠️  {role:20} : Aucun utilisateur")
print()

# Test 5 : Publications par agent
print("5. PUBLICATIONS PAR AGENT")
print("-"*70)
agents = User.objects.filter(role='AGENT_FACTURATION')
if agents.exists():
    for agent in agents:
        nb_pubs = Publication.objects.filter(agent=agent).count()
        print(f"✅ {agent.email:30} : {nb_pubs} publication(s)")
else:
    print("⚠️  Aucun agent de facturation trouvé")
print()

# Résumé
print("="*70)
print("RÉSUMÉ")
print("="*70)

if total_invoices > 0 and total_companies > 0:
    print("✅ La base de données est bien liée et contient des données")
    print("✅ Les endpoints de stats peuvent fonctionner")
    print()
    print("🎯 PROCHAINE ÉTAPE : Tester les endpoints via le serveur Django")
    print("   1. Démarrer le serveur : python manage.py runserver")
    print("   2. Tester avec curl ou Postman")
elif total_invoices == 0:
    print("⚠️  La base contient des entreprises mais pas de factures")
    print("   Les stats de facturation seront vides")
else:
    print("⚠️  La base de données est vide")
    print("   Créer des données de test d'abord")

print("="*70)
