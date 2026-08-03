"""Créer UNE facture globale correspondant au PDF"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date
from billing.models import Company, Line, Invoice

print("📄 Création d'une facture GLOBALE pour le test manuel\n")

# Nettoyer les anciennes factures de test
Invoice.objects.filter(numero_facture__startswith='A20260601041').delete()
print("✅ Anciennes factures de test supprimées")

company = Company.objects.get(compte='A0000009')

# Créer UNE facture globale pour toute l'entreprise
# (correspondant au PDF PHYS.OPN.202606.GLO-1-70.pdf)
invoice = Invoice.objects.create(
    company=company,
    line=None,  # Pas de ligne spécifique = facture globale
    numero_facture='A20260601041',  # Numéro exact du PDF
    periode_debut=date(2026, 6, 1),
    periode_fin=date(2026, 6, 30),
    montant_ht=Decimal('65753'),  # Total des 3 lignes
    montant_tva=Decimal('11835'),  # Total TVA
    montant_ttc=Decimal('77588'),  # Total TTC (comme dans le PDF)
    date_echeance=date(2026, 7, 30),
    statut='EN_COURS',
    commentaire='Facture globale juin 2026 - Test manuel Phase 4'
)

print(f"\n✅ Facture globale créée:")
print(f"   Numéro: {invoice.numero_facture}")
print(f"   Entreprise: {company.raison_sociale} ({company.compte})")
print(f"   Montant TTC: {invoice.montant_ttc} FCFA")
print(f"   Statut: {invoice.statut}")
print(f"   Type: Facture GLOBALE (line=None)")
print(f"\n📂 Cette facture correspond au PDF:")
print(f"   PHYS.OPN.202606.GLO-1-70.pdf")
print(f"\n🔍 Le matching automatique devrait maintenant fonctionner:")
print(f"   - Le PDF contient le numéro A20260601041")
print(f"   - La facture EN_COURS a le même numéro")
print(f"   - Le PDF contient le compte A0000009")
print(f"   - La facture appartient à l'entreprise A0000009")
print(f"\n⚠️  Après upload, la facture devrait passer:")
print(f"   EN_COURS → VALIDEE (pas PUBLIEE)")
