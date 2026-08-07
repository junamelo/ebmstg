"""
Script de test d'envoi réel Email + SMS
Email: yendoiboure@gmail.com
SMS: +22892628287
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
from billing.models import Company, Invoice
from billing.services.notification_service import notifier_facture


def creer_utilisateur_test():
    """Créer un utilisateur de test avec les coordonnées spécifiées"""
    print("\n" + "="*70)
    print("CRÉATION DE L'UTILISATEUR DE TEST")
    print("="*70)
    
    # Créer ou mettre à jour l'utilisateur
    user, created = User.objects.update_or_create(
        username='yendoi_test',
        defaults={
            'email': 'yendoiboure@gmail.com',
            'role': 'PAYEUR',
            'first_name': 'Yendoi',
            'last_name': 'Bouré',
            'telephone': '22892628287',  # Format sans le +
            'is_active': True
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Utilisateur créé : {user.username}")
    else:
        print(f"ℹ️  Utilisateur mis à jour : {user.username}")
    
    print(f"   - Email : {user.email}")
    print(f"   - Téléphone : {user.telephone}")
    
    return user


def creer_facture_test(user):
    """Créer une facture de test"""
    print("\n" + "="*70)
    print("CRÉATION DE LA FACTURE DE TEST")
    print("="*70)
    
    # Créer ou récupérer l'entreprise
    company, created = Company.objects.get_or_create(
        compte='TEST-YENDOI-001',
        defaults={
            'raison_sociale': 'Test Envoi Notifications',
            'categorie': 'PE',
            'payeur': user,
            'email_facturation': 'yendoiboure@gmail.com'
        }
    )
    
    if created:
        print(f"✅ Entreprise créée : {company.compte}")
    else:
        print(f"ℹ️  Entreprise existante : {company.compte}")
    
    # Supprimer les anciennes factures de test
    Invoice.objects.filter(numero_facture__startswith='FAC-TEST-YENDOI').delete()
    
    # Créer une nouvelle facture
    invoice = Invoice.objects.create(
        company=company,
        numero_facture=f'FAC-TEST-YENDOI-{date.today().strftime("%Y%m%d")}',
        periode_debut=date.today() - timedelta(days=30),
        periode_fin=date.today(),
        montant_ht=Decimal('50000'),
        montant_tva=Decimal('9000'),
        montant_ttc=Decimal('59000'),
        date_echeance=date.today() + timedelta(days=30),
        statut='PUBLIEE'
    )
    
    print(f"✅ Facture créée : {invoice.numero_facture}")
    print(f"   - Montant : {invoice.montant_ttc} FCFA")
    print(f"   - Période : du {invoice.periode_debut} au {invoice.periode_fin}")
    
    return invoice


def test_email(invoice):
    """Tester l'envoi d'email"""
    print("\n" + "="*70)
    print("📧 TEST ENVOI EMAIL")
    print("="*70)
    print(f"Destinataire : yendoiboure@gmail.com")
    print(f"Facture : {invoice.numero_facture}")
    print(f"Montant : {invoice.montant_ttc} FCFA")
    print("\nEnvoi en cours...")
    
    try:
        resultats = notifier_facture(invoice, ['EMAIL'])
        
        if resultats and len(resultats) > 0:
            notif = resultats[0]
            print(f"\n{'✅' if notif.statut == 'ENVOYEE' else '❌'} Résultat : {notif.statut}")
            print(f"   - Canal : {notif.canal}")
            print(f"   - Destinataire : {notif.destinataire}")
            print(f"   - Date : {notif.date_envoi}")
            
            if notif.detail:
                print(f"   - Détail : {notif.detail}")
            
            if notif.statut == 'ENVOYEE':
                print(f"\n🎉 EMAIL ENVOYÉ AVEC SUCCÈS !")
                print(f"   Vérifiez la boîte : yendoiboure@gmail.com")
                print(f"   (Vérifiez aussi les spams si besoin)")
                return True
            else:
                print(f"\n❌ ÉCHEC de l'envoi")
                return False
        else:
            print("\n❌ Aucun résultat retourné")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_sms(invoice):
    """Tester l'envoi de SMS"""
    print("\n" + "="*70)
    print("📱 TEST ENVOI SMS")
    print("="*70)
    print(f"Destinataire : +228 92 62 82 87")
    print(f"Facture : {invoice.numero_facture}")
    print(f"Montant : {invoice.montant_ttc} FCFA")
    print("\n⚠️  ATTENTION : Cet envoi coûtera environ 0.05€ via Vonage")
    
    confirm = input("\nConfirmer l'envoi du SMS ? (oui/non) : ").strip().lower()
    
    if confirm != 'oui':
        print("❌ Envoi SMS annulé")
        return False
    
    print("\nEnvoi en cours...")
    
    try:
        resultats = notifier_facture(invoice, ['SMS'])
        
        if resultats and len(resultats) > 0:
            notif = resultats[0]
            print(f"\n{'✅' if notif.statut == 'ENVOYEE' else '❌'} Résultat : {notif.statut}")
            print(f"   - Canal : {notif.canal}")
            print(f"   - Destinataire : {notif.destinataire}")
            print(f"   - Date : {notif.date_envoi}")
            
            if notif.detail:
                print(f"   - Détail : {notif.detail}")
            
            if notif.statut == 'ENVOYEE':
                print(f"\n🎉 SMS ENVOYÉ AVEC SUCCÈS !")
                print(f"   Vérifiez le téléphone : +228 92 62 82 87")
                print(f"   (Délai de réception : 5-30 secondes)")
                return True
            else:
                print(f"\n❌ ÉCHEC de l'envoi")
                return False
        else:
            print("\n❌ Aucun résultat retourné")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multicanal(invoice):
    """Tester l'envoi Email + SMS"""
    print("\n" + "="*70)
    print("📧📱 TEST ENVOI EMAIL + SMS")
    print("="*70)
    print(f"Email : yendoiboure@gmail.com")
    print(f"SMS : +228 92 62 82 87")
    print(f"Facture : {invoice.numero_facture}")
    print(f"Montant : {invoice.montant_ttc} FCFA")
    print("\n⚠️  ATTENTION : Le SMS coûtera environ 0.05€ via Vonage")
    
    confirm = input("\nConfirmer l'envoi Email + SMS ? (oui/non) : ").strip().lower()
    
    if confirm != 'oui':
        print("❌ Envoi annulé")
        return False
    
    print("\nEnvoi en cours...")
    
    try:
        resultats = notifier_facture(invoice, ['EMAIL', 'SMS'])
        
        if resultats and len(resultats) > 0:
            print(f"\n✅ {len(resultats)} notification(s) traitée(s) :\n")
            
            success_count = 0
            for notif in resultats:
                status_icon = "✅" if notif.statut == 'ENVOYEE' else "❌"
                print(f"{status_icon} {notif.canal}:")
                print(f"   - Destinataire : {notif.destinataire}")
                print(f"   - Statut : {notif.statut}")
                print(f"   - Date : {notif.date_envoi}")
                
                if notif.detail:
                    print(f"   - Détail : {notif.detail}")
                
                if notif.statut == 'ENVOYEE':
                    success_count += 1
                print()
            
            print(f"📊 Résultat : {success_count}/{len(resultats)} notification(s) envoyée(s)")
            
            if success_count > 0:
                print("\n🎉 AU MOINS UN CANAL A RÉUSSI !")
                print("   - Vérifiez yendoiboure@gmail.com pour l'email")
                print("   - Vérifiez +228 92 62 82 87 pour le SMS")
                return True
            else:
                return False
        else:
            print("\n❌ Aucun résultat retourné")
            return False
            
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verifier_configuration():
    """Vérifier la configuration Email et SMS"""
    print("\n" + "="*70)
    print("⚙️  VÉRIFICATION DE LA CONFIGURATION")
    print("="*70)
    
    from django.conf import settings
    
    # Email
    print("\n📧 Configuration Email:")
    email_ok = True
    if settings.EMAIL_HOST:
        print(f"   ✅ EMAIL_HOST: {settings.EMAIL_HOST}")
    else:
        print(f"   ❌ EMAIL_HOST non configuré")
        email_ok = False
    
    if settings.DEFAULT_FROM_EMAIL:
        print(f"   ✅ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    else:
        print(f"   ❌ DEFAULT_FROM_EMAIL non configuré")
        email_ok = False
    
    # SMS
    print("\n📱 Configuration SMS:")
    sms_ok = True
    if settings.VONAGE_API_KEY:
        print(f"   ✅ VONAGE_API_KEY: {settings.VONAGE_API_KEY}")
    else:
        print(f"   ❌ VONAGE_API_KEY non configuré")
        sms_ok = False
    
    if settings.VONAGE_SMS_FROM:
        print(f"   ✅ VONAGE_SMS_FROM: {settings.VONAGE_SMS_FROM}")
    else:
        print(f"   ❌ VONAGE_SMS_FROM non configuré")
        sms_ok = False
    
    print()
    return email_ok and sms_ok


def menu():
    """Menu principal"""
    print("\n" + "="*70)
    print("MENU DE TEST")
    print("="*70)
    print("\n1. Envoyer EMAIL uniquement à yendoiboure@gmail.com")
    print("2. Envoyer SMS uniquement au +228 92 62 82 87")
    print("3. Envoyer EMAIL + SMS (les deux)")
    print("0. Quitter")
    
    return input("\nVotre choix : ").strip()


def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("🧪 TEST D'ENVOI RÉEL - EMAIL & SMS")
    print("="*70)
    print("\nDestinataires:")
    print("   📧 Email : yendoiboure@gmail.com")
    print("   📱 SMS : +228 92 62 82 87")
    print("\n⚠️  ATTENTION : Ce script envoie de VRAIES notifications !")
    
    # Vérifier la configuration
    if not verifier_configuration():
        print("\n❌ Configuration incomplète. Vérifiez votre fichier .env")
        return
    
    # Créer les données de test
    user = creer_utilisateur_test()
    invoice = creer_facture_test(user)
    
    # Menu interactif
    while True:
        choix = menu()
        
        if choix == '1':
            test_email(invoice)
        elif choix == '2':
            test_sms(invoice)
        elif choix == '3':
            test_multicanal(invoice)
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
