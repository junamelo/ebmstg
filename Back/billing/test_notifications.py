"""
Tests pour les notifications Email et SMS
Valide l'envoi de notifications de disponibilité de factures
"""
from django.test import TestCase
from django.conf import settings
from django.core import mail
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import date, timedelta

from accounts.models import User
from billing.models import Company, Line, Invoice, NotificationFacture
from billing.services.notification_service import notifier_facture


class EmailNotificationTestCase(TestCase):
    """Tests pour les notifications par email"""
    
    def setUp(self):
        """Créer les données de test"""
        # Créer un payeur avec email
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
            payeur=self.payeur,
            email_facturation='contact@company.com'
        )
        
        # Créer une facture
        self.invoice = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-TEST-001',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ht=Decimal('10000'),
            montant_tva=Decimal('1800'),
            montant_ttc=Decimal('11800'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
    
    def test_email_configuration_valide(self):
        """Test : Les paramètres SMTP sont bien configurés"""
        self.assertTrue(hasattr(settings, 'EMAIL_HOST'))
        self.assertTrue(hasattr(settings, 'EMAIL_PORT'))
        self.assertTrue(hasattr(settings, 'EMAIL_HOST_USER'))
        self.assertTrue(hasattr(settings, 'DEFAULT_FROM_EMAIL'))
        # En mode test, Django utilise le backend locmem automatiquement
        self.assertIn('EmailBackend', settings.EMAIL_BACKEND)
    
    def test_envoi_email_payeur(self):
        """Test : Envoi d'email au payeur"""
        # Envoyer la notification
        resultats = notifier_facture(self.invoice, ['EMAIL'])
        
        # Vérifier qu'un résultat a été créé
        self.assertEqual(len(resultats), 1)
        notification = resultats[0]
        
        # Vérifier que la notification a été enregistrée
        self.assertEqual(notification.canal, 'EMAIL')
        self.assertEqual(notification.destinataire, 'payeur@test.com')
        self.assertEqual(notification.statut, 'ENVOYEE')
        
        # Vérifier qu'un email a été envoyé (dans la boîte de test Django)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('FAC-TEST-001', email.body)
        self.assertEqual(email.to, ['payeur@test.com'])
    
    def test_envoi_email_employe(self):
        """Test : Envoi d'email à un employé"""
        # Créer un employé
        employe = User.objects.create_user(
            username='employe1',
            email='employe@test.com',
            password='testpass123',
            role='EMPLOYE'
        )
        
        # Créer une ligne avec cet employé
        ligne = Line.objects.create(
            company=self.company,
            msisdn='70111111',
            utilisateur='Employé Test',
            cycle='HYB',
            forfait=Decimal('5000'),
            employe=employe
        )
        
        # Créer une facture pour cette ligne
        invoice_ligne = Invoice.objects.create(
            company=self.company,
            line=ligne,
            numero_facture='FAC-LINE-001',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('5900'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
        
        # Envoyer la notification
        resultats = notifier_facture(invoice_ligne, ['EMAIL'])
        
        # Vérifier que l'email a été envoyé à l'employé
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0].destinataire, 'employe@test.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['employe@test.com'])
    
    def test_email_fallback_vers_email_facturation(self):
        """Test : Si l'utilisateur n'a pas d'email, utiliser email_facturation de la company"""
        # Créer un payeur sans email
        payeur_sans_email = User.objects.create_user(
            username='payeur_no_email',
            email='',  # Pas d'email
            password='testpass123',
            role='PAYEUR'
        )
        
        company = Company.objects.create(
            compte='A0000002',
            raison_sociale='Company 2',
            categorie='PE',
            payeur=payeur_sans_email,
            email_facturation='facturation@company2.com'
        )
        
        invoice = Invoice.objects.create(
            company=company,
            numero_facture='FAC-002',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('8000'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
        
        # Envoyer la notification
        resultats = notifier_facture(invoice, ['EMAIL'])
        
        # Vérifier que l'email a été envoyé à l'adresse de facturation
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0].destinataire, 'facturation@company2.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['facturation@company2.com'])
    
    def test_email_sans_destinataire(self):
        """Test : Gestion du cas où il n'y a aucun destinataire"""
        # Créer un payeur sans email et une company sans email_facturation
        payeur_sans_email = User.objects.create_user(
            username='payeur_no_email2',
            email='',
            password='testpass123',
            role='PAYEUR'
        )
        
        company = Company.objects.create(
            compte='A0000003',
            raison_sociale='Company 3',
            categorie='PE',
            payeur=payeur_sans_email,
            email_facturation=''  # Pas d'email non plus
        )
        
        invoice = Invoice.objects.create(
            company=company,
            numero_facture='FAC-003',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('8000'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
        
        # Envoyer la notification
        resultats = notifier_facture(invoice, ['EMAIL'])
        
        # Vérifier que le statut est ECHEC
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0].statut, 'ECHEC')
        self.assertIn('Aucune adresse e-mail', resultats[0].detail)
        
        # Vérifier qu'aucun email n'a été envoyé
        self.assertEqual(len(mail.outbox), 0)


class SMSNotificationTestCase(TestCase):
    """Tests pour les notifications par SMS"""
    
    def setUp(self):
        """Créer les données de test"""
        # Créer un payeur avec téléphone
        self.payeur = User.objects.create_user(
            username='payeur_sms',
            email='payeur@test.com',
            password='testpass123',
            role='PAYEUR',
            telephone='22879000001'
        )
        
        # Créer une entreprise
        self.company = Company.objects.create(
            compte='A0000010',
            raison_sociale='Test Company SMS',
            categorie='PE',
            payeur=self.payeur
        )
        
        # Créer une facture
        self.invoice = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-SMS-001',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('15000'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
    
    def test_sms_configuration_valide(self):
        """Test : Les paramètres Vonage sont bien configurés"""
        self.assertTrue(hasattr(settings, 'VONAGE_API_KEY'))
        self.assertTrue(hasattr(settings, 'VONAGE_API_SECRET'))
        self.assertTrue(hasattr(settings, 'VONAGE_SMS_FROM'))
        
        # Vérifier que les valeurs sont définies (depuis .env)
        self.assertNotEqual(settings.VONAGE_API_KEY, '')
        self.assertNotEqual(settings.VONAGE_API_SECRET, '')
        self.assertNotEqual(settings.VONAGE_SMS_FROM, '')
    
    @patch('urllib.request.urlopen')
    def test_envoi_sms_succes(self, mock_urlopen):
        """Test : Envoi de SMS avec succès"""
        # Mocker la réponse Vonage (succès)
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"messages":[{"status":"0","message-id":"12345"}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Envoyer la notification
        resultats = notifier_facture(self.invoice, ['SMS'])
        
        # Vérifier qu'un résultat a été créé
        self.assertEqual(len(resultats), 1)
        notification = resultats[0]
        
        # Vérifier que la notification a été enregistrée
        self.assertEqual(notification.canal, 'SMS')
        self.assertEqual(notification.destinataire, '22879000001')
        self.assertEqual(notification.statut, 'ENVOYEE')
        
        # Vérifier que l'API Vonage a été appelée
        mock_urlopen.assert_called_once()
    
    @patch('urllib.request.urlopen')
    def test_envoi_sms_echec_vonage(self, mock_urlopen):
        """Test : Gestion de l'échec Vonage"""
        # Mocker la réponse Vonage (échec)
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"messages":[{"status":"5","error-text":"Invalid credentials"}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Envoyer la notification
        resultats = notifier_facture(self.invoice, ['SMS'])
        
        # Vérifier que le statut est ECHEC
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0].statut, 'ECHEC')
        self.assertIn('Vonage', resultats[0].detail)
    
    def test_sms_sans_telephone(self):
        """Test : Gestion du cas où il n'y a pas de téléphone"""
        # Créer un payeur sans téléphone
        payeur_sans_tel = User.objects.create_user(
            username='payeur_no_tel',
            email='payeur@test.com',
            password='testpass123',
            role='PAYEUR',
            telephone=''  # Pas de téléphone
        )
        
        company = Company.objects.create(
            compte='A0000011',
            raison_sociale='Company No Tel',
            categorie='PE',
            payeur=payeur_sans_tel
        )
        
        invoice = Invoice.objects.create(
            company=company,
            numero_facture='FAC-NO-TEL',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('8000'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
        
        # Envoyer la notification
        resultats = notifier_facture(invoice, ['SMS'])
        
        # Vérifier que le statut est ECHEC
        self.assertEqual(len(resultats), 1)
        self.assertEqual(resultats[0].statut, 'ECHEC')
        self.assertIn('Aucun numéro de téléphone', resultats[0].detail)


class NotificationMultiCanauxTestCase(TestCase):
    """Tests pour les notifications multi-canaux (EMAIL + SMS)"""
    
    def setUp(self):
        """Créer les données de test"""
        # Créer un payeur avec email ET téléphone
        self.payeur = User.objects.create_user(
            username='payeur_complet',
            email='payeur@test.com',
            password='testpass123',
            role='PAYEUR',
            telephone='22879000002'
        )
        
        # Créer une entreprise
        self.company = Company.objects.create(
            compte='A0000020',
            raison_sociale='Test Company Multi',
            categorie='PE',
            payeur=self.payeur
        )
        
        # Créer une facture
        self.invoice = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-MULTI-001',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('20000'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
    
    @patch('urllib.request.urlopen')
    def test_envoi_email_et_sms(self, mock_urlopen):
        """Test : Envoi simultané d'email et SMS"""
        # Mocker la réponse Vonage
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"messages":[{"status":"0"}]}'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        # Envoyer les deux canaux
        resultats = notifier_facture(self.invoice, ['EMAIL', 'SMS'])
        
        # Vérifier que 2 notifications ont été créées
        self.assertEqual(len(resultats), 2)
        
        # Vérifier l'email
        notif_email = next((r for r in resultats if r.canal == 'EMAIL'), None)
        self.assertIsNotNone(notif_email)
        self.assertEqual(notif_email.statut, 'ENVOYEE')
        self.assertEqual(notif_email.destinataire, 'payeur@test.com')
        
        # Vérifier le SMS
        notif_sms = next((r for r in resultats if r.canal == 'SMS'), None)
        self.assertIsNotNone(notif_sms)
        self.assertEqual(notif_sms.statut, 'ENVOYEE')
        self.assertEqual(notif_sms.destinataire, '22879000002')
        
        # Vérifier qu'un email a été envoyé
        self.assertEqual(len(mail.outbox), 1)
    
    def test_persistance_notifications(self):
        """Test : Les notifications sont bien enregistrées en base"""
        # Compter les notifications avant
        count_avant = NotificationFacture.objects.count()
        
        # Envoyer les notifications
        notifier_facture(self.invoice, ['EMAIL', 'SMS'])
        
        # Vérifier que 2 notifications ont été enregistrées
        count_apres = NotificationFacture.objects.count()
        self.assertEqual(count_apres, count_avant + 2)
        
        # Vérifier qu'elles sont liées à la bonne facture
        notifications = NotificationFacture.objects.filter(invoice=self.invoice)
        self.assertEqual(notifications.count(), 2)


class NotificationMessageTestCase(TestCase):
    """Tests pour le contenu des messages"""
    
    def setUp(self):
        """Créer les données de test"""
        self.payeur = User.objects.create_user(
            username='payeur_msg',
            email='payeur@test.com',
            password='testpass123',
            role='PAYEUR'
        )
        
        self.company = Company.objects.create(
            compte='A0000030',
            raison_sociale='Test Message',
            categorie='PE',
            payeur=self.payeur
        )
        
        self.invoice = Invoice.objects.create(
            company=self.company,
            numero_facture='FAC-MSG-12345',
            periode_debut=date.today() - timedelta(days=30),
            periode_fin=date.today(),
            montant_ttc=Decimal('25000'),
            date_echeance=date.today() + timedelta(days=30),
            statut='PUBLIEE'
        )
    
    def test_contenu_email(self):
        """Test : Le contenu de l'email est correct"""
        # Envoyer l'email
        notifier_facture(self.invoice, ['EMAIL'])
        
        # Vérifier le contenu
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        
        # Vérifier le sujet
        self.assertEqual(email.subject, 'Votre facture Moov Africa est disponible')
        
        # Vérifier que le numéro de facture est dans le corps
        self.assertIn('FAC-MSG-12345', email.body)
        self.assertIn('disponible', email.body.lower())
        self.assertIn('portail', email.body.lower())

