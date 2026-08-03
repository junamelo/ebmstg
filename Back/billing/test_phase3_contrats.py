"""
Tests Phase 3 : Isolation des données et protection des factures
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from billing.models import Company, Line, Invoice, Package, Service, TarifService

User = get_user_model()


class IsolationEntreprisesTest(TestCase):
    """Tests d'isolation des données entre entreprises"""
    
    def setUp(self):
        # Créer les utilisateurs
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='test123',
            role='SUPER_ADMIN'
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
        
        self.employe2 = User.objects.create_user(
            username='employe2',
            email='employe2@test.com',
            password='test123',
            role='EMPLOYE'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='test123',
            role='AGENT_FACTURATION'
        )
        
        # Créer deux entreprises
        self.company1 = Company.objects.create(
            compte='TEST001',
            raison_sociale='Entreprise 1',
            payeur=self.payeur1
        )
        
        self.company2 = Company.objects.create(
            compte='TEST002',
            raison_sociale='Entreprise 2',
            payeur=self.payeur2
        )
        
        # Créer des lignes
        self.line1_1 = Line.objects.create(
            company=self.company1,
            msisdn='99111111',
            employe=self.employe1,
            forfait=Decimal('10000')
        )
        
        self.line1_2 = Line.objects.create(
            company=self.company1,
            msisdn='99111112',
            forfait=Decimal('15000')
        )
        
        self.line2_1 = Line.objects.create(
            company=self.company2,
            msisdn='99222221',
            employe=self.employe2,
            forfait=Decimal('20000')
        )
        
        # Créer des factures publiées
        self.invoice1 = Invoice.objects.create(
            company=self.company1,
            line=self.line1_1,
            numero_facture='INV001',
            periode_debut=date(2026, 1, 1),
            periode_fin=date(2026, 1, 31),
            montant_ht=Decimal('10000'),
            montant_tva=Decimal('1800'),
            montant_ttc=Decimal('11800'),
            date_echeance=date(2026, 2, 28),
            statut='PUBLIEE'
        )
        
        self.invoice2 = Invoice.objects.create(
            company=self.company2,
            line=self.line2_1,
            numero_facture='INV002',
            periode_debut=date(2026, 1, 1),
            periode_fin=date(2026, 1, 31),
            montant_ht=Decimal('20000'),
            montant_tva=Decimal('3600'),
            montant_ttc=Decimal('23600'),
            date_echeance=date(2026, 2, 28),
            statut='PUBLIEE'
        )
        
        self.client = APIClient()
    
    def test_payeur_voit_seulement_ses_entreprises(self):
        """Un payeur ne doit voir que ses propres entreprises"""
        self.client.force_authenticate(user=self.payeur1)
        response = self.client.get('/api/billing/companies/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data if isinstance(response.data, list) else response.data.get('results', [])
        
        # Payeur1 ne doit voir que company1
        self.assertEqual(len(data), 1)
        self.assertEqual(str(data[0]['id']), str(self.company1.id))
    
    def test_payeur_ne_peut_pas_acceder_autre_entreprise(self):
        """Un payeur ne peut pas accéder aux détails d'une autre entreprise"""
        self.client.force_authenticate(user=self.payeur1)
        response = self.client.get(f'/api/billing/companies/{self.company2.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_employe_voit_seulement_ses_lignes(self):
        """Un employé ne doit voir que ses propres lignes"""
        self.client.force_authenticate(user=self.employe1)
        response = self.client.get('/api/billing/lines/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data if isinstance(response.data, list) else response.data.get('results', [])
        
        # Employe1 ne doit voir que line1_1
        self.assertEqual(len(data), 1)
        self.assertEqual(str(data[0]['id']), str(self.line1_1.id))
    
    def test_employe_ne_voit_pas_lignes_autres(self):
        """Un employé ne peut pas voir les lignes d'autres employés"""
        self.client.force_authenticate(user=self.employe1)
        response = self.client.get(f'/api/billing/lines/{self.line2_1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_payeur_voit_factures_publiees_de_ses_entreprises(self):
        """Un payeur voit les factures publiées de ses entreprises"""
        self.client.force_authenticate(user=self.payeur1)
        response = self.client.get('/api/billing/invoices/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data if isinstance(response.data, list) else response.data.get('results', [])
        
        # Payeur1 ne doit voir que invoice1 (PUBLIEE)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], str(self.invoice1.id))
    
    def test_payeur_ne_voit_pas_factures_autres_entreprises(self):
        """Un payeur ne peut pas voir les factures d'autres entreprises"""
        self.client.force_authenticate(user=self.payeur1)
        response = self.client.get(f'/api/billing/invoices/{self.invoice2.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_employe_voit_factures_publiees_de_ses_lignes(self):
        """Un employé voit les factures publiées de ses lignes"""
        self.client.force_authenticate(user=self.employe1)
        response = self.client.get('/api/billing/invoices/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data if isinstance(response.data, list) else response.data.get('results', [])
        
        # Employe1 ne doit voir que invoice1 (sa ligne, PUBLIEE)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], str(self.invoice1.id))
    
    def test_agent_voit_toutes_entreprises(self):
        """Un agent voit toutes les entreprises"""
        self.client.force_authenticate(user=self.agent)
        response = self.client.get('/api/billing/companies/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data if isinstance(response.data, list) else response.data.get('results', [])
        
        # Agent voit les 2 entreprises
        self.assertGreaterEqual(len(data), 2)


class ProtectionFacturesTest(TestCase):
    """Tests de protection des factures publiées et payées"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='test123',
            role='SUPER_ADMIN'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
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
            compte='TESTPROT',
            raison_sociale='Test Protection',
            payeur=self.payeur
        )
        
        self.line = Line.objects.create(
            company=self.company,
            msisdn='99999999',
            forfait=Decimal('10000')
        )
        
        # Facture BROUILLON (modifiable)
        self.invoice_brouillon = Invoice.objects.create(
            company=self.company,
            numero_facture='INVBROU',
            periode_debut=date(2026, 1, 1),
            periode_fin=date(2026, 1, 31),
            montant_ht=Decimal('10000'),
            montant_tva=Decimal('1800'),
            montant_ttc=Decimal('11800'),
            date_echeance=date(2026, 2, 28),
            statut='BROUILLON'
        )
        
        # Facture PUBLIEE (non modifiable)
        self.invoice_publiee = Invoice.objects.create(
            company=self.company,
            numero_facture='INVPUB',
            periode_debut=date(2026, 1, 1),
            periode_fin=date(2026, 1, 31),
            montant_ht=Decimal('10000'),
            montant_tva=Decimal('1800'),
            montant_ttc=Decimal('11800'),
            date_echeance=date(2026, 2, 28),
            statut='PUBLIEE'
        )
        
        # Facture PAYEE (non modifiable)
        self.invoice_payee = Invoice.objects.create(
            company=self.company,
            numero_facture='INVPAY',
            periode_debut=date(2026, 1, 1),
            periode_fin=date(2026, 1, 31),
            montant_ht=Decimal('10000'),
            montant_tva=Decimal('1800'),
            montant_ttc=Decimal('11800'),
            date_echeance=date(2026, 2, 28),
            statut='PAYEE'
        )
        
        self.client = APIClient()
    
    def test_modification_facture_brouillon_autorisee(self):
        """Une facture BROUILLON peut être modifiée"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f'/api/billing/invoices/{self.invoice_brouillon.id}/',
            {'commentaire': 'Modification test'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_modification_facture_publiee_interdite(self):
        """Une facture PUBLIEE ne peut pas être modifiée"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f'/api/billing/invoices/{self.invoice_publiee.id}/',
            {'commentaire': 'Tentative modification'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Impossible de modifier', response.data['error'])
    
    def test_modification_facture_payee_interdite(self):
        """Une facture PAYEE ne peut pas être modifiée"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f'/api/billing/invoices/{self.invoice_payee.id}/',
            {'commentaire': 'Tentative modification'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Impossible de modifier', response.data['error'])
    
    def test_suppression_facture_brouillon_autorisee(self):
        """Une facture BROUILLON peut être supprimée"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/billing/invoices/{self.invoice_brouillon.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_suppression_facture_publiee_interdite(self):
        """Une facture PUBLIEE ne peut pas être supprimée"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/billing/invoices/{self.invoice_publiee.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Impossible de supprimer', response.data['error'])
    
    def test_suppression_facture_payee_interdite(self):
        """Une facture PAYEE ne peut pas être supprimée"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/billing/invoices/{self.invoice_payee.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Impossible de supprimer', response.data['error'])
    
    def test_update_complet_facture_publiee_interdit(self):
        """Un PUT complet est aussi interdit sur facture PUBLIEE"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(
            f'/api/billing/invoices/{self.invoice_publiee.id}/',
            {
                'company': str(self.company.id),
                'numero_facture': 'INVPUB',
                'periode_debut': '2026-01-01',
                'periode_fin': '2026-01-31',
                'montant_ht': '15000',
                'montant_tva': '2700',
                'montant_ttc': '17700',
                'date_echeance': '2026-02-28'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ValidationMontantsTest(TestCase):
    """Tests de validation des montants négatifs"""
    
    def setUp(self):
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='test123',
            role='AGENT_FACTURATION'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.agent)
    
    def test_creation_package_prix_negatif_refuse(self):
        """Un package avec prix négatif est refusé"""
        response = self.client.post('/api/billing/packages/', {
            'nom': 'Forfait Test',
            'code': 'TESTNEG',
            'type_forfait': 'DATA',
            'prix_mensuel': '-1000',
            'description': 'Test prix négatif'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_creation_package_prix_zero_autorise(self):
        """Un package avec prix zéro est autorisé"""
        response = self.client.post('/api/billing/packages/', {
            'nom': 'Forfait Test Zero',
            'code': 'TESTZERO',
            'type_forfait': 'DATA',
            'prix_mensuel': '0',
            'description': 'Test prix zéro'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_creation_tarifservice_prix_negatif_refuse(self):
        """Un tarif de service avec prix négatif est refusé"""
        # Créer un service d'abord
        service = Service.objects.create(
            nom='Service Test',
            code='SRVTEST',
            type_service='SUPPLEMENTAIRE'
        )
        
        response = self.client.post('/api/billing/tarifs/', {
            'service': str(service.id),
            'nom_option': 'Option Test',
            'prix': '-500'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_creation_line_forfait_negatif_refuse(self):
        """Une ligne avec forfait négatif est refusée"""
        payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='test123',
            role='PAYEUR'
        )
        
        company = Company.objects.create(
            compte='TESTCOMP',
            raison_sociale='Test Company',
            payeur=payeur
        )
        
        response = self.client.post('/api/billing/lines/', {
            'company': str(company.id),
            'msisdn': '99888888',
            'cycle': 'HYB',
            'forfait': '-5000'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
