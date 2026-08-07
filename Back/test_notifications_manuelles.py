"""
Script de test manuel pour les notifications Email et SMS
Exécuter avec : python manage.py shell < test_notifications_manuelles.py
Ou directement : python test_notifications_manuelles.py (après avoir configuré Django)
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from accounts.models import User
from billing.models import Company, Line, Invoice, NotificationFacture
from billing.services.notification_service import notifier_facture


def creer_donnees_test():
    """Créer ou récupérer les données de test"""
    print("\n" + "="*70)
    print("CRÉATION DES DONNÉES DE TEST")
    print("="*70)
    
    # Créer ou récupérer un payeur de test
    payeur, created = User.objects.get_or_create(
        username='test_payeur_notif',
        defaults={
            'email': 'benoitbal55@gmail.com',  # VOTRE EMAIL
            'password': 'testpass123',
            'role': 'PAYEUR',
            'first_name': 'Payeur',
            'last_name': 'Test',
            'telephone': '22879983759'  # VOTRE NUMÉRO (format international)
        }
    )
    if created:
        payeur.set_password('testpass123')
        payeur.save()
        print(f"✅ Payeur créé : {payeur.username} ({payeur.email})")
    else:
        print(f"ℹ️  Payeur existant : {payeur.username} ({payeur.email})")
    
    # Créer ou récupérer une entreprise de test
    company, created = Company.objects.get_or_create(
        compte='TEST-NOTIF-001',
        defaults={
            'raison_sociale': 'Test Notifications SARL',
            'categorie': 'PE',
            'payeur': payeur,
            'email_facturation': 'benoitbal55@gmail.com'
        }
    )
    if created:
        print(f"✅ Entreprise créée : {company.compte} ({company.raison_sociale})")
    else:
        print(f"ℹ️  Entreprise existante : {company.compte} ({company.raison_sociale})")
    
    # Créer une nouvelle facture de test
    numero_facture = f'FAC-TEST-NOTIF-{date.today().strftime("%Y%m%d")}'
    
    # Supprimer les anciennes factures de test pour éviter les doublons
    Invoice.objects.filter(numero_facture__startswith='FAC-TEST-NOTIF').delete()
    
    invoice = Invoice.objects.create(
        company=company,
        numero_facture=numero_facture,
        periode_debut=date.today() - timedelta(days=30),
        periode_fin=date.today(),
        montant_ht=Decimal('50000'),
        montant_tva=Decimal('9000'),
        montant_ttc=Decimal('59000'),
        date_echeance=date.today() + timedelta(days=30),
        statut='PUBLIEE'
    )
    print(f"✅ Facture créée : {invoice.numero_facture} (Montant : {invoice.montant_ttc} FCFA)")
    
    return payeur, company, invoice


def test_configuration():
    """Vérifier la configuration Email et SMS"""
    print("\n" + "="*70)
    print("VÉRIFICATION DE LA CONFIGURATION")
    print("="*70)
    
    from django.conf import settings
    
    # Configuration Email
    print("\n📧 Configuration Email (SMTP):")
    print(f"  - EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  - EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"  - EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"  - EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"  - DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    if not settings.EMAIL_HOST or not settings.DEFAULT_FROM_EMAIL:
        print("  ⚠️  ATTENTION : Configuration Email incomplète !")
        return False
    else:
        print("  ✅ Configuration Email OK")
    
    # Configuration SMS
    print("\n📱 Configuration SMS (Vonage):")
    print(f"  - VONAGE_API_KEY: {settings.VONAGE_API_KEY}")
    print(f"  - VONAGE_API_SECRET: {'*' * len(settings.VONAGE_API_SECRET) if settings.VONAGE_API_SECRET else '(vide)'}")
    print(f"  - VONAGE_SMS_FROM: {settings.VONAGE_SMS_FROM}")
    
    if not all([settings.VONAGE_API_KEY, settings.VONAGE_API_SECRET, settings.VONAGE_SMS_FROM]):
        print("  ⚠️  ATTENTION : Configuration SMS incomplète !")
        return False
    else:
        print("  ✅ Configuration SMS OK")
    
    return True


def test_envoi_email(invoice):
    """Tester l'envoi d'un email réel"""
    print("\n" + "="*70)
    print("TEST ENVOI EMAIL")
    print("="*70)
    
    print(f"\n📧 Envoi d'un email pour la facture {invoice.numero_facture}...")
    print(f"   Destinataire : {invoice.company.payeur.email}")
    
    try:
        resultats = notifier_facture(invoice, ['EMAIL'])
        
        if resultats:
            notif = resultats[0]
            print(f"\n✅ Email envoyé avec succès !")
            print(f"   - Canal : {notif.canal}")
            print(f"   - Destinataire : {notif.destinataire}")
            print(f"   - Statut : {notif.statut}")
            print(f"   - Date : {notif.date_envoi}")
            
            if notif.statut == 'ENVOYEE':
                print(f"\n🎉 SUCCESS ! Vérifiez votre boîte email : {notif.destinataire}")
                return True
            else:
                print(f"\n❌ ÉCHEC : {notif.detail}")
                return False
        else:
            print("\n❌ Aucun résultat retourné")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_envoi_sms(invoice):
    """Tester l'envoi d'un SMS réel"""
    print("\n" + "="*70)
    print("TEST ENVOI SMS")
    print("="*70)
    
    telephone = invoice.company.payeur.telephone
    print(f"\n📱 Envoi d'un SMS pour la facture {invoice.numero_facture}...")
    print(f"   Destinataire : {telephone}")
    
    if not telephone:
        print("❌ Aucun numéro de téléphone configuré pour le payeur")
        return False
    
    try:
        resultats = notifier_facture(invoice, ['SMS'])
        
        if resultats:
            notif = resultats[0]
            print(f"\n✅ SMS traité !")
            print(f"   - Canal : {notif.canal}")
            print(f"   - Destinataire : {notif.destinataire}")
            print(f"   - Statut : {notif.statut}")
            print(f"   - Date : {notif.date_envoi}")
            
            if notif.statut == 'ENVOYEE':
                print(f"\n🎉 SUCCESS ! Vérifiez votre téléphone : {notif.destinataire}")
                print(f"   ⚠️  Attention : L'envoi SMS coûte ~0.05€ via Vonage")
                return True
            else:
                print(f"\n❌ ÉCHEC : {notif.detail}")
                return False
        else:
            print("\n❌ Aucun résultat retourné")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_envoi_multicanal(invoice):
    """Tester l'envoi simultané Email + SMS"""
    print("\n" + "="*70)
    print("TEST ENVOI MULTI-CANAL (EMAIL + SMS)")
    print("="*70)
    
    print(f"\n📧📱 Envoi Email + SMS pour la facture {invoice.numero_facture}...")
    print(f"   Email : {invoice.company.payeur.email}")
    print(f"   SMS : {invoice.company.payeur.telephone}")
    
    try:
        resultats = notifier_facture(invoice, ['EMAIL', 'SMS'])
        
        if resultats:
            print(f"\n✅ {len(resultats)} notification(s) traitée(s) :")
            
            success_count = 0
            for notif in resultats:
                status_icon = "✅" if notif.statut == 'ENVOYEE' else "❌"
                print(f"\n   {status_icon} {notif.canal}:")
                print(f"      - Destinataire : {notif.destinataire}")
                print(f"      - Statut : {notif.statut}")
                if notif.detail:
                    print(f"      - Détail : {notif.detail}")
                
                if notif.statut == 'ENVOYEE':
                    success_count += 1
            
            print(f"\n📊 Résultat : {success_count}/{len(resultats)} notification(s) envoyée(s) avec succès")
            return success_count > 0
        else:
            print("\n❌ Aucun résultat retourné")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def afficher_historique(invoice):
    """Afficher l'historique des notifications pour cette facture"""
    print("\n" + "="*70)
    print("HISTORIQUE DES NOTIFICATIONS")
    print("="*70)
    
    notifications = NotificationFacture.objects.filter(invoice=invoice).order_by('-date_envoi')
    
    if notifications.exists():
        print(f"\n📋 {notifications.count()} notification(s) enregistrée(s) :\n")
        
        for i, notif in enumerate(notifications, 1):
            status_icon = {
                'ENVOYEE': '✅',
                'ECHEC': '❌',
                'NON_CONFIGUREE': '⚠️'
            }.get(notif.statut, '❓')
            
            print(f"{i}. {status_icon} {notif.canal} - {notif.statut}")
            print(f"   - Destinataire : {notif.destinataire}")
            print(f"   - Date : {notif.date_envoi.strftime('%d/%m/%Y %H:%M:%S')}")
            if notif.detail:
                print(f"   - Détail : {notif.detail}")
            print()
    else:
        print("\nℹ️  Aucune notification enregistrée pour cette facture")


