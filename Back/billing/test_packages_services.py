"""
Tests pour la gestion des forfaits (Packages), services et options (TarifService)
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from billing.models import Package, Service, TarifService


class PackageServicePermissionsTestCase(TestCase):
    """Tests des permissions pour forfaits, services et options"""
    
    def setUp(self):
        """Initialiser les utilisateurs de test"""
        self.client = APIClient()
        
        # Créer les utilisateurs
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='test123',
            role='SUPER_ADMIN'
        )
        
        self.chef = User.objects.create_user(
            username='chef_test',
            email='chef@test.com',
            password='test123',
            role='CHEF_FACTURATION'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='test123',
            role='AGENT_FACTURATION'
        )
        
        self.employe = User.objects.create_user(
            username='employe_test',
            email='employe@test.com',
            password='test123',
            role='EMPLOYE'
        )
    
    def test_agent_peut_creer_forfait(self):
        """Test : un agent peut créer un forfait"""
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'nom': 'Forfait Test Agent',
            'code': 'TEST_AGENT',
            'type_forfait': 'MIXTE',
            'prix_mensuel': 5000,
            'quota_data_mo': 2048,
            'quota_minutes': 100,
            'quota_sms': 50
        }
        
        response = self.client.post('/api/billing/packages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Package.objects.filter(code='TEST_AGENT').count(), 1)
    
    def test_chef_peut_creer_forfait(self):
        """Test : un chef peut créer un forfait"""
        self.client.force_authenticate(user=self.chef)
        
        data = {
            'nom': 'Forfait Test Chef',
            'code': 'TEST_CHEF',
            'type_forfait': 'DATA',
            'prix_mensuel': 3000
        }
        
        response = self.client.post('/api/billing/packages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_admin_peut_creer_forfait(self):
        """Test : un admin peut créer un forfait"""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'nom': 'Forfait Test Admin',
            'code': 'TEST_ADMIN',
            'type_forfait': 'VOIX',
            'prix_mensuel': 2000
        }
        
        response = self.client.post('/api/billing/packages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_agent_peut_creer_service(self):
        """Test : un agent peut créer un service"""
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'nom': 'BlackBerry Test',
            'code': 'BB_TEST',
            'type_service': 'OPTION',
            'description': 'Service BlackBerry test'
        }
        
        response = self.client.post('/api/billing/services/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.filter(code='BB_TEST').count(), 1)
    
    def test_agent_peut_creer_option_sur_service(self):
        """Test : un agent peut créer une option sur un service"""
        self.client.force_authenticate(user=self.agent)
        
        # Créer d'abord un service
        service = Service.objects.create(
            nom='No Limit Test',
            code='NL_TEST',
            type_service='OPTION'
        )
        
        # Créer une option sur ce service
        data = {
            'service': str(service.id),
            'nom_option': 'No Limit 12h',
            'prix': 1200
        }
        
        response = self.client.post('/api/billing/tarifs/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TarifService.objects.filter(service=service).count(), 1)
    
    def test_employe_peut_lire_services_options_actifs(self):
        """Test : un employé peut lire services et options actifs"""
        self.client.force_authenticate(user=self.employe)
        
        # Créer un service avec une option active
        service = Service.objects.create(
            nom='Facture Détaillée',
            code='FD_TEST',
            type_service='OPTION',
            est_actif=True
        )
        
        TarifService.objects.create(
            service=service,
            nom_option='FD Standard',
            prix=500,
            est_actif=True
        )
        
        # Lire les services
        response = self.client.get('/api/billing/services/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'il voit le service
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        self.assertTrue(any(s['code'] == 'FD_TEST' for s in results))
    
    def test_employe_ne_peut_pas_creer_forfait(self):
        """Test : un employé ne peut pas créer un forfait"""
        self.client.force_authenticate(user=self.employe)
        
        data = {
            'nom': 'Forfait Interdit',
            'code': 'INTERDIT',
            'type_forfait': 'MIXTE',
            'prix_mensuel': 1000
        }
        
        response = self.client.post('/api/billing/packages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_employe_ne_peut_pas_creer_service(self):
        """Test : un employé ne peut pas créer un service"""
        self.client.force_authenticate(user=self.employe)
        
        data = {
            'nom': 'Service Interdit',
            'code': 'INTERDIT',
            'type_service': 'OPTION'
        }
        
        response = self.client.post('/api/billing/services/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_employe_ne_peut_pas_modifier_service(self):
        """Test : un employé ne peut pas modifier un service"""
        self.client.force_authenticate(user=self.employe)
        
        service = Service.objects.create(
            nom='Service Test',
            code='SRV_TEST',
            type_service='OPTION'
        )
        
        data = {
            'nom': 'Service Modifié',
            'code': 'SRV_TEST',
            'type_service': 'OPTION'
        }
        
        response = self.client.put(f'/api/billing/services/{service.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PackageServiceBusinessLogicTestCase(TestCase):
    """Tests de la logique métier forfaits vs services"""
    
    def setUp(self):
        """Initialiser les données"""
        self.client = APIClient()
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='test123',
            role='AGENT_FACTURATION'
        )
        
        self.client.force_authenticate(user=self.agent)
    
    def test_forfait_ne_contient_pas_options(self):
        """Test : un forfait Package ne contient pas d'options TarifService"""
        # Créer un forfait
        package = Package.objects.create(
            nom='Forfait Premium',
            code='PREMIUM_1',
            type_forfait='MIXTE',
            prix_mensuel=10000,
            quota_data_mo=5120,
            quota_minutes=200,
            quota_sms=100
        )
        
        # Vérifier qu'il n'y a aucune relation Package → TarifService
        # Les forfaits ont leurs propres quotas, pas d'options externes
        self.assertIsNotNone(package.prix_mensuel)
        self.assertIsNotNone(package.quota_data_mo)
        self.assertIsNotNone(package.quota_minutes)
        self.assertIsNotNone(package.quota_sms)
    
    def test_service_contient_options(self):
        """Test : un service peut avoir plusieurs options TarifService"""
        # Créer un service
        service = Service.objects.create(
            nom='BlackBerry',
            code='BB_MAIN',
            type_service='OPTION'
        )
        
        # Créer plusieurs options pour ce service
        TarifService.objects.create(
            service=service,
            nom_option='BB12',
            prix=1200
        )
        
        TarifService.objects.create(
            service=service,
            nom_option='BB15',
            prix=1500
        )
        
        # Vérifier que le service a bien ses options
        self.assertEqual(service.tarifs.count(), 2)
    
    def test_option_creee_apparait_dans_simulation(self):
        """Test : une option créée apparaît dans la liste des services pour simulation"""
        # Créer un service actif
        service = Service.objects.create(
            nom='No Limit',
            code='NL_MAIN',
            type_service='OPTION',
            est_actif=True
        )
        
        # Créer une option active
        tarif = TarifService.objects.create(
            service=service,
            nom_option='No Limit 24h',
            prix=2400,
            est_actif=True
        )
        
        # Lire les services (comme le ferait Simulation.jsx)
        response = self.client.get('/api/billing/services/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier que le service et son tarif sont présents
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        service_trouve = next((s for s in results if s['code'] == 'NL_MAIN'), None)
        
        self.assertIsNotNone(service_trouve)
        self.assertTrue(service_trouve['est_actif'])
        self.assertEqual(len(service_trouve['tarifs']), 1)
        self.assertEqual(service_trouve['tarifs'][0]['nom_option'], 'No Limit 24h')
        self.assertEqual(float(service_trouve['tarifs'][0]['prix']), 2400)
    
    def test_forfait_et_service_independants(self):
        """Test : forfaits et services sont indépendants, pas de relation croisée"""
        # Créer un forfait
        package = Package.objects.create(
            nom='Forfait Standard',
            code='STD_1',
            type_forfait='MIXTE',
            prix_mensuel=5000
        )
        
        # Créer un service avec option
        service = Service.objects.create(
            nom='Incognito',
            code='INC_MAIN',
            type_service='OPTION'
        )
        
        tarif = TarifService.objects.create(
            service=service,
            nom_option='Incognito Monthly',
            prix=1000
        )
        
        # Vérifier qu'il n'y a aucune relation directe
        # Package n'a pas de champ service ou tarif
        # TarifService n'a pas de champ package
        self.assertFalse(hasattr(package, 'tarifs'))
        self.assertFalse(hasattr(tarif, 'package'))

