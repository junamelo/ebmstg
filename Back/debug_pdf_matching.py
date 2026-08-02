"""
Script de diagnostic pour comprendre pourquoi le matching échoue
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.models import Company, Line, Invoice
from billing.services.pdf_processor import PDFProcessor

# Chemin du PDF
TEST_PDF_PATH = r"C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Contexte\testPDF\PHYS.OPN.202606.SOM-1-20.pdf"

def debug_matching():
    """Déboguer le matching"""
    
    print("="*80)
    print("🔍 DIAGNOSTIC DU MATCHING PDF")
    print("="*80)
    
    # 1. Analyser le PDF
    print("\n📄 Analyse du PDF...\n")
    with open(TEST_PDF_PATH, 'rb') as pdf_file:
        result = PDFProcessor.process_bulk_pdf(pdf_file)
    
    print(f"✅ PDF analysé : {result['total_blocks']} blocs détectés\n")
    
    # 2. Afficher ce qui est en base
    print("="*80)
    print("📊 DONNÉES EN BASE")
    print("="*80)
    
    companies = Company.objects.all()
    print(f"\n✅ {companies.count()} entreprise(s) :\n")
    for company in companies:
        print(f"   🏢 {company.compte} - {company.raison_sociale}")
        lines = company.lines.all()
        print(f"      📞 {lines.count()} ligne(s):")
        for line in lines:
            print(f"         • {line.msisdn} - {line.utilisateur}")
    
    invoices = Invoice.objects.all()
    print(f"\n✅ {invoices.count()} facture(s) :\n")
    for invoice in invoices:
        print(f"   📄 {invoice.numero_facture} - {invoice.company.raison_sociale} ({invoice.company.compte}) - Statut: {invoice.statut}")
    
    # 3. Tester le matching
    print("\n" + "="*80)
    print("🔗 TEST DE MATCHING")
    print("="*80)
    
    for idx, file_info in enumerate(result['files'][:5], 1):  # Tester les 5 premiers
        identifiers = file_info['identifiers']
        print(f"\n📦 Bloc {idx}: {file_info['filename']}")
        print(f"   Identifiants détectés :")
        for key, value in identifiers.items():
            print(f"      • {key}: {value}")
        
        # Tester le matching
        from billing.services.pdf_processor import PDFMatcher
        invoice = PDFMatcher.match_pdf_to_invoice(identifiers, Invoice.objects.all())
        
        if invoice:
            print(f"   ✅ MATCH TROUVÉ : {invoice.numero_facture} - {invoice.company.raison_sociale}")
        else:
            print(f"   ❌ AUCUN MATCH")
            
            # Essayer de comprendre pourquoi
            if 'numero_facture' in identifiers:
                print(f"      ❓ Recherche par numéro : {identifiers['numero_facture']}")
                if not Invoice.objects.filter(numero_facture=identifiers['numero_facture']).exists():
                    print(f"         ❌ Aucune facture avec ce numéro en base")
            
            if 'compte' in identifiers:
                print(f"      ❓ Recherche par compte : {identifiers['compte']}")
                if Company.objects.filter(compte=identifiers['compte']).exists():
                    company = Company.objects.get(compte=identifiers['compte'])
                    invoices_for_company = Invoice.objects.filter(company=company)
                    print(f"         ✅ Entreprise trouvée : {company.raison_sociale}")
                    print(f"         ✅ {invoices_for_company.count()} facture(s) pour cette entreprise :")
                    for inv in invoices_for_company:
                        print(f"            • {inv.numero_facture}")
                else:
                    print(f"         ❌ Aucune entreprise avec ce compte en base")
            
            if 'msisdn' in identifiers:
                print(f"      ❓ Recherche par MSISDN : {identifiers['msisdn']}")
                if Line.objects.filter(msisdn=identifiers['msisdn']).exists():
                    line = Line.objects.get(msisdn=identifiers['msisdn'])
                    print(f"         ✅ Ligne trouvée : {line.utilisateur} (Entreprise: {line.company.raison_sociale})")
                    invoices_for_line = Invoice.objects.filter(company=line.company)
                    print(f"         ✅ {invoices_for_line.count()} facture(s) pour cette entreprise :")
                    for inv in invoices_for_line:
                        print(f"            • {inv.numero_facture}")
                else:
                    print(f"         ❌ Aucune ligne avec ce MSISDN en base")
    
    print("\n" + "="*80)
    print("✅ Diagnostic terminé")
    print("="*80)

if __name__ == "__main__":
    debug_matching()
