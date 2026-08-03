"""
Tests d'authentification pour tous les rôles
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User


class AuthenticationTests(TestCase):
    """Tests de connexion pour tous les rôles"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer les comptes de test
        self.admin = User.objects.create_user(
            username='admin@moov.tg',
            email='admin@moov.tg',
            password='admin123',
            role='SUPER_ADMIN',
            first_name='Admin',
            last_name='System'
        )
        
        self.chef = User.objects.create_user(
            username='chef@moov.tg',
            email='chef@moov.tg',
            password='chef123',
            role='CHEF_FACTURATION',
            first_name='Chef',
            last_name='Facturation'
        )
        
        self.agent = User.objects.create_user(
            username='agent@moov.tg',
            email='agent@moov.tg',
            password='agent123',
            role='AGENT_FACTURATION',
            first_name='Agent',
            last_name='Test'
        )
        
        self.payeur = User.objects.create_user(
            username='A26TEST001',
            email='payeur.test@moov.tg',
            password='payeur123',
            role='PAYEUR',
            first_name='Payeur',
            last_name='Test'
        )
        
        self.employe = User.objects.create_user(
            username='99475555',
            email='employe@test.com',
            password='employe123',
            role='EMPLOYE',
            first_name='Employé',
            last_name='Test'
        )
    
    def test_connexion_admin(self):
        """Test : Admin peut se connecter avec email"""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@moov.tg',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['role'], 'SUPER_ADMIN')
    
    def test_connexion_chef(self):
        """Test : Chef facturation peut se connecter avec email"""
        response = self.client.post('/api/auth/login/', {
            'email': 'chef@moov.tg',
            'password': 'chef123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['role'], 'CHEF_FACTURATION')
    
    def test_connexion_agent(self):
        """Test : Agent facturation peut se connecter avec email"""
        response = self.client.post('/api/auth/login/', {
            'email': 'agent@moov.tg',
            'password': 'agent123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['role'], 'AGENT_FACTURATION')
    
    def test_connexion_payeur_avec_username(self):
        """Test : Payeur peut se connecter avec numéro de compte"""
        response = self.client.post('/api/auth/login/', {
            'email': 'A26TEST001',
            'password': 'payeur123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['role'], 'PAYEUR')
    
    def test_connexion_payeur_avec_email(self):
        """Test : Payeur peut se connecter avec email"""
        response = self.client.post('/api/auth/login/', {
            'email': 'payeur.test@moov.tg',
            'password': 'payeur123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['role'], 'PAYEUR')
    
    def test_connexion_employe_avec_msisdn(self):
        """Test : Employé peut se connecter avec MSISDN"""
        response = self.client.post('/api/auth/login/', {
            'email': '99475555',
            'password': 'employe123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['role'], 'EMPLOYE')
    
    def test_connexion_employe_avec_email(self):
        """Test : Employé peut se connecter avec email"""
        response = self.client.post('/api/auth/login/', {
            'email': 'employe@test.com',
            'password': 'employe123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['role'], 'EMPLOYE')
    
    def test_connexion_identifiants_invalides(self):
        """Test : Connexion échoue avec identifiants invalides"""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@moov.tg',
            'password': 'mauvais_mdp'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_connexion_utilisateur_inexistant(self):
        """Test : Connexion échoue avec utilisateur inexistant"""
        response = self.client.post('/api/auth/login/', {
            'email': 'inconnu@test.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_filtre_utilisateurs_par_role(self):
        """Test : GET /api/auth/users/?role=EMPLOYE filtre correctement"""
        # Se connecter en tant qu'admin
        self.client.force_authenticate(user=self.admin)
        
        # Filtrer par rôle EMPLOYE
        response = self.client.get('/api/auth/users/', {'role': 'EMPLOYE'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        users = response.data if isinstance(response.data, list) else response.data.get('results', [])
        # Vérifier qu'il y a au moins un employé
        self.assertTrue(len(users) > 0)
        # Vérifier que tous les résultats sont des employés
        for user in users:
            self.assertEqual(user['role'], 'EMPLOYE')
