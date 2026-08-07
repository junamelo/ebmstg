# Guide de Test des Notifications Email et SMS

## 🎯 Objectif

Tester l'envoi réel d'emails et de SMS depuis votre système de facturation.

---

## ⚙️ Prérequis

### Configuration Email (Gmail)
✅ **Déjà configuré dans `.env`** :
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=benoitbal55@gmail.com
SMTP_PASSWORD=vipglqzsgzifufgd
SMTP_USE_TLS=True
SMTP_FROM_EMAIL=benoitbal55@gmail.com
```

### Configuration SMS (Vonage)
✅ **Déjà configuré dans `.env`** :
```env
VONAGE_API_KEY=1956a1fd
VONAGE_API_SECRET=8oOEZccQuRpV14GN
VONAGE_SMS_FROM=22879983759
```

---

## 🚀 Méthode 1 : Script de test automatique (Recommandé)

### Étape 1 : Exécuter le script
```bash
cd Back
python test_notifications_manuelles.py
```

### Étape 2 : Menu interactif
Le script affiche un menu :
```
MENU DE TEST DES NOTIFICATIONS
1. Tester Email uniquement
2. Tester SMS uniquement
3. Tester Email + SMS (multi-canal)
4. Afficher l'historique des notifications
5. Créer de nouvelles données de test
0. Quitter
```

### Étape 3 : Choisir une option
- **Option 1** : Envoie un email à `benoitbal55@gmail.com`
- **Option 2** : Envoie un SMS au `22879983759` (⚠️ coût ~0.05€)
- **Option 3** : Envoie Email + SMS simultanément
- **Option 4** : Affiche l'historique des notifications en base

### Exemple de sortie
```
✅ Email envoyé avec succès !
   - Canal : EMAIL
   - Destinataire : benoitbal55@gmail.com
   - Statut : ENVOYEE
   - Date : 2026-08-06 10:30:15

🎉 SUCCESS ! Vérifiez votre boîte email : benoitbal55@gmail.com
```

---

## 🧪 Méthode 2 : Tests unitaires

### Exécuter les tests automatisés
```bash
cd Back
python manage.py test billing.test_notifications -v 2
```

### Résultat attendu
```
Ran 12 tests in 14.826s
OK
```

**Note** : Ces tests utilisent des mocks et n'envoient pas de vrais emails/SMS.

---

## 📧 Méthode 3 : Test Email via Django Shell

### Étape 1 : Ouvrir le shell Django
```bash
cd Back
python manage.py shell
```

### Étape 2 : Code de test
```python
from django.core.mail import send_mail

# Test simple
send_mail(
    'Test Moov Africa',
    'Ceci est un test d\'envoi d\'email depuis le système de facturation.',
    'benoitbal55@gmail.com',
    ['benoitbal55@gmail.com'],
    fail_silently=False
)

print("✅ Email envoyé ! Vérifiez votre boîte.")
```

### Étape 3 : Vérifier
- Ouvrir `benoitbal55@gmail.com`
- Chercher l'email avec le sujet "Test Moov Africa"
- ⚠️ Vérifier les spams si non reçu

---

## 📱 Méthode 4 : Test SMS via Django Shell

### Étape 1 : Ouvrir le shell Django
```bash
cd Back
python manage.py shell
```

### Étape 2 : Code de test
```python
import urllib.parse
import urllib.request
from django.conf import settings

# Paramètres SMS
data = urllib.parse.urlencode({
    'api_key': settings.VONAGE_API_KEY,
    'api_secret': settings.VONAGE_API_SECRET,
    'to': '22879983759',  # VOTRE NUMÉRO
    'from': settings.VONAGE_SMS_FROM,
    'text': 'Test SMS depuis Moov Africa. Si vous recevez ce message, le système fonctionne !',
}).encode()

# Envoi
request = urllib.request.Request(
    'https://rest.nexmo.com/sms/json',
    data=data,
    method='POST'
)

with urllib.request.urlopen(request, timeout=15) as response:
    body = response.read().decode('utf-8')
    print(body)
    
    if '"status":"0"' in body or '"status": "0"' in body:
        print("\n✅ SMS envoyé avec succès !")
    else:
        print("\n❌ Échec de l'envoi SMS")
        print(body)
```

### Étape 3 : Vérifier
- Vérifier la réception du SMS sur le `22879983759`
- Délai de réception : 5-30 secondes généralement

---

## 🔄 Méthode 5 : Test avec une vraie facture

### Étape 1 : Créer une facture de test
```bash
cd Back
python manage.py shell
```

```python
from decimal import Decimal
from datetime import date, timedelta
from accounts.models import User
from billing.models import Company, Invoice
from billing.services.notification_service import notifier_facture

# Récupérer ou créer un payeur
payeur = User.objects.filter(role='PAYEUR').first()
if not payeur:
    payeur = User.objects.create_user(
        username='test_payeur',
        email='benoitbal55@gmail.com',
        password='testpass',
        role='PAYEUR',
        telephone='22879983759'
    )

# Récupérer ou créer une entreprise
company = Company.objects.filter(payeur=payeur).first()
if not company:
    company = Company.objects.create(
        compte='TEST001',
        raison_sociale='Test SARL',
        categorie='PE',
        payeur=payeur
    )

# Créer une facture
invoice = Invoice.objects.create(
    company=company,
    numero_facture='FAC-TEST-001',
    periode_debut=date.today() - timedelta(days=30),
    periode_fin=date.today(),
    montant_ttc=Decimal('50000'),
    date_echeance=date.today() + timedelta(days=30),
    statut='PUBLIEE'
)

