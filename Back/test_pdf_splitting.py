"""
Script de test pour le découpage des PDF Moov
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from billing.services.pdf_processor import PDFProcessor

# Chemins des PDF de test
TEST_PDF_DIR = r"C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Contexte\testPDF"

def test_pdf_splitting(pdf_filename):
    """Tester le découpage d'un PDF"""
    pdf_path = os.path.join(TEST_PDF_DIR, pdf_filename)
    
    if not os.path.exists(pdf_path):
        print(f"❌ Fichier non trouvé: {pdf_path}")
        return
    
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {pdf_filename}")
    print(f"{'='*80}\n")
    
    # 1. Analyser la structure
    print("📊 Étape 1: Analyse de la structure...")
    with open(pdf_path, 'rb') as pdf_file:
        blocks = PDFProcessor.analyze_pdf_structure(pdf_file)
    
    print(f"✅ {len(blocks)} bloc(s) détecté(s)\n")
    
    # Afficher détails des blocs
    for idx, block in enumerate(blocks, 1):
        print(f"📦 BLOC {idx}:")
        print(f"   Pages: {block['start_page']+1} à {block['end_page']+1} ({len(block['pages'])} page(s))")
        print(f"   Identifiants:")
        for key, value in block['identifiers'].items():
            print(f"      - {key}: {value}")
        print()
    
    # 2. Découper le PDF
    print("✂️  Étape 2: Découpage du PDF...")
    with open(pdf_path, 'rb') as pdf_file:
        result = PDFProcessor.process_bulk_pdf(pdf_file)
    
    if result['success']:
        print(f"✅ Découpage réussi!")
        print(f"   Total pages: {result['total_pages']}")
        print(f"   Fichiers créés: {result['files_created']}\n")
        
        print("📄 Fichiers générés:")
        for file_info in result['files'][:5]:  # Afficher les 5 premiers
            print(f"   - {file_info['filename']} ({file_info['pages']} page(s))")
            for key, value in file_info['identifiers'].items():
                print(f"     • {key}: {value}")
        
        if len(result['files']) > 5:
            print(f"   ... et {len(result['files']) - 5} autre(s) fichier(s)")
    else:
        print("❌ Erreur lors du découpage")
    
    print(f"\n{'='*80}\n")

def main():
    """Fonction principale"""
    print("🧪 TEST DU SYSTÈME DE DÉCOUPAGE PDF MOOV")
    print("="*80)
    
    # Tester les 2 PDF
    test_files = [
        "PHYS.OPN.202606.GLO-1-30.pdf",  # Facture globale
        "PHYS.OPN.202606.SOM-1-20.pdf"   # Factures individuelles
    ]
    
    for pdf_file in test_files:
        try:
            test_pdf_splitting(pdf_file)
        except Exception as e:
            print(f"❌ ERREUR: {e}")
            import traceback
            traceback.print_exc()
    
    print("✅ Tests terminés")

if __name__ == "__main__":
    main()
