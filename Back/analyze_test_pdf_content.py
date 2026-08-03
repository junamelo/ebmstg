"""Analyser le contenu des PDFs de test"""
import PyPDF2
import sys

pdf_path = r"C:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Contexte\testPDF\PHYS.OPN.202606.GLO-1-70.pdf"

try:
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        print(f"📄 Fichier: PHYS.OPN.202606.GLO-1-70.pdf")
        print(f"📊 Nombre de pages: {len(reader.pages)}")
        print(f"\n📝 Contenu de la première page (premiers 2000 caractères):\n")
        
        page = reader.pages[0]
        text = page.extract_text()
        print(text[:2000])
        
        print(f"\n\n🔍 Recherche de MSISDN, numéro de facture, compte...")
        lines = text.split('\n')
        for i, line in enumerate(lines[:50]):
            if any(keyword in line.upper() for keyword in ['MSISDN', 'FACTURE', 'COMPTE', 'NUMERO', 'NUMÉRO']):
                print(f"  Ligne {i}: {line.strip()}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)
