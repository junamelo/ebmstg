"""
Script de test SMS final - Format validé
Envoie un SMS au numéro +228 92 62 82 87 (yendoiboure@gmail.com)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from accounts.models import User
from billing.models import Company, Invoice, NotificationFacture
from billing.services.notification_service import notifier_facture


def main():
    print("\n" + "="*70)
    print("📱 TEST SMS FINAL - Envoi au +228 92 62 82 87")
    print("="*70)
    
    # Vérifier la configuration
    from django.conf import settings
    
    print("\n⚙️  Configuration Vonage :")
    print(f"   - API Key : {settings.VONAGE_API_KEY}")
    print(f"   - Expéditeur : {settings.VONAGE_SMS_FROM}")
    print(f"   - Destinataire : 22892628287 (format sans +)")
    
    # Créer ou récupérer l'utilisateur
    print("\n👤 Utilisateur de test :")
    user, created = User.objects.update_or_create(
        username='yendoi_sms_test',
        defaults={
            'email': 'yendoiboure@gmail.com',
            'role': 'PAYEUR',
            'first_name': 'Yendoi',
            'last_name': 'Bouré',
            'telephone': '22892628287',  # Format SANS le + (validé par diagnostic)
            'is_active': True
        }
    )
    
    action = "créé" if created else "mis à jour"
    print(f"   ✅ Utilisateur {action}")
    print(f"   - Username : {user.username}")
    print(f"   - Email : {user.email}")
    print(f"   - Téléphone : {user.telephone}")
    
    # Créer l'entreprise
    print("\n🏢 Entreprise de test :")
    company, created = Company.objects.get_or_create(
        compte='TEST-SMS-YENDOI',
        defaults={
            'raison_sociale': 'Test SMS Final',
            'categorie': 'PE',
            'payeur': user,
            'email_facturation': 'yendoiboure@gmail.com'
        }
    )
    
    action = "créée" if created else "existante"
    print(f"   ✅ Entreprise {action} : {company.compte}")
    
    # Supprimer les anciennes factures de test
    Invoice.objects.filter(numero_facture__startswith='FAC-SMS-TEST').delete()
    
    # Créer une nouvelle facture
    print("\n📄 Facture de test :")
    invoice = Invoice.objects.create(
        company=company,
        numero_facture=f'FAC-SMS-TEST-{date.today().strftime("%Y%m%d-%H%M%S")}',
        periode_debut=date.today() - timedelta(days=30),
        periode_fin=date.today(),
        montant_ht=Decimal('50000'),
        montant_tva=Decimal('9000'),
        montant_ttc=Decimal('59000'),
        date_echeance=date.today() + timedelta(days=30),
        statut='PUBLIEE'
    )
    
    print(f"   ✅ Facture créée : {invoice.numero_facture}")
    print(f"   - Montant : {invoice.montant_ttc} FCFA")
    print(f"   - Période : du {invoice.periode_debut} au {invoice.periode_fin}")
    
    # Confirmation avant envoi
    print("\n" + "="*70)
    print("⚠️  ATTENTION : Envoi d'un SMS RÉEL")
    print("="*70)
    print(f"   Destinataire : +228 92 62 82 87")
    print(f"   Coût estimé : ~0.47 EUR")
    print(f"   Solde restant Vonage : ~1.53 EUR (après cet envoi)")
    
    confirm = input("\n✋ Confirmer l'envoi du SMS ? (oui/non) : ").strip().lower()
    
    if confirm != 'oui':
        print("\n❌ Envoi annulé par l'utilisateur")
        return
    
    # Envoi du SMS
    print("\n" + "="*70)
    print("📤 ENVOI EN COURS...")
    print("="*70)
    
    try:
        resultats = notifier_facture(invoice, ['SMS'])
        
        if not resultats:
            print("❌ Aucun résultat retourné par le service")
            return
        
        notif = resultats[0]
        
        print(f"\n{'✅' if notif.statut == 'ENVOYEE' else '❌'} Résultat de l'envoi")
        print("-" * 70)
        print(f"   Canal : {notif.canal}")
        print(f"   Destinataire : {notif.destinataire}")
        print(f"   Statut : {notif.statut}")
        print(f"   Date : {notif.date_envoi}")
        
        if notif.detail:
            print(f"   Détail : {notif.detail}")
        
        if notif.statut == 'ENVOYEE':
            print("\n" + "="*70)
            print("🎉 SMS ENVOYÉ AVEC SUCCÈS !")
            print("="*70)
            print("\n📱 Instructions de vérification :")
            print("   1. Vérifier le téléphone : +228 92 62 82 87")
            print("   2. Délai de réception : 5 secondes à 5 minutes")
            print("   3. Message attendu :")
            print(f"      'Votre facture {invoice.numero_facture} est disponible")
            print("       dans votre portail Moov Africa.'")
            print("\n⏱️  Si le SMS n'arrive pas dans les 5 minutes :")
            print("   1. Vérifier que le téléphone est allumé et a du réseau")
            print("   2. Consulter les logs Vonage :")
            print("      https://dashboard.nexmo.com/sms")
            print("   3. Rechercher l'ID du message :")
            print("      (visible dans les logs Vonage)")
            print("   4. Vérifier le statut de livraison détaillé")
            
            # Afficher l'historique des notifications
            print("\n📊 HISTORIQUE DES NOTIFICATIONS SMS")
            print("-" * 70)
            
            notifications = NotificationFacture.objects.filter(
                canal='SMS'
            ).order_by('-date_envoi')[:5]
            
            if notifications:
                for notif in notifications:
                    status_icon = "✅" if notif.statut == 'ENVOYEE' else "❌"
                    print(f"{status_icon} {notif.date_envoi.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Destinataire : {notif.destinataire}")
                    print(f"   Statut : {notif.statut}")
                    if notif.detail:
                        print(f"   Détail : {notif.detail}")
                    print()
            else:
                print("   (Aucune notification SMS dans l'historique)")
                
        else:
            print("\n" + "="*70)
            print("❌ ÉCHEC DE L'ENVOI SMS")
            print("="*70)
            print(f"\nRaison : {notif.detail or 'Erreur inconnue'}")
            print("\n🔍 Actions de dépannage :")
            print("   1. Vérifier les credentials Vonage dans .env")
            print("   2. Vérifier le solde sur https://dashboard.nexmo.com")
            print("   3. Exécuter : python Back/diagnostic_sms.py")
            
    except Exception as e:
        print("\n" + "="*70)
        print("❌ ERREUR CRITIQUE")
        print("="*70)
        print(f"\n{str(e)}")
        
        import traceback
        print("\n📋 Détails techniques :")
        traceback.print_exc()
        
        print("\n🔍 Actions de dépannage :")
        print("   1. Vérifier que Django est bien configuré")
        print("   2. Vérifier les settings dans moov_backend/settings.py")
        print("   3. Vérifier le fichier .env")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
