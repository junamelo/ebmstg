"""Vérifier si les données en base correspondent aux données du PDF"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Company, Line, Invoice

# MSISDNs extraits du PDF SOM
pdf_msisdns = [
    '99475555', '99478787', '99492454',  # CAFE INFORMATIQUE
    '99421137', '99421146', '99426714', '99520226',  # CAURIS MANAGEMENT
    '97525353', '99672121',  # LABOREX TOGO
    '99453100',  # CFAO MOBILITY
    '99476053',  # VIVI ROYALE
    '79300739', '79300742', '79300744', '79300746', '79302368', 
    '79302369', '79302370', '79603053', '79603054'  # WACEM SA (9 lignes)
]

print("🔍 VÉRIFICATION DES DONNÉES\n")
print(f"📊 Total MSISDNs dans le PDF : {len(pdf_msisdns)}")
print(f"📊 Total lignes en base : {Line.objects.count()}")
print(f"📊 Total factures EN_COURS : {Invoice.objects.filter(statut='EN_COURS').count()}\n")

print("="*70)
print("VÉRIFICATION MSISDN PAR MSISDN :")
print("="*70)

missing_lines = []
existing_lines = []
missing_invoices = []
existing_invoices = []

for msisdn in pdf_msisdns:
    # Vérifier si la ligne existe
    line = Line.objects.filter(msisdn=msisdn).first()
    
    if line:
        existing_lines.append(msisdn)
        print(f"✅ {msisdn} : Ligne existe - {line.company.raison_sociale}")
        
        # Vérifier si une facture existe pour cette ligne
        invoice = Invoice.objects.filter(
            company__lines__msisdn=msisdn,
            statut='EN_COURS'
        ).first()
        
        if invoice:
            existing_invoices.append(msisdn)
            print(f"   ✅ Facture : {invoice.numero_facture}")
        else:
            missing_invoices.append(msisdn)
            print(f"   ❌ Aucune facture EN_COURS pour ce MSISDN")
    else:
        missing_lines.append(msisdn)
        print(f"❌ {msisdn} : LIGNE N'EXISTE PAS EN BASE")

print("\n" + "="*70)
print("RÉSUMÉ :")
print("="*70)
print(f"✅ Lignes existantes : {len(existing_lines)}/{len(pdf_msisdns)}")
print(f"❌ Lignes manquantes : {len(missing_lines)}/{len(pdf_msisdns)}")
print(f"✅ Factures matchables : {len(existing_invoices)}/{len(pdf_msisdns)}")
print(f"❌ Factures manquantes : {len(missing_invoices)}/{len(pdf_msisdns)}")

if missing_lines:
    print(f"\n⚠️  MSISDNs manquants en base :")
    for msisdn in missing_lines:
        print(f"   - {msisdn}")

if missing_invoices:
    print(f"\n⚠️  MSISDNs sans facture EN_COURS :")
    for msisdn in missing_invoices:
        print(f"   - {msisdn}")

print("\n" + "="*70)
if len(existing_lines) == len(pdf_msisdns) and len(existing_invoices) == len(pdf_msisdns):
    print("🎯 PARFAIT ! Toutes les données correspondent. Le matching devrait fonctionner.")
else:
    print("⚠️  ATTENTION : Des données manquent. Le script create_test_invoices_from_pdf.py")
    print("   doit créer les lignes ET les factures pour correspondre au PDF.")