print(f"✅ Facture créée : {invoice.numero_facture}")
```

### Étape 2 : Envoyer les notifications
```python
# Email uniquement
resultats = notifier_facture(invoice, ['EMAIL'])
print(f"Email : {resultats[0].statut}")

# SMS uniquement
resultats = notifier_facture(invoice, ['SMS'])
print(f"SMS : {resultats[0].statut}")

# Email + SMS
resultats = notifier_facture(invoice, ['EMAIL', 'SMS'])
for r in resultats:
    print(f"{r.canal} : {r.statut}")
```

---

## 🐛 Dépannage

### Problème : Email non reçu

#### Vérification 1 : Boîte spam
- Ouvrir Gmail
- Aller dans "Spam"
- Chercher des emails de `benoitbal55@gmail.com`

#### Vérification 2 : Mot de passe d'application
```bash
cd Back
python manage.py shell
```
```python
from django.conf import settings
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"Mot de passe configuré : {'Oui' if settings.EMAIL_HOST_PASSWORD else 'Non'}")
```

Si le mot de passe n'est pas configuré :
1. Aller sur https://myaccount.google.com/apppasswords
2. Créer un nouveau mot de passe d'application
3. Copier dans `.env` : `SMTP_PASSWORD=votre_nouveau_mot_de_passe`

#### Vérification 3 : Logs Django
```bash
cd Back
python manage.py shell
```
```python
from django.core.mail import send_mail
try:
    send_mail('Test', 'Message', 'benoitbal55@gmail.com', ['benoitbal55@gmail.com'])
    print("✅ Envoi réussi")
except Exception as e:
    print(f"❌ Erreur : {e}")
```

---

### Problème : SMS non reçu

#### Vérification 1 : Crédit Vonage
- Se connecter sur https://dashboard.nexmo.com
- Vérifier le solde (minimum 0.05€ par SMS)
- Recharger si nécessaire

#### Vérification 2 : Format du numéro
```python
from django.conf import settings
print(f"Numéro expéditeur : {settings.VONAGE_SMS_FROM}")
print(f"Format attendu : 22879983759 (sans +, sans espaces)")
```

#### Vérification 3 : Test API Vonage
```python
import urllib.parse
import urllib.request
from django.conf import settings

data = urllib.parse.urlencode({
    'api_key': settings.VONAGE_API_KEY,
    'api_secret': settings.VONAGE_API_SECRET,
    'to': '22879983759',
    'from': settings.VONAGE_SMS_FROM,
    'text': 'Test',
}).encode()

request = urllib.request.Request('https://rest.nexmo.com/sms/json', data=data)
with urllib.request.urlopen(request) as response:
    print(response.read().decode('utf-8'))
```

Réponse attendue :
```json
{
  "messages": [
    {
      "status": "0",  ← "0" = succès
      "message-id": "...",
      "to": "22879983759"
    }
  ]
}
```

Si `status != "0"`, voir https://developer.vonage.com/en/messaging/sms/guides/delivery-receipts

---

## 📊 Vérifier l'historique en base

### Via Django Shell
```python
from billing.models import NotificationFacture

# Toutes les notifications
notifications = NotificationFacture.objects.all().order_by('-date_envoi')
for n in notifications[:10]:
    print(f"{n.date_envoi} | {n.canal} | {n.statut} | {n.destinataire}")

# Statistiques
print(f"\nTotal : {notifications.count()}")
print(f"Envoyées : {notifications.filter(statut='ENVOYEE').count()}")
print(f"Échecs : {notifications.filter(statut='ECHEC').count()}")
```

### Via Admin Django
1. Lancer le serveur : `python manage.py runserver`
2. Aller sur http://localhost:8000/admin
3. Se connecter avec un compte SUPER_ADMIN
4. Aller dans "Billing" → "Notification factures"

---

## ✅ Checklist de validation

### Email
- [ ] Configuration Gmail vérifiée
- [ ] Test unitaire `test_notifications` OK
- [ ] Email test reçu via script
- [ ] Email test reçu via Django Shell
- [ ] Email avec vraie facture reçu

### SMS
- [ ] Configuration Vonage vérifiée
- [ ] Crédit Vonage suffisant (>0.05€)
- [ ] Test unitaire `test_notifications` OK
- [ ] SMS test reçu via script
- [ ] SMS test reçu via Django Shell
- [ ] SMS avec vraie facture reçu

### Historique
- [ ] Notifications enregistrées en base
- [ ] Statuts corrects (ENVOYEE/ECHEC)
- [ ] Dates d'envoi cohérentes
- [ ] Destinataires corrects

---

## 🎯 Prochaines étapes

### Intégration dans le workflow
Ajouter l'envoi de notifications après publication de factures :

**Fichier** : `Back/billing/views.py`

```python
from billing.services.notification_service import notifier_facture

# Dans PublicationViewSet ou après upload PDF
@action(detail=True, methods=['post'])
def publier_avec_notification(self, request, pk=None):
    invoice = self.get_object()
    
    # ... logique de publication ...
    
    # Envoyer les notifications
    canaux = request.data.get('canaux', ['EMAIL'])
    resultats = notifier_facture(invoice, canaux)
    
    return Response({
        'message': 'Facture publiée et notifications envoyées',
        'notifications': [
            {
                'canal': r.canal,
                'destinataire': r.destinataire,
                'statut': r.statut
            }
            for r in resultats
        ]
    })
```

---

## 📞 Support

### Gmail
- Documentation : https://support.google.com/mail/answer/7126229
- Mots de passe d'application : https://myaccount.google.com/apppasswords

### Vonage
- Dashboard : https://dashboard.nexmo.com
- Documentation : https://developer.vonage.com/en/messaging/sms/overview
- Support : https://dashboard.nexmo.com/support

---

**Guide créé le** : 6 août 2026  
**Version** : 1.0
