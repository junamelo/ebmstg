"""
Test rapide d'envoi Email + SMS
Envoie directement sans menu interactif
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moov_backend.settings')
django.setup()

print("\n" + "="*70)
print("🧪 TEST RAPIDE D'ENVOI EMAIL + SMS")
print("="*70)
print("\nDestinataires:")
print("   📧 Email : yendoiboure@gmail.com")
print("   📱 SMS : +228 92 62 82 87")
print("\n⚠️  Le SMS coûtera environ 0.05€ via Vonage")

# Demander confirmation
confirm = input("\nVoulez-vous continuer ? (oui/non) : ").strip().lower()

if confirm != 'oui':
    print("❌ Test annulé")
    sys.exit(0)

print("\n" + "="*70)
print("PRÉPARATION...")
print("="*70)

from decimal import Decimal
from datetime import date, timedelta
from accounts.models import User
from billing.models import Company, Invoice
from billing.services.notification_service import notifier_facture

# Créer ou mettre à jour l'utilisateur
user, created = User.objects.update_or_create(
    username='yendoi_test',
    defaults={
        'email': 'yendoiboure@gmail.com',
        'role': 'PAYEUR',
        'first_name': 'Yendoi',
        'last_name': 'Bouré',
        'telephone': '22892628287',
        'is_active': True
    }
)

if created:
    user.set_password('testpass123')
    user.save()

print(f"✅ Utilisateur : {user.email} | {user.telephone}")

# Créer ou récupérer l'entreprise
company, _ = Company.objects.get_or_create(
    compte='TEST-YENDOI-001',
    defaults={
        'raison_sociale': 'Test Envoi Notifications',
        'categorie': 'PE',
        'payeur': user
    }
)

print(f"✅ Entreprise : {company.raison_sociale}")

# Créer une facture
Invoice.objects.filter(numero_facture__startswith='FAC-TEST-YENDOI').delete()

invoice = Invoice.objects.create(
    company=company,
    numero_facture=f'FAC-TEST-YENDOI-{date.today().strftime("%Y%m%d-%H%M%S")}',
    periode_debut=date.today() - timedelta(days=30),
    periode_fin=date.today(),
    montant_ttc=Decimal('59000'),
    date_echeance=date.today() + timedelta(days=30),
    statut='PUBLIEE'
)

print(f"✅ Facture : {invoice.numero_facture} ({invoice.montant_ttc} FCFA)")

# Envoyer les notifications
print("\n" + "="*70)
print("ENVOI DES NOTIFICATIONS...")
print("="*70)

try:
    resultats = notifier_facture(invoice, ['EMAIL', 'SMS'])
    
    print(f"\n✅ {len(resultats)} notification(s) traitée(s) :\n")
    
    success_count = 0
    for notif in resultats:
        icon = "✅" if notif.statut == 'ENVOYEE' else "❌"
        print(f"{icon} {notif.canal}")
        print(f"   Destinataire : {notif.destinataire}")
        print(f"   Statut : {notif.statut}")
        
        if notif.detail:
            print(f"   Détail : {notif.detail}")
        
        if notif.statut == 'ENVOYEE':
            success_count += 1
        print()
    
    print("="*70)
    print(f"RÉSULTAT : {success_count}/{len(resultats)} notification(s) envoyée(s)")
    print("="*70)
    
    if success_count > 0:
        print("\n🎉 SUCCÈS !")
        print("\nVérifiez:")
        print("   📧 Boîte email : yendoiboure@gmail.com (+ spam)")
        print("   📱 Téléphone : +228 92 62 82 87")
    else:
        print("\n❌ ÉCHEC de tous les envois")
        print("Vérifiez la configuration dans le fichier .env")

except Exception as e:
    print(f"\n❌ ERREUR : {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("FIN DU TEST")
print("="*70 + "\n")
