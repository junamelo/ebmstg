"""Corriger les données de test"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date
from billing.models import Line, Invoice
from accounts.models import User

print("🔧 Correction des données de test\n")

# Associer les employés aux lignes
employees_mapping = {
    '99475555': 'marie.noagbodji',
    '99478787': 'jean.noagbodji',
    '99492454': 'secretariat.tech',
}

for msisdn, username in employees_mapping.items():
    line = Line.objects.get(msisdn=msisdn)
    employe = User.objects.get(username=username)
    line.employe = employe
    line.save()
    print(f"✅ Ligne {msisdn} → Employé {username}")

# Mettre à jour les montants des factures
invoices_data = {
    'A20260601041-99475555': {'ht': '9998', 'ttc': '11798'},
    'A20260601041-99478787': {'ht': '36475', 'ttc': '43040'},
    'A20260601041-99492454': {'ht': '19280', 'ttc': '22750'},
}

print(f"\n💰 Mise à jour des montants des factures...")
for numero, montants in invoices_data.items():
    invoice = Invoice.objects.get(numero_facture=numero)
    invoice.montant_ht = Decimal(montants['ht'])
    invoice.montant_tva = Decimal(montants['ht']) * Decimal('0.18')
    invoice.montant_ttc = Decimal(montants['ttc'])
    invoice.save()
    print(f"✅ {numero}: {invoice.montant_ttc} FCFA")

print(f"\n✅ Données corrigées !")
