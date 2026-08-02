"""
Tests pour l'application billing - Phases 2 & 3
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from accounts.models import User
from .models import Company, Line, Package, Service, TarifService


class PackageTests(APITestCase):
    """Tests pour la gestion des forfaits"""
    
    def setUp(self):
        """Créer des utilisateurs de test"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION'
        )
        
        self.package = Package.objects.create(
            nom='Forfait Test',
            code='FT1000',
            type_forfait='MIXTE',
            prix_mensuel=Decimal('5000'),
            quota_data_mo=1024,
            quota_minutes=100,
            quota_sms=50
        )
        
        self.client = APIClient()
    
    def test_list_packages(self):
        """Test liste des forfaits"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('package-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_package(self):
        """Test création de forfait"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('package-list')
        data = {
            'nom': 'Nouveau Forfait',
            'code': 'NF2000',
            'type_forfait': 'DATA',
            'prix_mensuel': '10000',
            'quota_data_mo': 5120,
            'description': 'Forfait data premium'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nom'], 'Nouveau Forfait')
        
        # Vérifier création
        package = Package.objects.get(code='NF2000')
        self.assertEqual(package.quota_data_mo, 5120)
    
    def test_toggle_package_actif(self):
        """Test activation/désactivation forfait"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('package-toggle-actif', kwargs={'pk': self.package.pk})
        
        # Désactiver
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.package.refresh_from_db()
        self.assertFalse(self.package.est_actif)
        
        # Réactiver
        response = self.client.post(url)
        self.package.refresh_from_db()
        self.assertTrue(self.package.est_actif)


class ServiceTests(APITestCase):
    """Tests pour la gestion des services"""
    
    def setUp(self):
        """Créer des données de test"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION'
        )
        
        self.service = Service.objects.create(
            nom='BlackBerry',
            code='BB',
            type_service='OPTION',
            description='Service BlackBerry'
        )
        
        self.tarif1 = TarifService.objects.create(
            service=self.service,
            nom_option='BB 500 Mo',
            prix=Decimal('1000')
        )
        
        self.tarif2 = TarifService.objects.create(
            service=self.service,
            nom_option='BB 1 Go',
            prix=Decimal('2000')
        )
        
        self.client = APIClient()
    
    def test_list_services(self):
        """Test liste des services"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('service-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre_tarifs'], 2)
    
    def test_create_service_with_tarifs(self):
        """Test création de service avec tarifs"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('service-list')
        data = {
            'nom': 'No Limit',
            'code': 'NL',
            'type_service': 'OPTION',
            'description': 'Service No Limit',
            'tarifs': [
                {
                    'nom_option': 'NL 24h',
                    'prix': '500',
                    'duree_validite_heures': 24
                },
                {
                    'nom_option': 'NL 7j',
                    'prix': '2000',
                    'duree_validite_heures': 168
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier les tarifs créés
        service = Service.objects.get(code='NL')
        self.assertEqual(service.tarifs.count(), 2)
    
    def test_get_service_tarifs(self):
        """Test récupération des tarifs d'un service"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('service-tarifs', kwargs={'pk': self.service.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_toggle_service_actif(self):
        """Test activation/désactivation service"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('service-toggle-actif', kwargs={'pk': self.service.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.service.refresh_from_db()
        self.assertFalse(self.service.est_actif)


class TarifServiceTests(APITestCase):
    """Tests pour la gestion des tarifs de services"""
    
    def setUp(self):
        """Créer des données de test"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN'
        )
        
        self.service = Service.objects.create(
            nom='Test Service',
            code='TS',
            type_service='PASS'
        )
        
        self.tarif = TarifService.objects.create(
            service=self.service,
            nom_option='Option Test',
            prix=Decimal('1500')
        )
        
        self.client = APIClient()
    
    def test_list_tarifs(self):
        """Test liste des tarifs"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('tarif-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_tarif(self):
        """Test création de tarif"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('tarif-list')
        data = {
            'service': str(self.service.id),
            'nom_option': 'Nouvelle Option',
            'prix': '3000',
            'duree_validite_heures': 72
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_toggle_tarif_actif(self):
        """Test activation/désactivation tarif"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('tarif-toggle-actif', kwargs={'pk': self.tarif.pk})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.tarif.refresh_from_db()
        self.assertFalse(self.tarif.est_actif)


class CompanyTests(APITestCase):
    """Tests pour la gestion des contrats/entreprises"""
    
    def setUp(self):
        """Créer des utilisateurs et données de test"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN',
            first_name='Admin',
            last_name='Test'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION',
            first_name='Agent',
            last_name='Test'
        )
        
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='Payeur@123',
            role='PAYEUR',
            first_name='Payeur',
            last_name='Test'
        )
        
        self.employe = User.objects.create_user(
            username='employe_test',
            email='employe@test.com',
            password='Employe@123',
            role='EMPLOYE',
            first_name='Employe',
            last_name='Test'
        )
        
        # Créer une entreprise de test
        self.company = Company.objects.create(
            compte='C26TEST001',
            raison_sociale='Entreprise Test',
            categorie='PE',
            payeur=self.payeur
        )
        
        self.client = APIClient()
    
    def test_list_companies_as_agent(self):
        """Test liste des entreprises en tant qu'agent"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('company-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_list_companies_as_payeur(self):
        """Test payeur peut consulter ses entreprises (selon matrice d'accès)"""
        # Créer une autre entreprise sans ce payeur
        Company.objects.create(
            compte='C26TEST002',
            raison_sociale='Autre Entreprise',
            categorie='GE'
        )
        
        self.client.force_authenticate(user=self.payeur)
        url = reverse('company-list')
        response = self.client.get(url)
        
        # Selon MATRICE_ACCES_ET_TRANSITIONS.md : PAYEUR peut "Consulter ses entreprises" ✅
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Voit seulement la sienne
        self.assertEqual(response.data[0]['compte'], 'C26TEST001')
    
    def test_create_company_as_agent(self):
        """Test création d'entreprise par agent"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('company-list')
        data = {
            'compte': 'C26NEW001',
            'raison_sociale': 'Nouvelle Entreprise',
            'categorie': 'GE',
            'adresse': '123 Rue Test',
            'payeur': self.payeur.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['compte'], 'C26NEW001')
        
        # Vérifier que l'entreprise est créée
        company = Company.objects.get(compte='C26NEW001')
        self.assertEqual(company.raison_sociale, 'Nouvelle Entreprise')
    
    def test_create_company_with_lines(self):
        """Test création d'entreprise avec lignes"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('company-list')
        data = {
            'compte': 'C26NEW002',
            'raison_sociale': 'Entreprise avec Lignes',
            'categorie': 'PE',
            'payeur': self.payeur.id,
            'lignes': [
                {
                    'msisdn': '90123456',
                    'utilisateur': 'User 1',
                    'cycle': 'HYB',
                    'forfait': '5000'
                },
                {
                    'msisdn': '90123457',
                    'utilisateur': 'User 2',
                    'cycle': 'OP',
                    'forfait': '10000'
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier les lignes
        company = Company.objects.get(compte='C26NEW002')
        self.assertEqual(company.lines.count(), 2)
    
    def test_company_stats(self):
        """Test statistiques d'un contrat"""
        # Créer des lignes de test
        Line.objects.create(
            company=self.company,
            msisdn='90111111',
            statut='ACTIF',
            cycle='HYB',
            forfait=Decimal('5000')
        )
        Line.objects.create(
            company=self.company,
            msisdn='90222222',
            statut='ACTIF',
            cycle='OP',
            forfait=Decimal('10000')
        )
        Line.objects.create(
            company=self.company,
            msisdn='90333333',
            statut='INACTIF',
            cycle='HYB',
            forfait=Decimal('3000')
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('company-stats', kwargs={'pk': self.company.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_lignes_total'], 3)
        self.assertEqual(response.data['nombre_lignes_actives'], 2)
        self.assertEqual(response.data['nombre_lignes_inactives'], 1)
        self.assertEqual(float(response.data['montant_forfaits_total']), 18000.0)
    
    def test_change_company_statut(self):
        """Test changement de statut d'entreprise"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('company-change-statut', kwargs={'pk': self.company.pk})
        data = {
            'nouveau_statut': 'SUSPENDU',
            'raison': 'Test suspension'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le changement
        self.company.refresh_from_db()
        self.assertEqual(self.company.statut, 'SUSPENDU')


class LineTests(APITestCase):
    """Tests pour la gestion des lignes"""
    
    def setUp(self):
        """Créer des données de test"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION'
        )
        
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='Payeur@123',
            role='PAYEUR'
        )
        
        self.employe = User.objects.create_user(
            username='employe_test',
            email='employe@test.com',
            password='Employe@123',
            role='EMPLOYE'
        )
        
        self.company = Company.objects.create(
            compte='C26TEST001',
            raison_sociale='Entreprise Test',
            payeur=self.payeur
        )
        
        self.line = Line.objects.create(
            company=self.company,
            msisdn='90111111',
            utilisateur='User Test',
            cycle='HYB',
            forfait=Decimal('5000'),
            employe=self.employe
        )
        
        self.client = APIClient()
    
    def test_list_lines_as_agent(self):
        """Test liste des lignes en tant qu'agent"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('line-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_list_lines_as_employe(self):
        """Test employé voit seulement sa ligne"""
        # Créer une autre ligne
        Line.objects.create(
            company=self.company,
            msisdn='90222222',
            utilisateur='Autre User',
            cycle='OP'
        )
        
        self.client.force_authenticate(user=self.employe)
        url = reverse('line-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Voit seulement la sienne
        self.assertEqual(response.data[0]['msisdn'], '90111111')
    
    def test_create_line_as_agent(self):
        """Test création de ligne par agent"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('line-list')
        data = {
            'company': self.company.id,
            'msisdn': '90999999',
            'utilisateur': 'New User',
            'cycle': 'OP',
            'forfait': '10000'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['msisdn'], '90999999')
    
    def test_assigner_employe(self):
        """Test assignation d'un employé à une ligne"""
        line_without_employe = Line.objects.create(
            company=self.company,
            msisdn='90888888',
            utilisateur='User Sans Employe',
            cycle='HYB'
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('line-assigner-employe', kwargs={'pk': line_without_employe.pk})
        data = {'employe_id': self.employe.id}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier l'assignation
        line_without_employe.refresh_from_db()
        self.assertEqual(line_without_employe.employe, self.employe)
    
    def test_retirer_employe(self):
        """Test retrait d'un employé d'une ligne"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('line-retirer-employe', kwargs={'pk': self.line.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le retrait
        self.line.refresh_from_db()
        self.assertIsNone(self.line.employe)
    
    def test_change_line_statut(self):
        """Test changement de statut d'une ligne"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('line-change-statut', kwargs={'pk': self.line.pk})
        data = {
            'nouveau_statut': 'SUSPENDU',
            'raison': 'Test suspension ligne'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le changement
        self.line.refresh_from_db()
        self.assertEqual(self.line.statut, 'SUSPENDU')
    
    def test_change_cycle(self):
        """Test changement de cycle de facturation"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('line-change-cycle', kwargs={'pk': self.line.pk})
        data = {'cycle': 'OP'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le changement
        self.line.refresh_from_db()
        self.assertEqual(self.line.cycle, 'OP')


def run_tests():
    """Fonction helper pour lancer les tests"""
    from django.core.management import call_command
    
    print("🧪 Lancement des tests Phase 2...")
    print("=" * 60)
    
    call_command('test', 'billing', verbosity=2)
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")


if __name__ == '__main__':
    run_tests()



# ==================== TESTS PHASE 4 : FACTURATION ====================

from datetime import date, timedelta
from .models import Invoice, HistoriqueFacturation, Publication
from .services.calcul_tarification import CalculateurTarification


class CalculTarificationTests(TestCase):
    """Tests pour le service de calcul de tarification"""
    
    def test_calculer_data_dans_forfait(self):
        """Test calcul DATA dans le forfait"""
        result = CalculateurTarification.calculer_data(
            volume_mo=500,
            forfait_mo=1024
        )
        
        self.assertEqual(result['volume_hors_forfait_mo'], 0)
        self.assertEqual(result['montant_ht'], Decimal('0'))
    
    def test_calculer_data_palier_1go(self):
        """Test calcul DATA palier 1 Go"""
        result = CalculateurTarification.calculer_data(
            volume_mo=1024,
            forfait_mo=0
        )
        
        self.assertEqual(result['volume_hors_forfait_mo'], 1024)
        self.assertEqual(result['montant_ht'], Decimal('2000'))
        self.assertEqual(result['palier_applique'], '1.0 Go')
    
    def test_calculer_data_palier_5go(self):
        """Test calcul DATA palier 5 Go"""
        result = CalculateurTarification.calculer_data(
            volume_mo=5120,
            forfait_mo=0
        )
        
        self.assertEqual(result['montant_ht'], Decimal('5000'))
    
    def test_calculer_data_hors_paliers(self):
        """Test calcul DATA hors paliers (> 275 Go)"""
        volume_mo = 300 * 1024  # 300 Go
        result = CalculateurTarification.calculer_data(
            volume_mo=volume_mo,
            forfait_mo=0
        )
        
        # 300 Go = 307200 Mo
        # Montant = 50000 + (307200 × 5) = 50000 + 1536000 = 1586000
        montant_attendu = Decimal('50000') + (volume_mo * Decimal('5'))
        self.assertEqual(result['montant_ht'], montant_attendu)
    
    def test_calculer_voix_dans_forfait(self):
        """Test calcul VOIX dans le forfait"""
        result = CalculateurTarification.calculer_voix(
            duree_secondes=1800,  # 30 minutes
            forfait_minutes=60
        )
        
        self.assertEqual(result['duree_hors_forfait_secondes'], 0)
        self.assertEqual(result['montant_ht'], Decimal('0'))
    
    def test_calculer_voix_hors_forfait(self):
        """Test calcul VOIX hors forfait"""
        result = CalculateurTarification.calculer_voix(
            duree_secondes=7200,  # 120 minutes
            forfait_minutes=0
        )
        
        self.assertEqual(result['minutes_facturees'], 120)
        # 120 min × 79 × 0.85 (facteur moyen) = 8058
        montant_attendu = Decimal('79') * 120 * Decimal('0.85')
        self.assertEqual(result['montant_ht'], montant_attendu)
    
    def test_calculer_sms_dans_forfait(self):
        """Test calcul SMS dans le forfait"""
        result = CalculateurTarification.calculer_sms(
            nombre_sms=50,
            forfait_sms=100
        )
        
        self.assertEqual(result['nombre_hors_forfait_sms'], 0)
        self.assertEqual(result['montant_ht'], Decimal('0'))
    
    def test_calculer_sms_hors_forfait(self):
        """Test calcul SMS hors forfait"""
        result = CalculateurTarification.calculer_sms(
            nombre_sms=150,
            forfait_sms=100
        )
        
        self.assertEqual(result['nombre_hors_forfait_sms'], 50)
        # 50 SMS × 30 = 1500
        self.assertEqual(result['montant_ht'], Decimal('1500'))
    
    def test_calculer_tva(self):
        """Test calcul TVA 18%"""
        result = CalculateurTarification.calculer_tva(Decimal('10000'))
        
        self.assertEqual(result['montant_ht'], Decimal('10000'))
        self.assertEqual(result['montant_tva'], Decimal('1800'))
        self.assertEqual(result['montant_ttc'], Decimal('11800'))
    
    def test_calculer_facture_ligne_complete(self):
        """Test calcul facture ligne complète"""
        result = CalculateurTarification.calculer_facture_ligne(
            forfait_prix=Decimal('5000'),
            forfait_data_mo=1024,
            forfait_minutes=100,
            forfait_sms=50,
            conso_data_mo=2048,  # 2 Go
            conso_duree_secondes=9000,  # 150 minutes
            conso_sms=80,  # 80 SMS
            services_supplementaires=[
                {'nom': 'BlackBerry', 'prix': 1000},
                {'nom': 'No Limit', 'prix': 500}
            ]
        )
        
        # Vérifier la structure
        self.assertIn('forfait', result)
        self.assertIn('consommations', result)
        self.assertIn('hors_forfait', result)
        self.assertIn('services_supplementaires', result)
        self.assertIn('totaux', result)
        
        # Vérifier forfait
        self.assertEqual(result['forfait']['prix'], Decimal('5000'))
        
        # Vérifier services
        self.assertEqual(result['services_supplementaires']['montant'], Decimal('1500'))
        
        # Vérifier TVA
        self.assertGreater(result['totaux']['montant_tva'], Decimal('0'))
        self.assertGreater(result['totaux']['montant_ttc'], result['totaux']['montant_ht'])


class InvoiceTests(APITestCase):
    """Tests pour la gestion des factures"""
    
    def setUp(self):
        """Créer des données de test"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION'
        )
        
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='Payeur@123',
            role='PAYEUR'
        )
        
        self.company = Company.objects.create(
            compte='C26TEST001',
            raison_sociale='Entreprise Test',
            payeur=self.payeur
        )
        
        # Créer des lignes de test
        self.line1 = Line.objects.create(
            company=self.company,
            msisdn='90111111',
            utilisateur='User 1',
            cycle='HYB',
            forfait=Decimal('5000'),
            statut='ACTIF'
        )
        
        self.line2 = Line.objects.create(
            company=self.company,
            msisdn='90222222',
            utilisateur='User 2',
            cycle='HYB',
            forfait=Decimal('10000'),
            statut='ACTIF'
        )
        
        self.client = APIClient()
    
    def test_list_invoices_as_agent(self):
        """Test liste des factures en tant qu'agent"""
        # Créer une facture de test
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ht=Decimal('15000'),
            montant_tva=Decimal('2700'),
            montant_ttc=Decimal('17700'),
            date_echeance=date(2026, 8, 30)
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_list_invoices_as_payeur(self):
        """Test payeur voit seulement ses factures PUBLIEE"""
        # Facture PUBLIEE du payeur
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('17700'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'  # Payeur voit uniquement PUBLIEE
        )
        
        # Facture NON PUBLIEE du payeur (ne doit pas être visible)
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('15000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE'  # Payeur ne voit pas VALIDEE
        )
        
        # Autre facture
        other_company = Company.objects.create(
            compte='C26OTHER',
            raison_sociale='Autre Entreprise'
        )
        Invoice.objects.create(
            company=other_company,
            numero_facture='FAC-OTHER-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('50000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        self.client.force_authenticate(user=self.payeur)
        url = reverse('invoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['numero_facture'], 'FAC-TEST-001')
    
    def test_generate_invoices(self):
        """Test génération de factures en masse"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-generate')
        data = {
            'cycle': 'HYB',
            'periode_debut': '2026-07-01',
            'periode_fin': '2026-07-31'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('factures', response.data)
        self.assertGreater(len(response.data['factures']), 0)
        
        # Vérifier la facture créée
        facture = Invoice.objects.first()
        self.assertIsNotNone(facture)
        self.assertEqual(facture.statut, 'BROUILLON')
        self.assertEqual(facture.company, self.company)
    
    def test_calculate_line_invoice(self):
        """Test calcul facture d'une ligne"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-calculate-line')
        data = {
            'line_id': self.line1.id,
            'periode_debut': '2026-07-01',
            'periode_fin': '2026-07-31',
            'conso_data_mo': 2048,
            'conso_duree_secondes': 3600,
            'conso_sms': 100
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('calcul', response.data)
        self.assertIn('totaux', response.data['calcul'])
    
    def test_valider_invoice(self):
        """Test validation d'une facture"""
        facture = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('17700'),
            date_echeance=date(2026, 8, 30),
            statut='BROUILLON'
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-valider', kwargs={'pk': facture.pk})
        data = {'commentaire': 'Validation test'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le changement
        facture.refresh_from_db()
        self.assertEqual(facture.statut, 'EN_COURS')
        
        # Vérifier l'historique
        historique = HistoriqueFacturation.objects.filter(invoice=facture).first()
        self.assertIsNotNone(historique)
        self.assertEqual(historique.type_action, 'VALIDATION')
    
    def test_annuler_invoice(self):
        """Test annulation d'une facture"""
        facture = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-003',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('17700'),
            date_echeance=date(2026, 8, 30),
            statut='EN_COURS'
        )
        
        self.client.force_authenticate(user=self.admin)
        url = reverse('invoice-annuler', kwargs={'pk': facture.pk})
        data = {'raison': 'Erreur de facturation'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le changement
        facture.refresh_from_db()
        self.assertEqual(facture.statut, 'ANNULEE')
    
    def test_invoice_stats(self):
        """Test statistiques des factures"""
        # Créer plusieurs factures
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-STAT-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('10000'),
            date_echeance=date(2026, 8, 30),
            statut='BROUILLON'
        )
        Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-STAT-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('20000'),
            date_echeance=date(2026, 8, 30),
            statut='PUBLIEE'
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_factures'], 2)
        self.assertIn('factures_par_statut', response.data)
        self.assertIn('montant_total_ttc', response.data)


class PublicationTests(APITestCase):
    """Tests pour la gestion des publications"""
    
    def setUp(self):
        """Créer des données de test"""
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION'
        )
        
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@test.com',
            password='Payeur@123',
            role='PAYEUR'
        )
        
        self.company = Company.objects.create(
            compte='C26TEST001',
            raison_sociale='Entreprise Test',
            payeur=self.payeur
        )
        
        self.client = APIClient()
    
    def test_create_publication(self):
        """Test création d'une publication - doit être refusée (405)"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('publication-list')
        data = {
            'cycle_facturation': 'HYB',
            'periode_debut': '2026-07-01',
            'periode_fin': '2026-07-31',
            'commentaire': 'Publication test'
        }
        response = self.client.post(url, data, format='json')
        
        # POST est refusé car PublicationViewSet est ReadOnly
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_publish_invoices_masse(self):
        """Test publication de factures en masse via publier_masse"""
        # Créer des factures VALIDEE avec PDF
        facture1 = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-PUB-001',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('10000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE',
            fichier_pdf='factures/test1.pdf'  # PDF requis
        )
        
        facture2 = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-PUB-002',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            montant_ttc=Decimal('20000'),
            date_echeance=date(2026, 8, 30),
            statut='VALIDEE',
            fichier_pdf='factures/test2.pdf'  # PDF requis
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('invoice-publier-masse')
        data = {
            'invoice_ids': [str(facture1.id), str(facture2.id)]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # L'API retourne 'factures_publiees' et non 'published_count'
        self.assertIn('factures_publiees', response.data)
        self.assertEqual(response.data['factures_publiees'], 2)
        
        # Vérifier les factures publiées
        facture1.refresh_from_db()
        facture2.refresh_from_db()
        self.assertEqual(facture1.statut, 'PUBLIEE')
        self.assertEqual(facture2.statut, 'PUBLIEE')
    
    def test_publication_stats(self):
        """Test statistiques d'une publication"""
        publication = Publication.objects.create(
            agent=self.agent,
            cycle_facturation='OP',
            periode_debut=date(2026, 7, 1),
            periode_fin=date(2026, 7, 31),
            nombre_lignes_traitees=10,
            montant_total=Decimal('150000')
        )
        
        self.client.force_authenticate(user=self.agent)
        url = reverse('publication-stats', kwargs={'pk': publication.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_lignes_traitees'], 10)
        self.assertEqual(Decimal(response.data['montant_total']), Decimal('150000'))


def run_all_tests():
    """Lancer tous les tests (Phases 2, 3 et 4)"""
    from django.core.management import call_command
    
    print("🧪 Lancement de TOUS les tests Backend (Phases 2, 3, 4)...")
    print("=" * 70)
    
    call_command('test', 'billing', verbosity=2)
    
    print("\n" + "=" * 70)
    print("✅ Tous les tests terminés")


if __name__ == '__main__':
    run_all_tests()
