"""
Tests pour les corrections Payeur/Employé
- Montants par ligne corrects
- Accès PDF sécurisé
- Services dans LineListSerializer
- Simulations dans dashboard payeur
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Company, Line, Invoice, Simulation
from accounts.models import User


class MontantsParLigneTestCase(TestCase):
    """Tests pour vérifier que chaque ligne affiche uniquement ses propres montants"""
    
    def setUp(self):
        """Créer les données de test"""
        # Créer un payeur
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='testpass123',
            role='PAYEUR',
            first_name='Payeur',
            last_name='Test'
        )
        
        # Créer une entreprise
        self.company = Company.objects.create(
            compte='A0000001',
            raison_sociale='Test Company',
            categorie='PE',
            payeur=self.payeur
        )
        
        # Créer deux lignes
        self.ligne1 = Line.objects.create(
            company=self.company,
            msisdn='70111111',
            utilisateur='Ligne 1',
            cycle='HYB',
            forfait=Decimal('5000')
        )
        
        self.ligne2 = Line.objects.create(
            company=self.company,
            msisdn='70222222',
            utilisateur='Ligne 2',
            cycle='HYB',
            forfait=Decimal('7000')
        )
        
        # Créer des factures spécifiques à chaque ligne
        self.facture_ligne1 = Invoice.objects.create(
            company=self.company,
            line=self.ligne1,
            numero_facture='FAC-L1-001',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ht=Decimal('5000'),
            montant_tva=Decimal('900'),
            montant_ttc=Decimal('5900'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
        
        self.facture_ligne2 = Invoice.objects.create(
            company=self.company,
            line=self.ligne2,
            numero_facture='FAC-L2-001',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ht=Decimal('7000'),
            montant_tva=Decimal('1260'),
            montant_ttc=Decimal('8260'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
        
        # Créer une facture globale (non liée à une ligne)
        self.facture_globale = Invoice.objects.create(
            company=self.company,
            line=None,
            numero_facture='FAC-GLOBAL-001',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ht=Decimal('10000'),
            montant_tva=Decimal('1800'),
            montant_ttc=Decimal('11800'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.payeur)
    
    def test_ligne_affiche_uniquement_ses_factures(self):
        """Test : Une ligne n'affiche que la somme de ses propres factures"""
        response = self.client.get('/api/billing/stats/payeur/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        lignes_a_surveiller = response.data['lignes_a_surveiller']
        
        # Trouver ligne1 et ligne2 dans les résultats
        ligne1_data = next((l for l in lignes_a_surveiller if l['msisdn'] == '70111111'), None)
        ligne2_data = next((l for l in lignes_a_surveiller if l['msisdn'] == '70222222'), None)
        
        self.assertIsNotNone(ligne1_data, "Ligne 1 doit être présente")
        self.assertIsNotNone(ligne2_data, "Ligne 2 doit être présente")
        
        # Vérifier que ligne1 affiche uniquement ses 5900 F
        self.assertEqual(
            float(ligne1_data['montant_facture']),
            5900.0,
            "Ligne 1 doit afficher uniquement 5900 F (sa propre facture)"
        )
        
        # Vérifier que ligne2 affiche uniquement ses 8260 F
        self.assertEqual(
            float(ligne2_data['montant_facture']),
            8260.0,
            "Ligne 2 doit afficher uniquement 8260 F (sa propre facture)"
        )
    
    def test_facture_globale_non_dupliquee_sur_lignes(self):
        """Test : La facture globale n'est pas dupliquée sur chaque ligne"""
        response = self.client.get('/api/billing/stats/payeur/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        lignes_a_surveiller = response.data['lignes_a_surveiller']
        
        # Vérifier que le montant de la facture globale (11800) 
        # n'apparaît PAS dans les montants des lignes
        for ligne in lignes_a_surveiller:
            montant = float(ligne['montant_facture'] or 0)
            self.assertNotEqual(
                montant,
                11800.0,
                f"La facture globale ne doit pas être attribuée à la ligne {ligne['msisdn']}"
            )
    
    def test_statistiques_factures_globales(self):
        """Test : Les factures globales sont trackées séparément"""
        response = self.client.get('/api/billing/stats/payeur/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.data['statistiques']
        
        # Vérifier que les factures globales sont comptées
        self.assertEqual(stats['nombre_factures_globales'], 1)
        self.assertEqual(float(stats['montant_factures_globales']), 11800.0)


class AccesPDFSecuriseTestCase(TestCase):
    """Tests pour vérifier que l'accès aux PDF est sécurisé"""
    
    def setUp(self):
        """Créer les données de test"""
        # Créer deux payeurs avec leurs entreprises
        self.payeur1 = User.objects.create_user(
            username='payeur1',
            email='payeur1@test.com',
            password='testpass123',
            role='PAYEUR',
            first_name='Payeur',
            last_name='Un'
        )
        
        self.payeur2 = User.objects.create_user(
            username='payeur2',
            email='payeur2@test.com',
            password='testpass123',
            role='PAYEUR',
            first_name='Payeur',
            last_name='Deux'
        )
        
        self.company1 = Company.objects.create(
            compte='A0000001',
            raison_sociale='Company 1',
            categorie='PE',
            payeur=self.payeur1
        )
        
        self.company2 = Company.objects.create(
            compte='A0000002',
            raison_sociale='Company 2',
            categorie='PE',
            payeur=self.payeur2
        )
        
        # Créer un employé avec sa ligne
        self.employe1 = User.objects.create_user(
            username='employe1',
            email='employe1@test.com',
            password='testpass123',
            role='EMPLOYE',
            first_name='Employé',
            last_name='Un'
        )
        
        self.ligne_employe1 = Line.objects.create(
            company=self.company1,
            msisdn='70111111',
            utilisateur='Employé 1',
            cycle='HYB',
            forfait=Decimal('5000'),
            employe=self.employe1
        )
        
        self.employe2 = User.objects.create_user(
            username='employe2',
            email='employe2@test.com',
            password='testpass123',
            role='EMPLOYE',
            first_name='Employé',
            last_name='Deux'
        )
        
        self.ligne_employe2 = Line.objects.create(
            company=self.company1,
            msisdn='70222222',
            utilisateur='Employé 2',
            cycle='HYB',
            forfait=Decimal('7000'),
            employe=self.employe2
        )
        
        # Créer des factures avec PDF
        fake_pdf = SimpleUploadedFile(
            "test.pdf",
            b"%PDF-1.4 fake content",
            content_type="application/pdf"
        )
        
        self.facture_company1 = Invoice.objects.create(
            company=self.company1,
            line=self.ligne_employe1,
            numero_facture='FAC-001',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('5900'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE',
            fichier_pdf=fake_pdf
        )
        
        fake_pdf2 = SimpleUploadedFile(
            "test2.pdf",
            b"%PDF-1.4 fake content 2",
            content_type="application/pdf"
        )
        
        self.facture_company2 = Invoice.objects.create(
            company=self.company2,
            numero_facture='FAC-002',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('8260'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE',
            fichier_pdf=fake_pdf2
        )
        
        self.client = APIClient()
    
    def test_payeur_peut_acceder_pdf_de_son_contrat(self):
        """Test : Un payeur peut accéder au PDF de son contrat"""
        self.client.force_authenticate(user=self.payeur1)
        response = self.client.get(f'/api/billing/invoices/{self.facture_company1.id}/pdf/')
        
        # Devrait réussir (200) ou retourner FileResponse
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK],
            "Le payeur doit pouvoir accéder au PDF de son contrat"
        )
    
    def test_payeur_ne_peut_pas_acceder_pdf_autre_contrat(self):
        """Test : Un payeur ne peut PAS accéder au PDF d'un autre contrat"""
        self.client.force_authenticate(user=self.payeur1)
        response = self.client.get(f'/api/billing/invoices/{self.facture_company2.id}/pdf/')
        
        # Devrait retourner 404 (pas dans son queryset)
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Le payeur ne doit PAS accéder au PDF d'un autre contrat"
        )
    
    def test_employe_peut_acceder_pdf_de_sa_ligne(self):
        """Test : Un employé peut accéder au PDF de sa ligne"""
        self.client.force_authenticate(user=self.employe1)
        response = self.client.get(f'/api/billing/invoices/{self.facture_company1.id}/pdf/')
        
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "L'employé doit pouvoir accéder au PDF de sa ligne"
        )
    
    def test_employe_ne_peut_pas_acceder_pdf_autre_employe(self):
        """Test : Un employé ne peut PAS accéder au PDF d'un autre employé"""
        # Créer une facture pour employe2
        fake_pdf3 = SimpleUploadedFile(
            "test3.pdf",
            b"%PDF-1.4 fake content 3",
            content_type="application/pdf"
        )
        
        facture_employe2 = Invoice.objects.create(
            company=self.company1,
            line=self.ligne_employe2,
            numero_facture='FAC-003',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('7200'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE',
            fichier_pdf=fake_pdf3
        )
        
        self.client.force_authenticate(user=self.employe1)
        response = self.client.get(f'/api/billing/invoices/{facture_employe2.id}/pdf/')
        
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "L'employé ne doit PAS accéder au PDF d'un autre employé"
        )


class ServicesLigneListTestCase(TestCase):
    """Tests pour vérifier que les services sont exposés dans LineListSerializer"""
    
    def setUp(self):
        """Créer les données de test"""
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='testpass123',
            role='PAYEUR'
        )
        
        self.company = Company.objects.create(
            compte='A0000001',
            raison_sociale='Test Company',
            categorie='PE',
            payeur=self.payeur
        )
        
        # Créer une ligne avec services activés
        self.ligne = Line.objects.create(
            company=self.company,
            msisdn='70111111',
            utilisateur='Test User',
            cycle='HYB',
            forfait=Decimal('5000'),
            facture_detaillee=True,
            option_nolimit='No Limit 5000',
            option_blackberry='BB Pro',
            est_incognito=True,
            est_roaming=True,
            est_internet=True,
            est_international=False,
            est_non_revenu=False
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.payeur)
    
    def test_services_presentes_dans_liste_lignes(self):
        """Test : Les services d'une ligne sont présents dans la réponse de liste"""
        response = self.client.get('/api/billing/lines/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Trouver notre ligne (gérer à la fois liste directe et objet paginé)
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        ligne_data = next((l for l in results if l['msisdn'] == '70111111'), None)
        
        self.assertIsNotNone(ligne_data, "La ligne doit être présente")
        
        # Vérifier que tous les champs de services sont présents
        self.assertIn('facture_detaillee', ligne_data)
        self.assertIn('option_nolimit', ligne_data)
        self.assertIn('option_blackberry', ligne_data)
        self.assertIn('est_incognito', ligne_data)
        self.assertIn('est_roaming', ligne_data)
        self.assertIn('est_internet', ligne_data)
        self.assertIn('est_international', ligne_data)
        self.assertIn('est_non_revenu', ligne_data)
        
        # Vérifier les valeurs
        self.assertTrue(ligne_data['facture_detaillee'])
        self.assertEqual(ligne_data['option_nolimit'], 'No Limit 5000')
        self.assertEqual(ligne_data['option_blackberry'], 'BB Pro')
        self.assertTrue(ligne_data['est_incognito'])
        self.assertTrue(ligne_data['est_roaming'])
        self.assertTrue(ligne_data['est_internet'])
        self.assertFalse(ligne_data['est_international'])
        self.assertFalse(ligne_data['est_non_revenu'])


class SimulationsDashboardPayeurTestCase(TestCase):
    """Tests pour vérifier que les simulations apparaissent dans le dashboard payeur"""
    
    def setUp(self):
        """Créer les données de test"""
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='testpass123',
            role='PAYEUR'
        )
        
        self.company = Company.objects.create(
            compte='A0000001',
            raison_sociale='Test Company',
            categorie='PE',
            payeur=self.payeur
        )
        
        # Créer des simulations
        self.sim1 = Simulation.objects.create(
            utilisateur=self.payeur,
            montant_estime=Decimal('15000'),
            services_selectionnes=['Roaming', 'Internet'],
            resultat_detaille={'cycle': 'HYB'}
        )
        
        self.sim2 = Simulation.objects.create(
            utilisateur=self.payeur,
            montant_estime=Decimal('20000'),
            services_selectionnes=['Roaming', 'Internet', 'International'],
            resultat_detaille={'cycle': 'OP'}
        )
        
        self.sim3 = Simulation.objects.create(
            utilisateur=self.payeur,
            montant_estime=Decimal('18000'),
            services_selectionnes=['Internet'],
            resultat_detaille={'cycle': 'HYB'}
        )
        
        self.sim4 = Simulation.objects.create(
            utilisateur=self.payeur,
            montant_estime=Decimal('12000'),
            services_selectionnes=['Roaming'],
            resultat_detaille={'cycle': 'HYB'}
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.payeur)
    
    def test_dernieres_simulations_presentes(self):
        """Test : Les 3 dernières simulations de l'utilisateur sont présentes"""
        response = self.client.get('/api/billing/stats/payeur/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        simulations = response.data.get('dernieres_simulations', [])
        
        # Doit avoir exactement 3 simulations (les 3 dernières)
        self.assertEqual(len(simulations), 3, "Doit avoir 3 simulations")
        
        # Vérifier que ce sont les 3 dernières (ordre DESC par date)
        montants = [float(s['montant_estime']) for s in simulations]
        # sim4, sim3, sim2 sont les 3 dernières créées
        self.assertIn(12000.0, montants)
        self.assertIn(18000.0, montants)
        self.assertIn(20000.0, montants)
    
    def test_structure_simulation(self):
        """Test : Chaque simulation a la bonne structure"""
        response = self.client.get('/api/billing/stats/payeur/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        simulations = response.data.get('dernieres_simulations', [])
        self.assertGreater(len(simulations), 0, "Doit avoir au moins 1 simulation")
        
        sim = simulations[0]
        
        # Vérifier la structure
        self.assertIn('id', sim)
        self.assertIn('date_simulation', sim)
        self.assertIn('montant_estime', sim)
        self.assertIn('services_selectionnes', sim)
        self.assertIn('resultat_detaille', sim)
        
        # Vérifier les types
        self.assertIsInstance(sim['montant_estime'], (int, float))
        self.assertIsInstance(sim['services_selectionnes'], list)
        self.assertIsInstance(sim['resultat_detaille'], dict)
