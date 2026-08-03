"""
Tests pour la Phase 2 : Gestion utilisateurs, entreprises et affectations
"""
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date

from accounts.models import User
from billing.models import Company, Line, Invoice


class AffectationEmployeTests(APITestCase):
    """Tests pour l'affectation d'employés aux lignes"""
    
    def setUp(self):
        """Configuration des tests"""
        # Créer admin
        self.admin = User.objects.create_user(
            username='admin_affectation',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN'
        )
        
        # Créer agent
        self.agent = User.objects.create_user(
            username='agent_affectation',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION'
        )
        
        # Créer payeur
        self.payeur = User.objects.create_user(
            username='payeur_affectation',
            email='payeur@test.com',
            password='Payeur@123',
            role='PAYEUR'
        )
        
        # Créer 2 employés
        self.employe1 = User.objects.create_user(
            username='employe1',
            email='employe1@test.com',
            password='Employe@123',
            role='EMPLOYE'
        )
        
        self.employe2 = User.objects.create_user(
            username='employe2',
            email='employe2@test.com',
            password='Employe@123',
            role='EMPLOYE'
        )
        
        # Créer entreprise
        self.company = Company.objects.create(
            compte='C26TEST001',
            raison_sociale='Entreprise Test',
            categorie='PE',
            payeur=self.payeur
        )
        
        # Créer ligne avec employé1
        self.line1 = Line.objects.create(
            company=self.company,
            msisdn='90111111',
            utilisateur='Employé 1',
            employe=self.employe1
        )
        
        # Créer ligne sans employé
        self.line2 = Line.objects.create(
            company=self.company,
            msisdn='90222222',
            utilisateur='Non assigné'
        )
        
        self.client = APIClient()
    
    def test_01_agent_peut_assigner_employe(self):
        """Test : Agent peut assigner un employé à une ligne"""
        self.client.force_authenticate(user=self.agent)
        url = f'/api/billing/lines/{self.line2.id}/assigner_employe/'
        data = {'employe_id': self.employe2.id}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.line2.refresh_from_db()
        self.assertEqual(self.line2.employe, self.employe2)
    
    def test_02_agent_peut_retirer_employe(self):
        """Test : Agent peut retirer un employé d'une ligne"""
        self.client.force_authenticate(user=self.agent)
        url = f'/api/billing/lines/{self.line1.id}/retirer_employe/'
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.line1.refresh_from_db()
        self.assertIsNone(self.line1.employe)
    
    def test_03_employe_voit_seulement_ses_factures_publiees(self):
        """Test : Employé voit seulement ses factures PUBLIEE"""
        # Facture PUBLIEE de l'employé1
        Invoice.objects.create(
            company=self.company,
            line=self.line1,
            numero_facture='FAC-EMP1-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('15000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Facture VALIDEE de l'employé1 (ne doit pas être visible)
        Invoice.objects.create(
            company=self.company,
            line=self.line1,
            numero_facture='FAC-EMP1-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('12000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE'
        )
        
        self.client.force_authenticate(user=self.employe1)
        url = '/api/billing/invoices/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero_facture'], 'FAC-EMP1-001')
        self.assertEqual(response.data[0]['statut'], 'PUBLIEE')
    
    def test_04_employe_ne_voit_pas_factures_autre_employe(self):
        """Test : Employé ne voit pas les factures d'un autre employé"""
        # Facture de l'employé1
        Invoice.objects.create(
            company=self.company,
            line=self.line1,
            numero_facture='FAC-EMP1-003',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('15000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Facture de l'employé2 (après affectation)
        self.line2.employe = self.employe2
        self.line2.save()
        
        Invoice.objects.create(
            company=self.company,
            line=self.line2,
            numero_facture='FAC-EMP2-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('18000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Employé2 connecté
        self.client.force_authenticate(user=self.employe2)
        url = '/api/billing/invoices/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero_facture'], 'FAC-EMP2-001')
    
    def test_05_payeur_voit_factures_publiees_son_entreprise(self):
        """Test : Payeur voit uniquement factures PUBLIEE de son entreprise"""
        # Facture globale PUBLIEE
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-GLOB-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('250000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Facture VALIDEE (ne doit pas être visible)
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-GLOB-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('200000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE'
        )
        
        # Facture d'une autre entreprise
        autre_company = Company.objects.create(
            compte='C26OTHER',
            raison_sociale='Autre Entreprise',
            categorie='GE'
        )
        Invoice.objects.create(
            company=autre_company,
            numero_facture='FAC-OTHER-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('300000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        self.client.force_authenticate(user=self.payeur)
        url = '/api/billing/invoices/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero_facture'], 'FAC-GLOB-001')
    
    def test_06_ligne_non_attribuee_gere_proprement(self):
        """Test : Ligne non attribuée est gérée proprement"""
        # Créer facture pour ligne sans employé
        Invoice.objects.create(
            company=self.company,
            line=self.line2,
            numero_facture='FAC-NOASSIGN-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('10000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Vérifier que personne (sauf agent/admin) ne la voit
        self.client.force_authenticate(user=self.employe1)
        url = '/api/billing/invoices/'
        response = self.client.get(url)
        
        # Employé1 ne doit pas voir cette facture
        factures_employe1 = [f['numero_facture'] for f in response.data]
        self.assertNotIn('FAC-NOASSIGN-001', factures_employe1)
        
        # Agent doit la voir
        self.client.force_authenticate(user=self.agent)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        factures_agent = [f['numero_facture'] for f in response.data]
        self.assertIn('FAC-NOASSIGN-001', factures_agent)
    
    def test_07_facture_sans_ligne_gere_proprement(self):
        """Test : Facture sans ligne (globale) est gérée proprement"""
        # Facture globale PUBLIEE
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-GLOBAL-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('500000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        # Employé ne doit pas la voir
        self.client.force_authenticate(user=self.employe1)
        url = '/api/billing/invoices/'
        response = self.client.get(url)
        factures = [f['numero_facture'] for f in response.data]
        self.assertNotIn('FAC-GLOBAL-001', factures)
        
        # Payeur doit la voir
        self.client.force_authenticate(user=self.payeur)
        response = self.client.get(url)
        factures = [f['numero_facture'] for f in response.data]
        self.assertIn('FAC-GLOBAL-001', factures)
    
    def test_08_affectation_inter_entreprise_refusee(self):
        """Test : Affectation d'une ligne à un employé d'une autre entreprise refusée"""
        # Créer une autre entreprise avec autre payeur
        autre_payeur = User.objects.create_user(
            username='autre_payeur',
            email='autre.payeur@test.com',
            password='Payeur@123',
            role='PAYEUR'
        )
        
        autre_company = Company.objects.create(
            compte='C26OTHER2',
            raison_sociale='Autre Entreprise 2',
            categorie='GE',
            payeur=autre_payeur
        )
        
        # Créer ligne dans autre entreprise
        autre_line = Line.objects.create(
            company=autre_company,
            msisdn='90333333',
            utilisateur='Ligne autre entreprise'
        )
        
        # Tenter d'assigner employe1 (de company) à autre_line (de autre_company)
        self.client.force_authenticate(user=self.agent)
        url = f'/api/billing/lines/{autre_line.id}/assigner_employe/'
        data = {'employe_id': self.employe1.id}
        response = self.client.post(url, data, format='json')
        
        # La validation empêche l'affectation inter-entreprise
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('entreprise', str(response.data).lower())


class IntegriteModeleTests(APITestCase):
    """Tests d'intégrité des modèles"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_integrite',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
    
    def test_01_msisdn_unique(self):
        """Test : MSISDN doit être unique"""
        company = Company.objects.create(
            compte='C26UNIQUE',
            raison_sociale='Test Unique'
        )
        
        Line.objects.create(
            company=company,
            msisdn='90555555'
        )
        
        # Tenter de créer ligne avec même MSISDN
        with self.assertRaises(Exception):
            Line.objects.create(
                company=company,
                msisdn='90555555'
            )
    
    def test_02_ligne_sans_entreprise_refusee(self):
        """Test : Ligne sans entreprise refusée"""
        with self.assertRaises(Exception):
            Line.objects.create(
                msisdn='90666666'
            )
    
    def test_03_ligne_attribuee_non_employe_refusee(self):
        """Test : Ligne attribuée à utilisateur non-EMPLOYE refusée"""
        agent = User.objects.create_user(
            username='agent_test',
            email='agent.test@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION'
        )
        
        company = Company.objects.create(
            compte='C26ROLE',
            raison_sociale='Test Rôle'
        )
        
        line = Line.objects.create(
            company=company,
            msisdn='90777777'
        )
        
        # Assigner agent (pas EMPLOYE) à une ligne
        url = f'/api/billing/lines/{line.id}/assigner_employe/'
        data = {'employe_id': agent.id}
        response = self.client.post(url, data, format='json')
        
        # Doit être refusé
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
