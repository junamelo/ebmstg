#!/usr/bin/env python3
"""
Script pour créer un PDF de test pour tester le découpage automatique
"""
import os
import sys
from io import BytesIO

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
sys.path.append('.')

import django
django.setup()

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab non installé. Utilisation d'un PDF alternatif.")

def create_test_pdf_with_reportlab():
    """Créer un PDF de test avec ReportLab"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Simuler 3 clients différents
    clients = [
        {
            'msisdn': '90123456',
            'compte': 'C26TEST001',
            'nom': 'ENTREPRISE ALPHA SARL',
            'facture': 'FAC-C26TEST001-202607-001'
        },
        {
            'msisdn': '93456789',
            'compte': 'C26TEST002',
            'nom': 'BETA CORPORATION',
            'facture': 'FAC-C26TEST002-202607-001'
        },
        {
            'msisdn': '96789012',
            'compte': 'C26TEST003',
            'nom': 'GAMMA TECHNOLOGIES',
            'facture': 'FAC-C26TEST003-202607-001'
        }
    ]
    
    for i, client in enumerate(clients):
        # Page de facture pour chaque client
        story.append(Paragraph("MOOV AFRICA TOGO", styles['Title']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph(f"FACTURE N° {client['facture']}", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph(f"Client : {client['nom']}", styles['Normal']))
        story.append(Paragraph(f"Compte : {client['compte']}", styles['Normal']))
        story.append(Paragraph(f"Ligne principale : {client['msisdn']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Détail de facturation :", styles['Heading2']))
        story.append(Paragraph(f"Forfait mensuel : 25 000 FCFA", styles['Normal']))
        story.append(Paragraph(f"Consommation DATA : 2.5 GB", styles['Normal']))
        story.append(Paragraph(f"Appels voix : 120 minutes", styles['Normal']))
        story.append(Paragraph(f"SMS envoyés : 45", styles['Normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Montant TTC : 29 500 FCFA", styles['Heading2']))
        story.append(Spacer(1, 24))
        
        # Saut de page sauf pour le dernier
        if i < len(clients) - 1:
            from reportlab.platypus import PageBreak
            story.append(PageBreak())
    
    doc.build(story)
    return buffer.getvalue()

def create_simple_test_pdf():
    """Créer un PDF simple avec PyPDF2"""
    from PyPDF2 import PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    
    buffer = BytesIO()
    
    # Créer une page simple avec canvas
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Client 1
    c.drawString(100, 750, "MOOV AFRICA TOGO")
    c.drawString(100, 720, "FACTURE N° FAC-C26TEST001-202607-001")
    c.drawString(100, 690, "Client : ENTREPRISE ALPHA SARL")
    c.drawString(100, 660, "Compte : C26TEST001")
    c.drawString(100, 630, "Ligne principale : 90123456")
    c.drawString(100, 600, "Montant TTC : 29 500 FCFA")
    c.showPage()
    
    # Client 2
    c.drawString(100, 750, "MOOV AFRICA TOGO")
    c.drawString(100, 720, "FACTURE N° FAC-C26TEST002-202607-001")
    c.drawString(100, 690, "Client : BETA CORPORATION")
    c.drawString(100, 660, "Compte : C26TEST002")
    c.drawString(100, 630, "Ligne principale : 93456789")
    c.drawString(100, 600, "Montant TTC : 35 000 FCFA")
    c.showPage()
    
    # Client 3
    c.drawString(100, 750, "MOOV AFRICA TOGO")
    c.drawString(100, 720, "FACTURE N° FAC-C26TEST003-202607-001")
    c.drawString(100, 690, "Client : GAMMA TECHNOLOGIES")
    c.drawString(100, 660, "Compte : C26TEST003")
    c.drawString(100, 630, "Ligne principale : 96789012")
    c.drawString(100, 600, "Montant TTC : 42 000 FCFA")
    
    c.save()
    return buffer.getvalue()

def main():
    """Créer le PDF de test"""
    print("🔧 Création d'un PDF de test pour le découpage...")
    
    # Créer le PDF
    if REPORTLAB_AVAILABLE:
        pdf_content = create_test_pdf_with_reportlab()
        print("✅ PDF créé avec ReportLab (3 clients, format professionnel)")
    else:
        pdf_content = create_simple_test_pdf()
        print("✅ PDF créé avec canvas simple (3 clients)")
    
    # Sauvegarder
    output_path = "media/test_bulk_moov.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'wb') as f:
        f.write(pdf_content)
    
    print(f"📄 PDF de test sauvegardé : {output_path}")
    print("📊 Contenu :")
    print("   - 3 clients (ALPHA, BETA, GAMMA)")
    print("   - MSISDNs : 90123456, 93456789, 96789012")
    print("   - Comptes : C26TEST001, C26TEST002, C26TEST003")
    print("   - Numéros facture : FAC-C26TEST001-202607-001, etc.")
    print("\n🚀 Maintenant tu peux tester l'endpoint :")
    print("   POST /api/billing/invoices/upload_bulk_pdf/")
    print(f"   fichier: {output_path}")

if __name__ == "__main__":
    main()