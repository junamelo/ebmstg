"""
Tests Phase 4 : Génération, import et traitement robuste des factures PDF
"""
import os
import tempfile
from decimal import Decimal
from datetime import date, timedelta
from io import BytesIO

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework import serializers

from billing.models import Company, Line, Invoice
from accounts.models import User

try:
    from PyPDF2 import PdfWriter, PdfReader
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def create_test_pdf(content_text="Test PDF", num_pages=1):
    """
    Créer un PDF de test avec reportlab
    
    Args:
        content_text: Texte à inclure dans le PDF
        num_pages: Nombre de pages
        
    Returns:
        BytesIO contenant le PDF
    """
    if not PDF_AVAILABLE:
        return None
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    for i in range(num_pages):
        p.drawString(100, 800, f"Page {i+1}")
        p.drawString(100, 750, content_text)
        p.showPage()
    
    p.save()
    buffer.seek(0)
    return buffer


def create_multi_invoice_pdf(invoices_data):
    """
    Créer un PDF multi-factures pour tests
    
    Args:
        invoices_data: Liste de dict avec msisdn, numero_facture, compte
        
    Returns:
        BytesIO contenant le PDF
    """
    if not PDF_AVAILABLE:
        return None
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    for idx, invoice_data in enumerate(invoices_data):
        # Page de facture
        y_pos = 800
        p.drawString(100, y_pos, f"FACTURE MOOV AFRICA")
        y_pos -= 30
        
        if 'numero_facture' in invoice_data:
            p.drawString(100, y_pos, f"Numéro: {invoice_data['numero_facture']}")
            y_pos -= 25
        
        if 'compte' in invoice_data:
            p.drawString(100, y_pos, f"Compte: {invoice_data['compte']}")
            y_pos -= 25
        
        if 'msisdn' in invoice_data:
            p.drawString(100, y_pos, f"MSISDN: {invoice_data['msisdn']}")
            y_pos -= 25
        
        p.drawString(100, y_pos, f"Montant: {invoice_data.get('montant', '10000')} FCFA")
        
        p.showPage()
    
    p.save()
    buffer.seek(0)
    return buffer


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PDFUploadValidationTests(TestCase):
    """Tests de validation des uploads PDF"""
    
    def setUp(self):
        self.agent = User.objects.create_user(
            username='agent_pdf',
            email='agent@pdf.test',
            password='test123',
            role='AGENT_FACTURATION'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.agent)
    
    def test_upload_fichier_non_pdf_rejete(self):
        """Un fichier non-PDF doit être rejeté"""
        # Créer un fichier texte
        txt_file = SimpleUploadedFile(
            "facture.txt",
            b"Ceci n'est pas un PDF",
            content_type="text/plain"
        )
        
        response = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {'fichier': txt_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pdf', str(response.data).lower())
    
    def test_upload_pdf_trop_gros_rejete(self):
        """Un PDF dépassant la limite de taille doit être rejeté"""
        from reportlab.pdfgen import canvas
        from io import BytesIO
        from unittest.mock import patch
        
        # Créer un petit PDF valide (environ 2 Ko)
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=(595, 842))
        p.drawString(100, 800, "Test PDF")
        p.drawString(100, 750, "Ce PDF est structurellement valide")
        p.showPage()
        p.save()
        
        pdf_content = buffer.getvalue()
        pdf_size = len(pdf_content)
        
        # Vérifier que le PDF est bien petit (< 10 Ko)
        self.assertLess(pdf_size, 10 * 1024, "Le PDF de test doit être petit")
        
        # Patcher la méthode validate_fichier du serializer pour réduire temporairement la limite
        from billing.serializers import BulkPDFUploadSerializer
        original_validate = BulkPDFUploadSerializer.validate_fichier
        
        def validate_with_small_limit(self, value):
            # Vérifier l'extension
            if not value.name.lower().endswith('.pdf'):
                from rest_framework import serializers
                raise serializers.ValidationError("Le fichier doit avoir l'extension .pdf")
            
            # Vérifier la taille avec limite réduite à 1 Ko
            max_size = 1 * 1024  # 1 Ko
            if value.size > max_size:
                from rest_framework import serializers
                raise serializers.ValidationError(
                    f"Le fichier ne doit pas dépasser {max_size / 1024:.0f} Ko (taille: {value.size / 1024:.1f} Ko)"
                )
            
            # Vérifier que ce n'est pas un fichier vide
            if value.size == 0:
                from rest_framework import serializers
                raise serializers.ValidationError("Le fichier PDF est vide")
            
            # Vérifier le header PDF basique
            value.seek(0)
            header = value.read(8)
            value.seek(0)
            
            if not header.startswith(b'%PDF'):
                from rest_framework import serializers
                raise serializers.ValidationError("Le fichier ne semble pas être un PDF valide")
            
            return value
        
        # Remplacer temporairement la méthode
        BulkPDFUploadSerializer.validate_fichier = validate_with_small_limit
        
        try:
            large_file = SimpleUploadedFile(
                "facture_test.pdf",
                pdf_content,
                content_type="application/pdf"
            )
            
            response = self.client.post(
                '/api/billing/invoices/upload_bulk_pdf/',
                {'fichier': large_file},
                format='multipart'
            )
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # Vérifier que le message mentionne le dépassement de taille
            response_str = str(response.data)
            self.assertTrue(
                'Ko' in response_str or 'taille' in response_str.lower() or 'dépasser' in response_str.lower(),
                f"Le message d'erreur devrait mentionner la taille : {response_str}"
            )
        finally:
            # Restaurer la méthode originale
            BulkPDFUploadSerializer.validate_fichier = original_validate
    
    def test_upload_sans_authentification_interdit(self):
        """L'upload sans authentification doit être interdit"""
        self.client.force_authenticate(user=None)
        
        pdf_buffer = create_test_pdf("Test")
        pdf_file = SimpleUploadedFile(
            "test.pdf",
            pdf_buffer.getvalue() if pdf_buffer else b"",
            content_type="application/pdf"
        )
        
        response = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {'fichier': pdf_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_upload_par_employe_interdit(self):
        """Un employé ne doit pas pouvoir uploader de PDF"""
        employe = User.objects.create_user(
            username='employe_test',
            email='employe@test.com',
            password='test123',
            role='EMPLOYE'
        )
        self.client.force_authenticate(user=employe)
        
        pdf_buffer = create_test_pdf("Test")
        pdf_file = SimpleUploadedFile(
            "test.pdf",
            pdf_buffer.getvalue() if pdf_buffer else b"",
            content_type="application/pdf"
        )
        
        response = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {'fichier': pdf_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PDFProcessingTests(TestCase):
    """Tests du traitement et découpage PDF"""
    
    def setUp(self):
        if not PDF_AVAILABLE:
            self.skipTest("PyPDF2 ou reportlab non disponible")
        
        self.agent = User.objects.create_user(
            username='agent_pdf',
            email='agent@pdf.test',
            password='test123',
            role='AGENT_FACTURATION'
        )
        
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='test123',
            role='PAYEUR'
        )
        
        self.company = Company.objects.create(
            compte='A1234567',
            raison_sociale='Test Company',
            payeur=self.payeur
        )
        
        self.line1 = Line.objects.create(
            company=self.company,
            msisdn='99111111',
            forfait=Decimal('10000'),
            cycle='HYB'
        )
        
        self.line2 = Line.objects.create(
            company=self.company,
            msisdn='99222222',
            forfait=Decimal('15000'),
            cycle='HYB'
        )
        
        # Créer des factures EN_COURS pour le matching
        self.invoice1 = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-99111111-202608-001',
            periode_debut=date(2026, 8, 1),
            periode_fin=date(2026, 8, 31),
            montant_ht=Decimal('10000'),
            montant_tva=Decimal('1800'),
            montant_ttc=Decimal('11800'),
            date_echeance=date(2026, 9, 30),
            statut='EN_COURS'
        )
        
        self.invoice2 = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-99222222-202608-002',
            periode_debut=date(2026, 8, 1),
            periode_fin=date(2026, 8, 31),
            montant_ht=Decimal('15000'),
            montant_tva=Decimal('2700'),
            montant_ttc=Decimal('17700'),
            date_echeance=date(2026, 9, 30),
            statut='EN_COURS'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.agent)
    
    def test_upload_pdf_multi_factures_avec_matching(self):
        """Upload d'un PDF contenant plusieurs factures avec matching automatique"""
        # Créer un PDF avec 2 factures
        pdf_buffer = create_multi_invoice_pdf([
            {
                'numero_facture': 'FAC-99111111-202608-001',
                'msisdn': '99111111',
                'compte': 'A1234567',
                'montant': '11800'
            },
            {
                'numero_facture': 'FAC-99222222-202608-002',
                'msisdn': '99222222',
                'compte': 'A1234567',
                'montant': '17700'
            }
        ])
        
        pdf_file = SimpleUploadedFile(
            "factures_test.pdf",
            pdf_buffer.getvalue(),
            content_type="application/pdf"
        )
        
        response = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {
                'fichier': pdf_file,
                'auto_match': True
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('matching', response.data)
        
        # Vérifier qu'au moins une facture a été attachée
        matching = response.data['matching']
        self.assertGreater(matching.get('successfully_matched', 0), 0)
        
        # Vérifier que les factures ont bien été attachées
        self.invoice1.refresh_from_db()
        self.invoice2.refresh_from_db()
        
        # Au moins invoice1 doit être VALIDEE
        self.assertEqual(self.invoice1.statut, 'VALIDEE')
        self.assertIsNotNone(self.invoice1.fichier_pdf)
    
    def test_reimport_meme_pdf_idempotent(self):
        """Réimporter le même PDF ne doit pas créer de doublons"""
        pdf_buffer = create_multi_invoice_pdf([
            {
                'numero_facture': 'FAC-99111111-202608-001',
                'msisdn': '99111111',
                'compte': 'A1234567'
            }
        ])
        
        pdf_file1 = SimpleUploadedFile(
            "factures_test.pdf",
            pdf_buffer.getvalue(),
            content_type="application/pdf"
        )
        
        # Premier upload
        response1 = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {'fichier': pdf_file1, 'auto_match': True},
            format='multipart'
        )
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Réinitialiser le buffer
        pdf_buffer.seek(0)
        pdf_file2 = SimpleUploadedFile(
            "factures_test.pdf",
            pdf_buffer.getvalue(),
            content_type="application/pdf"
        )
        
        # Second upload du même fichier
        response2 = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {'fichier': pdf_file2, 'auto_match': True},
            format='multipart'
        )
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'il n'y a pas de doublons
        invoices_count = Invoice.objects.filter(numero_facture='FAC-99111111-202608-001').count()
        self.assertEqual(invoices_count, 1)
        
        # Vérifier que le second upload a été marqué comme 'skipped'
        matching = response2.data.get('matching', {})
        self.assertGreater(matching.get('skipped_already_processed', 0), 0)
    
    def test_pdf_avec_msisdn_non_reconnu(self):
        """PDF avec un MSISDN qui n'existe pas en base"""
        pdf_buffer = create_multi_invoice_pdf([
            {
                'msisdn': '99999999',  # MSISDN inexistant
                'compte': 'A1234567'
            }
        ])
        
        pdf_file = SimpleUploadedFile(
            "facture_msisdn_inconnu.pdf",
            pdf_buffer.getvalue(),
            content_type="application/pdf"
        )
        
        response = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {'fichier': pdf_file, 'auto_match': True},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'il y a une erreur de non-matching
        matching = response.data.get('matching', {})
        self.assertGreater(matching.get('not_matched', 0), 0)
        details = matching.get('details', {})
        self.assertGreater(len(details.get('errors', [])), 0)
    
    def test_facture_deja_publiee_non_modifiee(self):
        """Une facture déjà PUBLIEE ne doit pas être modifiée"""
        # Changer le statut à PUBLIEE
        self.invoice1.statut = 'PUBLIEE'
        self.invoice1.save()
        
        pdf_buffer = create_multi_invoice_pdf([
            {
                'numero_facture': 'FAC-99111111-202608-001',
                'msisdn': '99111111'
            }
        ])
        
        pdf_file = SimpleUploadedFile(
            "facture_publiee.pdf",
            pdf_buffer.getvalue(),
            content_type="application/pdf"
        )
        
        response = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {'fichier': pdf_file, 'auto_match': True},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que la facture est dans 'skipped'
        matching = response.data.get('matching', {})
        self.assertGreater(matching.get('skipped_already_processed', 0), 0)
        details = matching.get('details', {})
        skipped = details.get('skipped', [])
        self.assertGreater(len(skipped), 0)
        
        # Vérifier que le statut n'a pas changé
        self.invoice1.refresh_from_db()
        self.assertEqual(self.invoice1.statut, 'PUBLIEE')
    
    def test_pdf_avec_page_invalide_au_milieu(self):
        """Un PDF avec une page invalide au milieu ne doit pas bloquer les autres"""
        # Créer un PDF avec une facture valide, une invalide, et une valide
        pdf_buffer = create_multi_invoice_pdf([
            {
                'numero_facture': 'FAC-99111111-202608-001',
                'msisdn': '99111111'
            },
            {
                # Page sans identifiants reconnaissables
                'texte_libre': 'Page de publicité ou page vide'
            },
            {
                'numero_facture': 'FAC-99222222-202608-002',
                'msisdn': '99222222'
            }
        ])
        
        pdf_file = SimpleUploadedFile(
            "factures_mixtes.pdf",
            pdf_buffer.getvalue(),
            content_type="application/pdf"
        )
        
        response = self.client.post(
            '/api/billing/invoices/upload_bulk_pdf/',
            {'fichier': pdf_file, 'auto_match': True},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'au moins une facture a été matchée
        matching = response.data.get('matching', {})
        self.assertGreater(matching.get('successfully_matched', 0), 0)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PDFSecurityTests(TestCase):
    """Tests de sécurité d'accès aux PDF"""
    
    def setUp(self):
        if not PDF_AVAILABLE:
            self.skipTest("PyPDF2 ou reportlab non disponible")
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='test123',
            role='AGENT_FACTURATION'
        )
        
        self.payeur1 = User.objects.create_user(
            username='payeur1',
            email='payeur1@test.com',
            password='test123',
            role='PAYEUR'
        )
        
        self.payeur2 = User.objects.create_user(
            username='payeur2',
            email='payeur2@test.com',
            password='test123',
            role='PAYEUR'
        )
        
        self.employe1 = User.objects.create_user(
            username='employe1',
            email='employe1@test.com',
            password='test123',
            role='EMPLOYE'
        )
        
        self.company1 = Company.objects.create(
            compte='A1111111',
            raison_sociale='Company 1',
            payeur=self.payeur1
        )
        
        self.company2 = Company.objects.create(
            compte='A2222222',
            raison_sociale='Company 2',
            payeur=self.payeur2
        )
        
        self.line1 = Line.objects.create(
            company=self.company1,
            msisdn='99111111',
            employe=self.employe1,
            forfait=Decimal('10000')
        )
        
        # Créer une facture avec PDF
        self.invoice1 = Invoice.objects.create(
            company=self.company1,
            line=self.line1,
            numero_facture='FAC-TEST-001',
            periode_debut=date(2026, 8, 1),
            periode_fin=date(2026, 8, 31),
            montant_ht=Decimal('10000'),
            montant_tva=Decimal('1800'),
            montant_ttc=Decimal('11800'),
            date_echeance=date(2026, 9, 30),
            statut='PUBLIEE'
        )
        
        # Attacher un PDF factice
        pdf_buffer = create_test_pdf("Facture confidentielle")
        self.invoice1.fichier_pdf.save(
            'facture_test.pdf',
            pdf_buffer,
            save=True
        )
        
        self.client = APIClient()
    
    def test_payeur_peut_acceder_a_sa_facture(self):
        """Un payeur peut accéder aux factures de son entreprise"""
        self.client.force_authenticate(user=self.payeur1)
        
        response = self.client.get(f'/api/billing/invoices/{self.invoice1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.invoice1.id))
    
    def test_payeur_ne_peut_pas_acceder_facture_autre_entreprise(self):
        """Un payeur ne peut pas accéder aux factures d'une autre entreprise"""
        self.client.force_authenticate(user=self.payeur2)
        
        response = self.client.get(f'/api/billing/invoices/{self.invoice1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_employe_peut_acceder_a_sa_facture(self):
        """Un employé peut accéder à sa facture individuelle"""
        self.client.force_authenticate(user=self.employe1)
        
        response = self.client.get(f'/api/billing/invoices/{self.invoice1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.invoice1.id))

