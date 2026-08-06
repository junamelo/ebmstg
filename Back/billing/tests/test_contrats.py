"""
Tests pour la gestion des contrats et commerciaux
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from billing.models import Commercial, Company, Line, AuditContrat
import datetime


def creer_agent():
    return User.objects.create_user(
        username='agent_test',
        email='agent@test.com',
        password='testpass123',
        role='AGENT_FACTURATION',
        status='ACTIF',
        est_actif=True
    )


class CommercialTests(APITestCase):
    def setUp(self):
        self.agent = creer_agent()
        self.client.force_authenticate(user=self.agent)

    def test_creation_commercial(self):
        data = {
            'nom': 'DUPONT',
            'prenom': 'Jean',
            'matricule': 'COM001',
            'telephone': '90000001',
            'email': 'jean.dupont@moov.tg'
        }
        response = self.client.post('/api/billing/commerciaux/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['matricule'], 'COM001')

    def test_matricule_unique(self):
        Commercial.objects.create(nom='A', prenom='B', matricule='COM002')
        data = {'nom': 'C', 'prenom': 'D', 'matricule': 'COM002'}
        response = self.client.post('/api/billing/commerciaux/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ContratTests(APITestCase):
    def setUp(self):
        self.agent = creer_agent()
        self.client.force_authenticate(user=self.agent)
        self.commercial = Commercial.objects.create(
            nom='TEST', prenom='Commercial', matricule='COM100'
        )

    def test_creation_contrat_avec_commercial(self):
        data = {
            'compte': 'A26000001',
            'raison_sociale': 'ENTREPRISE TEST',
            'categorie': 'PE',
            'commercial': self.commercial.id,
            'mode_reglement': 'VIREMENT',
            'statut_factures': 'EN_ATTENTE',
        }
        response = self.client.post('/api/billing/companies/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['commercial'], self.commercial.id)

    def test_code_contrat_unique(self):
        Company.objects.create(compte='A26000002', raison_sociale='EXISTANT')
        data = {'compte': 'A26000002', 'raison_sociale': 'DOUBLON', 'categorie': 'PE'}
        response = self.client.post('/api/billing/companies/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resiliation_valide(self):
        company = Company.objects.create(
            compte='A26000003',
            raison_sociale='A RESILIER',
            date_effet=datetime.date(2024, 1, 1)
        )
        data = {
            'date_resiliation': '2024-06-01',
            'motif_resiliation': 'Départ client'
        }
        response = self.client.post(f'/api/billing/companies/{company.id}/resilier/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company.refresh_from_db()
        self.assertTrue(company.est_resilie)
        self.assertEqual(company.statut_factures, 'CLOS')

    def test_resiliation_date_anterieure_date_effet(self):
        company = Company.objects.create(
            compte='A26000004',
            raison_sociale='TEST DATE',
            date_effet=datetime.date(2024, 6, 1)
        )
        data = {
            'date_resiliation': '2024-01-01',
            'motif_resiliation': 'Test'
        }
        response = self.client.post(f'/api/billing/companies/{company.id}/resilier/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_heritage_services_nouvelle_ligne(self):
        company = Company.objects.create(
            compte='A26000005',
            raison_sociale='TEST HERITAGE',
            facture_detaillee_defaut=True,
            roaming_defaut=True,
            internet_defaut=False,
        )
        data = {
            'company': company.id,
            'msisdn': '90000099',
            'cycle': 'HYB',
        }
        response = self.client.post('/api/billing/lines/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        line = Line.objects.get(msisdn='90000099')
        self.assertTrue(line.facture_detaillee)
        self.assertTrue(line.est_roaming)
        self.assertFalse(line.est_internet)

    def test_modification_ligne_sans_modifier_contrat(self):
        company = Company.objects.create(
            compte='A26000006',
            raison_sociale='TEST LIGNE',
            facture_detaillee_defaut=True,
        )
        line = Line.objects.create(
            company=company, msisdn='90000098', cycle='HYB',
            facture_detaillee=True
        )
        response = self.client.patch(
            f'/api/billing/lines/{line.id}/',
            {'facture_detaillee': False},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        line.refresh_from_db()
        company.refresh_from_db()
        self.assertFalse(line.facture_detaillee)
        self.assertTrue(company.facture_detaillee_defaut)  # Contrat inchangé

    def test_audit_creation_contrat(self):
        data = {
            'compte': 'A26000007',
            'raison_sociale': 'AUDIT TEST',
            'categorie': 'PE',
        }
        response = self.client.post('/api/billing/companies/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        company_id = response.data['id']
        company = Company.objects.get(id=company_id)
        audits = AuditContrat.objects.filter(company=company)
        self.assertTrue(audits.exists())
        self.assertEqual(audits.first().type_action, 'CREATION')
