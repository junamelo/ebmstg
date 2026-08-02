"""Vérifier les cycles des lignes"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Line, Invoice

print("🔍 VÉRIFICATION DES CYCLES\n")

# MSISDNs du PDF
test_msisdns = ['99475555', '79300739', '99421137', '97525353']

print("Cycles des lignes de test:")
for msisdn in test_msisdns:
    line = Line.objects.filter(msisdn=msisdn).first()
    if line:
        print(f"  ✅ {msisdn}: cycle={line.cycle} | Entreprise: {line.company.raison_sociale}")
    else:
        print(f"  ❌ {msisdn}: Non trouvé")

print("\n" + "="*70)
print("TOUTES LES LIGNES EN BASE:")
print("="*70)
for line in Line.objects.all()[:10]:
    print(f"{line.msisdn}: {line.cycle}")

print("\n" + "="*70)
print("TEST DU FILTRE BACKEND:")
print("="*70)

# Simuler le filtre du backend
invoices_op = Invoice.objects.filter(
    statut='EN_COURS',
    company__lines__cycle='OP'
).distinct()

invoices_hyb = Invoice.objects.filter(
    statut='EN_COURS',
    company__lines__cycle='HYB'
).distinct()

print(f"Factures EN_COURS avec cycle='OP': {invoices_op.count()}")
print(f"Factures EN_COURS avec cycle='HYB': {invoices_hyb.count()}")

print("\n💡 Le frontend envoie cycle='OP' pour le PDF SOM")
print(f"   Donc {invoices_op.count()} factures seront candidates au matching")
