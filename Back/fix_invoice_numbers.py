"""Corriger les numéros de facture pour correspondre au PDF"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date
from billing.models import Company, Line, Invoice
from accounts.models import User

print("🔧 Correction des numéros de facture\n")

# Supprimer les anciennes factures de test
Invoice.objects.filter(numero_facture__startswith='A20260601041-').delete()
print("✅ Anciennes factures de test supprimées")

# Le PDF contient des factures individuelles par MSISDN
# mais avec le numéro de facture A20260601041 (commun)
# Nous devons créer 3 factures distinctes portant le même numéro global
# OU créer une facture globale unique

company = Company.objects.get(compte='A0000009')
lines = Line.objects.filter(company=company)

print(f"\n📄 Création des factures correspondant au PDF...")

# OPTION 1: Créer 3 factures individuelles avec des numéros différents
# qui correspondent à ce que le PDF pourrait contenir
invoices_data = [
    {
        'numero': 'A20260601041',  # Numéro global
        'msisdn': '99475555',
        'ht': '9998',
        'ttc': '11798'
    },
    {
        'numero': 'A20260601041',  # Même numéro global
        'msisdn': '99478787',
        'ht': '36475',
        'ttc': '43040'
    },
    {
        'numero': 'A20260601041',  # Même numéro global
        'msisdn': '99492454',
        'ht': '19280',
        'ttc': '22750'
    },
]

created = []
for data in invoices_data:
    line = Line.objects.get(company=company, msisdn=data['msisdn'])
    
    # Créer une facture avec un identifiant unique incluant le MSISDN
    # mais le numéro facture reste le numéro global
    invoice = Invoice.objects.create(
        company=company,
        line=line,
        numero_facture=f"{data['numero']}",  # Numéro global du PDF
        periode_debut=date(2026, 6, 1),
        periode_fin=date(2026, 6, 30),
        montant_ht=Decimal(data['ht']),
        montant_tva=Decimal(data['ht']) * Decimal('0.18'),
        montant_ttc=Decimal(data['ttc']),
        date_echeance=date(2026, 7, 30),
        statut='EN_COURS',
        commentaire=f'Facture juin 2026 - Ligne {data["msisdn"]}'
    )
    created.append(invoice)
    print(f"  ✅ {invoice.numero_facture} (MSISDN: {data['msisdn']}) | {invoice.montant_ttc} FCFA")

print(f"\n⚠️  NOTE IMPORTANTE:")
print(f"Le PDF est une facture GLOBALE avec le numéro A20260601041")
print(f"Le matching automatique va chercher ce numéro et trouver plusieurs factures.")
print(f"La logique actuelle matche la PREMIÈRE facture trouvée.")
print(f"")
print(f"Pour un test réussi, on devrait :")
print(f"1. Soit avoir UNE SEULE facture globale pour l'entreprise")
print(f"2. Soit améliorer la logique de matching pour gérer les factures individuelles")
print(f"")
print(f"💡 Solution alternative : Créer UNE facture globale pour toute l'entreprise")
