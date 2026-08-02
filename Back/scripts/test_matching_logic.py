"""Tester la nouvelle logique de matching"""
import os, sys, django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Invoice
from billing.services.pdf_processor import PDFMatcher

# Test avec quelques MSISDNs
test_cases = [
    {'msisdn': '99475555', 'compte': 'A0000009'},  # CAFE INFORMATIQUE
    {'msisdn': '99478787', 'compte': 'A0000009'},  # CAFE INFORMATIQUE
    {'msisdn': '79300739', 'compte': 'A0000106'},  # WACEM SA
    {'msisdn': '79603054', 'compte': 'A0000106'},  # WACEM SA
]

print("🧪 TEST DE LA NOUVELLE LOGIQUE DE MATCHING\n")
print("="*70)

invoices_query = Invoice.objects.filter(statut='EN_COURS')

for identifiers in test_cases:
    msisdn = identifiers['msisdn']
    matched_invoice = PDFMatcher.match_pdf_to_invoice(identifiers, invoices_query)
    
    if matched_invoice:
        # Vérifier si le numéro de facture contient le MSISDN
        contains_msisdn = msisdn in matched_invoice.numero_facture
        status = "✅ CORRECT" if contains_msisdn else "❌ ERREUR"
        
        print(f"{status} | MSISDN: {msisdn}")
        print(f"         Facture matchée: {matched_invoice.numero_facture}")
        print(f"         Entreprise: {matched_invoice.company.raison_sociale}")
        if not contains_msisdn:
            print(f"         ⚠️  Le MSISDN '{msisdn}' ne se trouve PAS dans '{matched_invoice.numero_facture}'")
    else:
        print(f"❌ AUCUN MATCH | MSISDN: {msisdn}")
    print()

print("="*70)
print("\n💡 Si tous les matchs sont CORRECTS, le système est prêt !")
