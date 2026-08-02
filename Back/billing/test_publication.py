"""
Tests pour le workflow de publication des factures
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile

from accounts.models import User
from .models import Company, Line, Invoice, HistoriqueFacturation, Publication


class PublicationWorkflowTests(TestCase):
    """Tests du workflow complet de publication"""
    
    def setUp(self):
        """Créer les données de test"""
        # Utilisateurs
        self.agent = User.objects.create_user(
            username='agent_pub',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION',
            first_name='Agent',
            last_name='Test'
        )
        
        self.payeur = User.objects.create_user(
            username='payeur_pub',
            email='payeur@test.com',
            password='Payeur@123',
            role='PAYEUR',
            first_name='Payeur',
            last_name='Test'
        )
        
        self.employe = User.objects.create_user(
            username='99111111',
            email='employe@test.com',
            password='Employe@123',
            role='EMPLOYE',
            first_name='Jean',
            last_name='Dupont'
        )
        
        self.autre_employe = User.objects.create_user(
            username='99222222',
            email='employe2@test.com',
            password='Employe@123',
            role='EMPLOYE',
            first_name='Marie',
            last_name='Martin'
        )
        
        # Entreprise
        self.company = Company.objects.create(
            compte='C26TEST001',
            raison_sociale='Entreprise Test Publication',
            categorie='PE',
            payeur=self.payeur
        )
        
        # Lignes
        self.line1 = Line.objects.create(
            company=self.company,
            msisdn='99111111',
            utilisateur='Jean Dupont',
            cycle='HYB',
            forfait=Decimal('5000'),
            employe=self.employe
        )
        
        self.line2 = Line.objects.create(
            company=self.company,
            msisdn='99222222',
            utilisateur='Marie Martin',
            cycle='HYB',
            forfait=Decimal('7000'),
            employe=self.autre_employe
        )
        
        # Créer un PDF fictif
        self.pdf_file = SimpleUploadedFile(
            "test_invoice.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        self.client = APIClient()
    
    def test_01_facture_validee_avec_pdf(self):
        """Test : Facture VALIDEE avec PDF peut être publiée"""
        # Créer une facture VALIDEE avec PDF
        invoice = Invoice.objects.create(
            company=self.company,
            line=self.line1,
            numero_facture='FAC-TEST-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ht=Decimal('20000'),
            montant_tva=Decimal('3600'),
            montant_ttc=Decimal('23600'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE',
            fichier_pdf=self.pdf_file
        )
        
        # Publier la facture
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-publier-masse')
        data = {'invoice_ids': [str(invoice.id)]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['factures_publiees'], 1)
        
        # Vérifier le statut
        invoice.refresh_from_db()
        self.assertEqual(invoice.statut, 'PUBLIEE')
        
        # Vérifier l'historique
        historique = HistoriqueFacturation.objects.filter(invoice=invoice).first()
        self.assertIsNotNone(historique)
        self.assertEqual(historique.type_action, 'PUBLICATION')
        self.assertEqual(historique.ancien_statut, 'VALIDEE')
        self.assertEqual(historique.nouveau_statut, 'PUBLIEE')
        self.assertEqual(historique.utilisateur, self.agent)
        
        # Vérifier la création de Publication
        publication = Publication.objects.filter(agent=self.agent).first()
        self.assertIsNotNone(publication)
        self.assertEqual(publication.statut, 'PUBLIEE')
        self.assertGreater(publication.nombre_lignes_traitees, 0)
    
    def test_02_facture_sans_pdf_refusee(self):
        """Test : Facture VALIDEE sans PDF ne peut pas être publiée"""
        invoice = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('23600'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE',
            fichier_pdf=None  # Pas de PDF
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-publier-masse')
        data = {'invoice_ids': [str(invoice.id)]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('factures_invalides', response.data)
        
        # Vérifier que le statut n'a pas changé
        invoice.refresh_from_db()
        self.assertEqual(invoice.statut, 'VALIDEE')
    
    def test_03_facture_mauvais_statut_refusee(self):
        """Test : Facture EN_COURS ne peut pas être publiée"""
        invoice = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-003',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('23600'),
            date_echeance=date(2026, 8, 30),
            statut='EN_COURS',
            fichier_pdf=self.pdf_file
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-publier-masse')
        data = {'invoice_ids': [str(invoice.id)]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('factures_invalides', response.data)
    
    def test_04_facture_deja_publiee_refusee(self):
        """Test : Facture déjà PUBLIEE ne peut pas être republiée"""
        invoice = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-004',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('23600'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE',
            fichier_pdf=self.pdf_file
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-publier-masse')
        data = {'invoice_ids': [str(invoice.id)]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_05_payeur_voit_seulement_publiee(self):
        """Test : Payeur voit uniquement ses factures PUBLIEE"""
        # Créer plusieurs factures
        inv_validee = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-005',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('20000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE'
        )
        
        inv_publiee = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-006',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('30000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Autre entreprise
        autre_company = Company.objects.create(
            compte='C26AUTRE',
            raison_sociale='Autre Entreprise'
        )
        
        inv_autre = Invoice.objects.create(
            company=autre_company,
            numero_facture='FAC-AUTRE-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('50000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Se connecter en tant que payeur
        self.client.force_authenticate(user=self.payeur)
        url = reverse('invoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Doit voir uniquement la facture PUBLIEE de son entreprise
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero_facture'], 'FAC-TEST-006')
    
    def test_06_employe_voit_sa_facture_publiee(self):
        """Test : Employé voit sa facture PUBLIEE"""
        invoice = Invoice.objects.create(
            company=self.company,
            line=self.line1,  # Ligne de self.employe
            numero_facture='FAC-EMP-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('25000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        self.client.force_authenticate(user=self.employe)
        url = reverse('invoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero_facture'], 'FAC-EMP-001')
    
    def test_07_employe_ne_voit_pas_autre_facture(self):
        """Test : Employé ne voit pas la facture d'un autre employé"""
        # Facture de l'autre employé
        invoice = Invoice.objects.create(
            company=self.company,
            line=self.line2,  # Ligne de self.autre_employe
            numero_facture='FAC-EMP-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('27000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Se connecter en tant que premier employé
        self.client.force_authenticate(user=self.employe)
        url = reverse('invoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Ne voit rien
    
    def test_08_publication_en_masse(self):
        """Test : Publication en masse de plusieurs factures"""
        # Créer 3 factures VALIDEE avec PDF
        invoices = []
        for i in range(3):
            inv = Invoice.objects.create(
                company=self.company,
                numero_facture=f'FAC-MASSE-{i+1:03d}',
                periode_debut=date(2026, 7, 1),
                periode_fin=date(2026, 7, 31),
                montant_ht=Decimal('20000'),
                montant_tva=Decimal('3600'),
                montant_ttc=Decimal('23600'),
                date_echeance=date(2026, 8, 30),
                statut='VALIDEE',
                fichier_pdf=SimpleUploadedFile(
                    f"test_{i}.pdf",
                    b"content",
                    content_type="application/pdf"
                )
            )
            invoices.append(inv)
        
        # Publier toutes les factures
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-publier-masse')
        data = {'invoice_ids': [str(inv.id) for inv in invoices]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['factures_publiees'], 3)
        
        # Vérifier que toutes sont PUBLIEE
        for inv in invoices:
            inv.refresh_from_db()
            self.assertEqual(inv.statut, 'PUBLIEE')
        
        # Vérifier historique créé pour chacune
        historiques = HistoriqueFacturation.objects.filter(
            invoice__in=invoices,
            type_action='PUBLICATION'
        )
        self.assertEqual(historiques.count(), 3)
    
    def test_09_liste_factures_a_publier(self):
        """Test : Endpoint factures_a_publier retourne uniquement VALIDEE"""
        # Créer factures de différents statuts
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-EN-COURS',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('20000'),
            date_echeance=date(2026, 8, 30),
            statut='EN_COURS'
        )
        
        inv_validee = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-VALIDEE',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('25000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE'
        )
        
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-PUBLIEE',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('30000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Appeler l'endpoint
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-factures-a-publier')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['factures']), 1)
        self.assertEqual(response.data['factures'][0]['numero_facture'], 'FAC-VALIDEE')
        self.assertIn('stats', response.data)
    
    def test_10_cycle_periode_differents_refuses(self):
        """Test : Publication refusée si cycles ou périodes différents"""
        # Créer 2 factures avec cycles différents
        line_op = Line.objects.create(
            company=self.company,
            msisdn='99333333',
            cycle='OP',
            forfait=Decimal('5000')
        )
        
        inv1_hyb = Invoice.objects.create(
            company=self.company,
            line=self.line1,  # Cycle HYB
            numero_facture='FAC-HYB-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('20000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE',
            fichier_pdf=SimpleUploadedFile("test1.pdf", b"content", content_type="application/pdf")
        )
        
        inv2_op = Invoice.objects.create(
            company=self.company,
            line=line_op,  # Cycle OP
            numero_facture='FAC-OP-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('25000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE',
            fichier_pdf=SimpleUploadedFile("test2.pdf", b"content", content_type="application/pdf")
        )
        
        # Tenter de publier ensemble
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-publier-masse')
        data = {'invoice_ids': [str(inv1_hyb.id), str(inv2_op.id)]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cycles_detectes', response.data)
        
        # Vérifier qu'aucune n'a été publiée
        inv1_hyb.refresh_from_db()
        inv2_op.refresh_from_db()
        self.assertEqual(inv1_hyb.statut, 'VALIDEE')
        self.assertEqual(inv2_op.statut, 'VALIDEE')
        
        # Test avec périodes différentes
        inv3_periode_diff = Invoice.objects.create(
            company=self.company,
            line=self.line1,
            numero_facture='FAC-PERIODE-DIFF',
            periode_debut=date(2026, 8, 1),  # Période différente
            periode_fin=date(2026, 8, 31),
            montant_ttc=Decimal('22000'),
            date_echeance=date(2026, 9, 30),
            statut='VALIDEE',
            fichier_pdf=SimpleUploadedFile("test3.pdf", b"content", content_type="application/pdf")
        )
        
        data = {'invoice_ids': [str(inv1_hyb.id), str(inv3_periode_diff.id)]}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('periodes_detectees', response.data)
    
    def test_11_creation_directe_publication_refusee(self):
        """Test : Création directe de Publication est refusée"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('publication-list')
        data = {
            'cycle_facturation': 'HYB',
            'periode_debut': '2026-07-01',
            'periode_fin': '2026-07-31',
            'commentaire': 'Test'
        }
        response = self.client.post(url, data, format='json')
        
        # Doit être refusé (ReadOnlyModelViewSet)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_12_upload_pdf_cree_publication_validee(self):
        """Test : Upload PDF réel crée Publication avec statut VALIDEE, pas PUBLIEE"""
        from unittest.mock import patch
        
        # Créer une facture EN_COURS sans PDF
        invoice = Invoice.objects.create(
            company=self.company,
            line=self.line1,
            numero_facture='FAC-UPLOAD-TEST',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ht=Decimal('20000'),
            montant_tva=Decimal('3600'),
            montant_ttc=Decimal('23600'),
            date_echeance=date(2026, 8, 30),
            statut='EN_COURS'
        )
        
        # Mock pour process_bulk_pdf
        mock_process_result = {
            'success': True,
            'total_pages': 5,
            'total_blocks': 1,
            'files_created': 1,
            'files': [
                {
                    'filename': f'facture_{invoice.numero_facture}.pdf',
                    'pages': 5,
                    'identifiers': {'numero_facture': invoice.numero_facture}
                }
            ]
        }
        
        # Mock pour auto_attach_pdfs qui simule l'attachement du PDF
        def mock_auto_attach_pdfs(files, invoices_query, processed_invoices_query):
            # Simuler l'attachement du PDF à la facture
            invoice.fichier_pdf.save(
                f'factures/test_{invoice.numero_facture}.pdf',
                ContentFile(b'test pdf content'),
                save=False
            )
            invoice.statut = 'VALIDEE'
            invoice.save()
            
            return {
                'total_files': 1,
                'matched': 1,
                'not_matched': 0,
                'attached': [
                    {
                        'invoice_id': str(invoice.id),
                        'filename': f'facture_{invoice.numero_facture}.pdf'
                    }
                ],
                'skipped': [],
                'errors': []
            }
        
        # Préparer le fichier PDF minimal valide
        pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF'
        pdf_file = SimpleUploadedFile(
            "test_bulk.pdf",
            pdf_content,
            content_type="application/pdf"
        )
        
        # Appeler l'endpoint réel avec patches corrects
        with patch('billing.services.pdf_processor.PDFProcessor.check_dependencies', return_value=True):
            with patch('billing.services.pdf_processor.PDFProcessor.process_bulk_pdf', return_value=mock_process_result):
                with patch('billing.services.pdf_processor.PDFMatcher.auto_attach_pdfs', side_effect=mock_auto_attach_pdfs):
                    self.client.force_authenticate(user=self.agent)
                    url = reverse('invoice-upload-bulk-pdf')
                    data = {
                        'fichier': pdf_file,
                        'auto_match': True,
                        'cycle': 'HYB',
                        'periode_debut': '2026-07-01',
                        'periode_fin': '2026-07-31'
                    }
                    response = self.client.post(url, data, format='multipart')
        
        # Vérifications de la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('message'))
        
        # La facture doit être VALIDEE avec PDF attaché
        invoice.refresh_from_db()
        self.assertEqual(invoice.statut, 'VALIDEE')
        self.assertTrue(invoice.fichier_pdf)
        
        # Une Publication doit avoir été créée avec statut VALIDEE
        publications = Publication.objects.filter(
            agent=self.agent,
            cycle_facturation='HYB',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31)
        )
        self.assertGreaterEqual(publications.count(), 1)
        
        # Vérifier qu'au moins une Publication est VALIDEE
        publication_validee = publications.filter(statut='VALIDEE').first()
        self.assertIsNotNone(publication_validee)
        
        # Aucune Publication PUBLIEE ne doit exister
        publications_publiees = Publication.objects.filter(statut='PUBLIEE')
        self.assertEqual(publications_publiees.count(), 0)
        
        # Le payeur ne doit pas voir cette facture (elle n'est pas PUBLIEE)
        self.client.force_authenticate(user=self.payeur)
        url_list = reverse('invoice-list')
        response = self.client.get(url_list)
        self.assertEqual(len(response.data), 0)
    
    def test_13_upload_pdf_ne_cree_pas_publication_publiee(self):
        """Test : Upload PDF ne doit jamais créer de Publication PUBLIEE"""
        from unittest.mock import patch
        
        # Créer 2 factures EN_COURS
        inv1 = Invoice.objects.create(
            company=self.company,
            line=self.line1,
            numero_facture='FAC-UPLOAD-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ht=Decimal('18000'),
            montant_tva=Decimal('3240'),
            montant_ttc=Decimal('21240'),
            date_echeance=date(2026, 8, 30),
            statut='EN_COURS'
        )
        
        inv2 = Invoice.objects.create(
            company=self.company,
            line=self.line2,
            numero_facture='FAC-UPLOAD-003',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ht=Decimal('22000'),
            montant_tva=Decimal('3960'),
            montant_ttc=Decimal('25960'),
            date_echeance=date(2026, 8, 30),
            statut='EN_COURS'
        )
        
        # Mock pour process_bulk_pdf
        mock_process_result = {
            'success': True,
            'total_pages': 10,
            'total_blocks': 2,
            'files_created': 2,
            'files': [
                {'filename': f'facture_{inv1.numero_facture}.pdf', 'pages': 5},
                {'filename': f'facture_{inv2.numero_facture}.pdf', 'pages': 5}
            ]
        }
        
        # Mock pour auto_attach_pdfs avec signature correcte
        def mock_auto_attach_pdfs(files, invoices_query, processed_invoices_query):
            # Attacher PDFs et passer les factures à VALIDEE
            inv1.fichier_pdf.save(
                f'factures/test_{inv1.numero_facture}.pdf',
                ContentFile(b'test pdf content 1'),
                save=False
            )
            inv1.statut = 'VALIDEE'
            inv1.save()
            
            inv2.fichier_pdf.save(
                f'factures/test_{inv2.numero_facture}.pdf',
                ContentFile(b'test pdf content 2'),
                save=False
            )
            inv2.statut = 'VALIDEE'
            inv2.save()
            
            return {
                'total_files': 2,
                'matched': 2,
                'not_matched': 0,
                'attached': [
                    {'invoice_id': str(inv1.id), 'filename': f'facture_{inv1.numero_facture}.pdf'},
                    {'invoice_id': str(inv2.id), 'filename': f'facture_{inv2.numero_facture}.pdf'}
                ],
                'skipped': [],
                'errors': []
            }
        
        # Préparer le fichier PDF minimal
        pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF'
        pdf_file = SimpleUploadedFile("test_bulk_multi.pdf", pdf_content, content_type="application/pdf")
        
        # Appeler l'endpoint réel avec patches corrects
        with patch('billing.services.pdf_processor.PDFProcessor.check_dependencies', return_value=True):
            with patch('billing.services.pdf_processor.PDFProcessor.process_bulk_pdf', return_value=mock_process_result):
                with patch('billing.services.pdf_processor.PDFMatcher.auto_attach_pdfs', side_effect=mock_auto_attach_pdfs):
                    self.client.force_authenticate(user=self.agent)
                    url = reverse('invoice-upload-bulk-pdf')
                    data = {
                        'fichier': pdf_file,
                        'auto_match': True,
                        'cycle': 'HYB',
                        'periode_debut': '2026-07-01',
                        'periode_fin': '2026-07-31'
                    }
                    response = self.client.post(url, data, format='multipart')
        
        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'aucune Publication PUBLIEE n'existe
        publications_publiees = Publication.objects.filter(statut='PUBLIEE')
        self.assertEqual(publications_publiees.count(), 0)
        
        # Les factures doivent être VALIDEE, pas PUBLIEE
        inv1.refresh_from_db()
        inv2.refresh_from_db()
        self.assertEqual(inv1.statut, 'VALIDEE')
        self.assertEqual(inv2.statut, 'VALIDEE')
        self.assertTrue(inv1.fichier_pdf)
        self.assertTrue(inv2.fichier_pdf)
        
        # Elles ne sont pas visibles par le payeur
        self.client.force_authenticate(user=self.payeur)
        url_list = reverse('invoice-list')
        response = self.client.get(url_list)
        self.assertEqual(len(response.data), 0)
        
        # Elles ne sont pas visibles par l'employé tant qu'elles ne sont pas PUBLIEE
        self.client.force_authenticate(user=self.employe)
        response = self.client.get(url_list)
        self.assertEqual(len(response.data), 0)


def run_publication_tests():
    """Helper pour lancer les tests de publication"""
    from django.core.management import call_command
    
    print("🧪 Tests du workflow de publication")
    print("=" * 60)
    
    call_command('test', 'billing.test_publication', verbosity=2)
    
    print("\n" + "=" * 60)
    print("✅ Tests de publication terminés")


if __name__ == '__main__':
    run_publication_tests()
