"""
Tests pour la fonctionnalité de résiliation de contrat
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from accounts.models import User
from billing.models import Company, AuditContrat


class ResiliationContratTests(TestCase):
    """Tests pour la résiliation de contrat"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = APIClient()
        
        # Créer un agent de facturation
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@moov.tg',
            password='testpass123',
            role='AGENT_FACTURATION',
            first_name='Agent',
            last_name='Test'
        )
        
        # Créer un payeur
        self.payeur = User.objects.create_user(
            username='payeur_test',
            email='payeur@example.com',
            password='testpass123',
            role='PAYEUR',
            first_name='Payeur',
            last_name='Test'
        )
        
        # Créer un contrat
        self.company = Company.objects.create(
            compte='CTR-TEST-001',
            raison_sociale='Entreprise Test SARL',
            categorie='PE',
            statut='ACTIF',
            date_effet=date.today() - timedelta(days=180),
            payeur=self.payeur
        )
        
    def test_resilier_contrat_success(self):
        """Test de résiliation réussie d'un contrat"""
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'date_resiliation': str(date.today() + timedelta(days=30)),
            'motif_resiliation': 'Fin de contrat - Demande client',
            'observation_resiliation': 'Client satisfait du service'
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['est_resilie'])
        self.assertEqual(response.data['motif_resiliation'], data['motif_resiliation'])
        self.assertEqual(response.data['observation_resiliation'], data['observation_resiliation'])
        self.assertEqual(response.data['statut_factures'], 'CLOS')
        
        # Vérifier que le contrat a été mis à jour en base
        self.company.refresh_from_db()
        self.assertTrue(self.company.est_resilie)
        self.assertEqual(str(self.company.date_resiliation), data['date_resiliation'])
        self.assertEqual(self.company.motif_resiliation, data['motif_resiliation'])
        self.assertEqual(self.company.statut_factures, 'CLOS')
        
        # Vérifier la traçabilité
        audit = AuditContrat.objects.filter(
            company=self.company,
            type_action='RESILIATION'
        ).first()
        
        self.assertIsNotNone(audit)
        self.assertEqual(audit.utilisateur, self.agent)
        self.assertIn('Contrat résilié', audit.description)
        
    def test_resilier_contrat_sans_observation(self):
        """Test de résiliation sans observation (champ optionnel)"""
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'date_resiliation': str(date.today() + timedelta(days=30)),
            'motif_resiliation': 'Liquidation judiciaire'
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['est_resilie'])
        self.assertEqual(response.data['observation_resiliation'], '')
        
    def test_resilier_contrat_deja_resilie(self):
        """Test de résiliation d'un contrat déjà résilié"""
        # Marquer le contrat comme déjà résilié
        self.company.est_resilie = True
        self.company.date_resiliation = date.today() - timedelta(days=10)
        self.company.motif_resiliation = 'Ancien motif'
        self.company.save()
        
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'date_resiliation': str(date.today()),
            'motif_resiliation': 'Nouveau motif'
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('déjà résilié', response.data['error'].lower())
        
    def test_resilier_sans_date_resiliation(self):
        """Test de résiliation sans date (champ obligatoire)"""
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'motif_resiliation': 'Test motif'
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('obligatoire', response.data['error'].lower())
        
    def test_resilier_sans_motif_resiliation(self):
        """Test de résiliation sans motif (champ obligatoire)"""
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'date_resiliation': str(date.today() + timedelta(days=30))
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('obligatoire', response.data['error'].lower())
        
    def test_resilier_date_invalide(self):
        """Test de résiliation avec format de date invalide"""
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'date_resiliation': '31/08/2026',  # Format invalide
            'motif_resiliation': 'Test'
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('format', response.data['error'].lower())
        
    def test_resilier_date_anterieure_date_effet(self):
        """Test de résiliation avec date antérieure à la date d'effet"""
        self.client.force_authenticate(user=self.agent)
        
        # Date de résiliation antérieure à la date d'effet
        date_resiliation = self.company.date_effet - timedelta(days=10)
        
        data = {
            'date_resiliation': str(date_resiliation),
            'motif_resiliation': 'Test'
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('antérieure', response.data['error'].lower())
        
    def test_resilier_permission_payeur_refuse(self):
        """Test que le payeur ne peut pas résilier un contrat"""
        self.client.force_authenticate(user=self.payeur)
        
        data = {
            'date_resiliation': str(date.today() + timedelta(days=30)),
            'motif_resiliation': 'Test'
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        # Le payeur n'a pas la permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_resilier_sans_authentification(self):
        """Test de résiliation sans authentification"""
        data = {
            'date_resiliation': str(date.today() + timedelta(days=30)),
            'motif_resiliation': 'Test'
        }
        
        response = self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_resilier_contrat_inexistant(self):
        """Test de résiliation d'un contrat qui n'existe pas"""
        self.client.force_authenticate(user=self.agent)
        
        data = {
            'date_resiliation': str(date.today() + timedelta(days=30)),
            'motif_resiliation': 'Test'
        }
        
        response = self.client.post(
            '/api/billing/companies/99999/resilier/',
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_motifs_resiliation_varies(self):
        """Test de différents motifs de résiliation"""
        motifs = [
            'Fin de contrat - Demande client',
            'Liquidation judiciaire',
            'Déménagement hors zone de couverture',
            'Insatisfaction client - Service',
            'Offre concurrente plus avantageuse',
            'Résiliation pour non-paiement',
            'Fermeture définitive de l\'entreprise',
            'Fusion avec une autre entreprise'
        ]
        
        for i, motif in enumerate(motifs):
            # Créer un nouveau contrat pour chaque test
            company = Company.objects.create(
                compte=f'CTR-TEST-{i+100}',
                raison_sociale=f'Entreprise Test {i+1}',
                categorie='PE',
                statut='ACTIF',
                date_effet=date.today() - timedelta(days=180)
            )
            
            self.client.force_authenticate(user=self.agent)
            
            data = {
                'date_resiliation': str(date.today() + timedelta(days=30)),
                'motif_resiliation': motif
            }
            
            response = self.client.post(
                f'/api/billing/companies/{company.id}/resilier/',
                data,
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['motif_resiliation'], motif)


class HistoriqueResiliationTests(TestCase):
    """Tests pour l'historique des résiliations"""
    
    def setUp(self):
        """Configuration initiale"""
        self.client = APIClient()
        
        self.agent = User.objects.create_user(
            username='agent_test',
            email='agent@moov.tg',
            password='testpass123',
            role='AGENT_FACTURATION'
        )
        
        self.company = Company.objects.create(
            compte='CTR-HIST-001',
            raison_sociale='Test Historique',
            categorie='PE',
            date_effet=date.today() - timedelta(days=180)
        )
        
    def test_historique_apres_resiliation(self):
        """Test que la résiliation est enregistrée dans l'historique"""
        self.client.force_authenticate(user=self.agent)
        
        # Résilier le contrat
        data = {
            'date_resiliation': str(date.today() + timedelta(days=30)),
            'motif_resiliation': 'Test historique'
        }
        
        self.client.post(
            f'/api/billing/companies/{self.company.id}/resilier/',
            data,
            format='json'
        )
        
        # Récupérer l'historique
        response = self.client.get(
            f'/api/billing/companies/{self.company.id}/historique/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Vérifier qu'il y a au moins une entrée de résiliation
        results = response.data['results']
        resiliation_audit = [a for a in results if a['type_action'] == 'RESILIATION']
        
        self.assertTrue(len(resiliation_audit) > 0)
        self.assertIn('Contrat résilié', resiliation_audit[0]['description'])


# Script de lancement des tests
if __name__ == '__main__':
    import sys
    import django
    import os
    
    # Configuration Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
    django.setup()
    
    # Lancer les tests
    from django.core.management import call_command
    call_command('test', 'billing.test_resiliation', verbosity=2)
