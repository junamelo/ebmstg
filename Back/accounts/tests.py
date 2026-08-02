"""
Tests pour l'application accounts - Phase 1
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User, StatusHistory


class AuthenticationTests(APITestCase):
    """Tests pour l'authentification"""
    
    def setUp(self):
        """Créer des utilisateurs de test"""
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
        
        self.client = APIClient()
    
    def test_login_success(self):
        """Test login avec credentials valides"""
        url = reverse('login')
        data = {
            'email': 'admin@test.com',
            'password': 'Admin@123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'admin@test.com')
    
    def test_login_invalid_password(self):
        """Test login avec mauvais mot de passe"""
        url = reverse('login')
        data = {
            'email': 'admin@test.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_invalid_email(self):
        """Test login avec email inexistant"""
        url = reverse('login')
        data = {
            'email': 'inexistant@test.com',
            'password': 'Admin@123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_inactive_user(self):
        """Test login avec utilisateur inactif"""
        self.admin.status = 'INACTIF'
        self.admin.save()
        
        url = reverse('login')
        data = {
            'email': 'admin@test.com',
            'password': 'Admin@123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_profile_authenticated(self):
        """Test récupération du profil connecté"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@test.com')
    
    def test_profile_unauthenticated(self):
        """Test profil sans authentification"""
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_change_password_success(self):
        """Test changement de mot de passe réussi"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('change-password')
        data = {
            'old_password': 'Agent@123',
            'new_password': 'NewAgent@456',
            'new_password_confirm': 'NewAgent@456'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # Vérifier que le nouveau mot de passe fonctionne
        self.agent.refresh_from_db()
        self.assertTrue(self.agent.check_password('NewAgent@456'))
    
    def test_change_password_wrong_old(self):
        """Test changement avec mauvais ancien mot de passe"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('change-password')
        data = {
            'old_password': 'WrongOld@123',
            'new_password': 'NewAgent@456',
            'new_password_confirm': 'NewAgent@456'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_mismatch(self):
        """Test changement avec confirmation différente"""
        self.client.force_authenticate(user=self.agent)
        url = reverse('change-password')
        data = {
            'old_password': 'Agent@123',
            'new_password': 'NewAgent@456',
            'new_password_confirm': 'Different@789'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserManagementTests(APITestCase):
    """Tests pour la gestion des utilisateurs"""
    
    def setUp(self):
        """Créer des utilisateurs de test"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN',
            first_name='Admin',
            last_name='Test'
        )
        
        self.chef = User.objects.create_user(
            username='chef_test',
            email='chef@test.com',
            password='Chef@123',
            role='CHEF_FACTURATION',
            first_name='Chef',
            last_name='Test'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION',
            first_name='Agent',
            last_name='Test',
            created_by=self.chef
        )
        
        self.client = APIClient()
    
    def test_list_users_as_admin(self):
        """Test liste des utilisateurs en tant qu'admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # admin, chef, agent
    
    def test_list_users_as_chef(self):
        """Test liste en tant que chef (voit seulement ses agents)"""
        self.client.force_authenticate(user=self.chef)
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # chef + son agent
    
    def test_create_user_as_admin(self):
        """Test création d'utilisateur par admin"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('user-list')
        data = {
            'email': 'newuser@test.com',
            'username': 'newuser',
            'password': 'NewUser@123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'AGENT_FACTURATION',
            'telephone': '90123456'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'newuser@test.com')
        
        # Vérifier que l'utilisateur est créé
        user = User.objects.get(email='newuser@test.com')
        self.assertEqual(user.created_by, self.admin)
    
    def test_create_user_as_chef(self):
        """Test création d'agent par chef"""
        self.client.force_authenticate(user=self.chef)
        url = reverse('user-list')
        data = {
            'email': 'newagent@test.com',
            'username': 'newagent',
            'password': 'NewAgent@123',
            'first_name': 'New',
            'last_name': 'Agent',
            'role': 'AGENT_FACTURATION',
            'telephone': '90123456'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_admin_as_chef_forbidden(self):
        """Test chef ne peut pas créer admin"""
        self.client.force_authenticate(user=self.chef)
        url = reverse('user-list')
        data = {
            'email': 'newadmin@test.com',
            'username': 'newadmin',
            'password': 'NewAdmin@123',
            'first_name': 'New',
            'last_name': 'Admin',
            'role': 'SUPER_ADMIN',
            'telephone': '90123456'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_status(self):
        """Test changement de statut d'utilisateur"""
        self.client.force_authenticate(user=self.chef)
        url = reverse('user-change-status', kwargs={'pk': self.agent.pk})
        data = {
            'new_status': 'SUSPENDU',
            'reason': 'Test suspension',
            'send_notification': False
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le changement
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.status, 'SUSPENDU')
        
        # Vérifier l'historique
        history = StatusHistory.objects.filter(user=self.agent).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.new_status, 'SUSPENDU')
    
    def test_reset_password(self):
        """Test réinitialisation de mot de passe"""
        self.client.force_authenticate(user=self.chef)
        url = reverse('user-reset-password', kwargs={'pk': self.agent.pk})
        data = {
            'new_password': 'ResetPassword@123',
            'force_change': True,
            'send_email': False
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier le nouveau mot de passe
        self.agent.refresh_from_db()
        self.assertTrue(self.agent.check_password('ResetPassword@123'))


class PermissionsTests(TestCase):
    """Tests pour le système de permissions"""
    
    def setUp(self):
        """Créer des utilisateurs de test"""
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin@123',
            role='SUPER_ADMIN'
        )
        
        self.chef = User.objects.create_user(
            username='chef_test',
            email='chef@test.com',
            password='Chef@123',
            role='CHEF_FACTURATION'
        )
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION'
        )
    
    def test_admin_has_all_permissions(self):
        """Test admin a toutes les permissions"""
        self.assertTrue(self.admin.has_permission('billing.publish'))
        self.assertTrue(self.admin.has_permission('billing.cancel'))
        self.assertTrue(self.admin.has_permission('any.permission'))
    
    def test_chef_has_specific_permissions(self):
        """Test chef a ses permissions spécifiques"""
        self.assertTrue(self.chef.has_permission('billing.publish'))
        self.assertTrue(self.chef.has_permission('accounts.create_agent'))
        self.assertTrue(self.chef.has_permission('tarifs.create'))
    
    def test_agent_limited_permissions(self):
        """Test agent a permissions limitées"""
        self.assertTrue(self.agent.has_permission('billing.publish'))
        self.assertFalse(self.agent.has_permission('billing.cancel'))
        self.assertFalse(self.agent.has_permission('accounts.create_agent'))
    
    def test_can_manage_user(self):
        """Test gestion d'utilisateurs"""
        agent2 = User.objects.create_user(
            username='agent2',
            email='agent2@test.com',
            password='Agent@123',
            role='AGENT_FACTURATION',
            created_by=self.chef
        )
        
        # Admin peut gérer tout le monde
        self.assertTrue(self.admin.can_manage_user(self.chef))
        self.assertTrue(self.admin.can_manage_user(self.agent))
        
        # Chef peut gérer ses agents
        self.assertTrue(self.chef.can_manage_user(agent2))
        self.assertFalse(self.chef.can_manage_user(self.agent))  # pas créé par lui
        
        # Agent ne peut gérer personne
        self.assertFalse(self.agent.can_manage_user(agent2))


def run_tests():
    """Fonction helper pour lancer les tests"""
    import sys
    from django.core.management import call_command
    
    print("🧪 Lancement des tests Phase 1...")
    print("=" * 60)
    
    call_command('test', 'accounts', verbosity=2)
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")


if __name__ == '__main__':
    run_tests()