def menu_principal():
    """Menu interactif"""
    print("\n" + "="*70)
    print("MENU DE TEST DES NOTIFICATIONS")
    print("="*70)
    print("\n1. Tester Email uniquement")
    print("2. Tester SMS uniquement")
    print("3. Tester Email + SMS (multi-canal)")
    print("4. Afficher l'historique des notifications")
    print("5. Créer de nouvelles données de test")
    print("0. Quitter")
    
    choix = input("\nVotre choix : ").strip()
    return choix


def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("🧪 SCRIPT DE TEST DES NOTIFICATIONS EMAIL ET SMS")
    print("="*70)
    print("\n⚠️  ATTENTION : Ce script envoie de VRAIES notifications !")
    print("   - Les emails seront envoyés via Gmail SMTP")
    print("   - Les SMS seront envoyés via Vonage (coût : ~0.05€/SMS)")
    
    # Vérifier la configuration
    if not test_configuration():
        print("\n❌ Configuration incomplète. Vérifiez votre fichier .env")
        return
    
    # Créer les données de test
    payeur, company, invoice = creer_donnees_test()
    
    # Mode interactif
    while True:
        choix = menu_principal()
        
        if choix == '1':
            test_envoi_email(invoice)
        elif choix == '2':
            confirm = input("\n⚠️  Confirmer l'envoi SMS (coût ~0.05€) ? (oui/non) : ").strip().lower()
            if confirm == 'oui':
                test_envoi_sms(invoice)
            else:
                print("❌ Envoi SMS annulé")
        elif choix == '3':
            confirm = input("\n⚠️  Confirmer l'envoi Email + SMS (coût ~0.05€ pour SMS) ? (oui/non) : ").strip().lower()
            if confirm == 'oui':
                test_envoi_multicanal(invoice)
            else:
                print("❌ Envoi annulé")
        elif choix == '4':
            afficher_historique(invoice)
        elif choix == '5':
            payeur, company, invoice = creer_donnees_test()
        elif choix == '0':
            print("\n👋 Au revoir !")
            break
        else:
            print("\n❌ Choix invalide")
        
        input("\nAppuyez sur Entrée pour continuer...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption par l'utilisateur. Au revoir !")
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {str(e)}")
        import traceback
        traceback.print_exc()
