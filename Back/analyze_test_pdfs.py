"""
Script pour analyser les PDF de test et comprendre leur structure
"""
import os
import sys

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ PyPDF2 non installé. Installer avec: pip install PyPDF2")
    sys.exit(1)

# Chemin vers les PDF de test
TEST_PDF_DIR = r"C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Contexte\testPDF"

def analyze_pdf(filepath):
    """Analyser un fichier PDF"""
    print(f"\n{'='*80}")
    print(f"Fichier: {os.path.basename(filepath)}")
    print(f"{'='*80}")
    
    reader = PdfReader(filepath)
    total_pages = len(reader.pages)
    print(f"📄 Nombre total de pages: {total_pages}")
    
    # Analyser les 3 premières pages
    for i in range(min(3, total_pages)):
        print(f"\n--- PAGE {i+1} ---")
        page = reader.pages[i]
        text = page.extract_text()
        
        # Afficher les premiers 800 caractères
        preview = text[:800] if len(text) > 800 else text
        print(preview)
        
        # Chercher des patterns
        import re
        
        # MSISDNs
        msisdns = re.findall(r'\b(9[0-9]{7})\b', text)
        if msisdns:
            print(f"\n📞 MSISDNs trouvés: {msisdns[:5]}")  # Afficher les 5 premiers
        
        # Comptes
        comptes = re.findall(r'\b(C26[A-Z0-9]{6,10}|A[0-9]{7})\b', text)
        if comptes:
            print(f"🏢 Comptes trouvés: {comptes[:5]}")
        
        # Numéros de facture
        factures = re.findall(r'\b(FAC-[A-Z0-9\-]+|FACTURE[:\s]+[A-Z0-9\-]+)\b', text)
        if factures:
            print(f"📑 Factures trouvées: {factures[:3]}")
        
        print(f"\n📊 Longueur texte: {len(text)} caractères")
        print("-" * 80)
    
    return reader, total_pages

def main():
    """Fonction principale"""
    print("🔍 Analyse des PDF de test Moov Africa")
    print(f"📁 Répertoire: {TEST_PDF_DIR}\n")
    
    if not os.path.exists(TEST_PDF_DIR):
        print(f"❌ Erreur: Le répertoire n'existe pas: {TEST_PDF_DIR}")
        return
    
    # Lister les PDF
    pdf_files = [f for f in os.listdir(TEST_PDF_DIR) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ Aucun fichier PDF trouvé dans {TEST_PDF_DIR}")
        return
    
    print(f"✅ {len(pdf_files)} fichier(s) PDF trouvé(s):\n")
    for pdf_file in pdf_files:
        filepath = os.path.join(TEST_PDF_DIR, pdf_file)
        try:
            analyze_pdf(filepath)
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse de {pdf_file}: {e}")
    
    print(f"\n{'='*80}")
    print("✅ Analyse terminée")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
