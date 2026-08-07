# 📧📱 Instructions de Test d'Envoi Email & SMS

**Destinataires configurés** :
- 📧 **Email** : yendoiboure@gmail.com
- 📱 **SMS** : +228 92 62 82 87

---

## 🚀 Méthode 1 : Test rapide (Recommandé)

### Script automatique Email + SMS

```bash
cd Back
python test_envoi_rapide.py
```

**Ce script va** :
1. Créer un utilisateur de test avec les coordonnées spécifiées
2. Créer une facture de test
3. Envoyer automatiquement Email + SMS
4. Afficher le résultat

**Sortie attendue** :
```
✅ 2 notification(s) traitée(s) :

✅ EMAIL
   Destinataire : yendoiboure@gmail.com
   Statut : ENVOYEE

✅ SMS
   Destinataire : 22892628287
   Statut : ENVOYEE

🎉 SUCCÈS !

Vérifiez:
   📧 Boîte email : yendoiboure@gmail.com (+ spam)
   📱 Téléphone : +228 92 62 82 87
```

---

## 🎯 Méthode 2 : Test avec menu interactif

### Script avec choix

```bash
cd Back
python test_envoi_reel.py
```

**Menu proposé** :
```
1. Envoyer EMAIL uniquement à yendoiboure@gmail.com
2. Envoyer SMS uniquement au +228 92 62 82 87
3. Envoyer EMAIL + SMS (les deux)
0. Quitter
```

**Avantage** : Permet de tester chaque canal séparément

---

## 📝 Méthode 3 : Via Django Shell (Manuel)

### Test Email uniquement

```bash
cd Back
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Moov Africa - Facture disponible',
    'Votre facture est maintenant disponible dans votre portail Moov Africa.',
    'benoitbal55@gmail.com',
    ['yendoiboure@gmail.com'],
    fail_silently=False
)

print("✅ Email envoyé à yendoiboure@gmail.com")
```

### Test SMS uniquement

```python
import urllib.parse
import urllib.request
from django.conf import settings

data = urllib.parse.urlencode({
    'api_key': settings.VONAGE_API_KEY,
    'api_secret': settings.VONAGE_API_SECRET,
    'to': '22892628287',
    'from': settings.VONAGE_SMS_FROM,
    'text': 'Test Moov Africa: Votre facture est disponible.',
}).encode()

request = urllib.request.Request(
    'https://rest.nexmo.com/sms/json',
    data=data,
    method='POST'
)

with urllib.request.urlopen(request, timeout=15) as response:
    body = response.read().decode('utf-8')
    print(body)
    
    if '"status":"0"' in body:
        print("✅ SMS envoyé au +228 92 62 82 87")
    else:
        print("❌ Échec envoi SMS")
```

### Test complet avec facture

```python
from decimal import Decimal
from datetime import date, timedelta
from accounts.models import User
from billing.models import Company, Invoice
from billing.services.notification_service import notifier_facture

# Créer utilisateur
user, _ = User.objects.update_or_create(
    username='yendoi_test',
    defaults={
        'email': 'yendoiboure@gmail.com',
        'role': 'PAYEUR',
        'telephone': '22892628287',
    }
)

# Créer entreprise
company, _ = Company.objects.get_or_create(
    compte='TEST-YENDOI',
    defaults={
        'raison_sociale': 'Test',
        'categorie': 'PE',
        'payeur': user
    }
)

# Créer facture
invoice = Invoice.objects.create(
    company=company,
    numero_facture='FAC-TEST-001',
    periode_debut=date.today() - timedelta(days=30),
    periode_fin=date.today(),
    montant_ttc=Decimal('50000'),
    date_echeance=date.today() + timedelta(days=30),
    statut='PUBLIEE'
)

# Envoyer notifications
resultats = notifier_facture(invoice, ['EMAIL', 'SMS'])

for r in resultats:
    print(f"{r.canal}: {r.statut} → {r.destinataire}")
```

---

## ✅ Vérification après envoi

### Pour l'Email

1. **Ouvrir la boîte** : https://mail.google.com
2. **Se connecter avec** : yendoiboure@gmail.com
3. **Chercher** :
   - Boîte de réception : "Moov Africa"
   - **Si absent** : Vérifier les **SPAMS** ⚠️
4. **Contenu attendu** :
   - Sujet : "Votre facture Moov Africa est disponible"
   - Corps : Numéro de facture + mention "portail Moov Africa"

### Pour le SMS

1. **Vérifier le téléphone** : +228 92 62 82 87
2. **Délai** : 5-30 secondes (parfois jusqu'à 2 minutes)
3. **Contenu attendu** :
   - "Votre facture [NUMERO] est disponible dans votre portail Moov Africa."
4. **Expéditeur** : Peut être "MOOV" ou un numéro court

---

## 🐛 Dépannage

### Email non reçu

#### 1. Vérifier les spams
- Ouvrir Gmail : yendoiboure@gmail.com
- Aller dans **Spam** (gauche)
- Chercher "Moov" ou "benoitbal55"

#### 2. Vérifier la configuration
```bash
cd Back
python manage.py shell
```

```python
from django.conf import settings
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"PASSWORD configuré: {'Oui' if settings.EMAIL_HOST_PASSWORD else 'Non'}")
```

Si problème, vérifier le fichier `.env` :
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=benoitbal55@gmail.com
SMTP_PASSWORD=vipglqzsgzifufgd
SMTP_USE_TLS=True
SMTP_FROM_EMAIL=benoitbal55@gmail.com
```

#### 3. Test de connexion SMTP
```python
from django.core.mail import send_mail
try:
    send_mail('Test', 'Test', 'benoitbal55@gmail.com', ['yendoiboure@gmail.com'])
    print("✅ Email envoyé")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

---

### SMS non reçu

#### 1. Vérifier le crédit Vonage
- Aller sur : https://dashboard.nexmo.com
- Se connecter avec les identifiants Vonage
- Vérifier le **solde** (minimum 0.05€ par SMS)

#### 2. Vérifier le format du numéro
```python
from django.conf import settings
print(f"Numéro expéditeur: {settings.VONAGE_SMS_FROM}")
print(f"Format attendu: 22892628287 (sans + ni espaces)")
```

Le numéro doit être en format international **sans le +** :
- ✅ Correct : `22892628287`
- ❌ Incorrect : `+22892628287` ou `+228 92 62 82 87`

#### 3. Test API Vonage
```python
import urllib.parse
import urllib.request
from django.conf import settings

data = urllib.parse.urlencode({
    'api_key': settings.VONAGE_API_KEY,
    'api_secret': settings.VONAGE_API_SECRET,
    'to': '22892628287',
    'from': settings.VONAGE_SMS_FROM,
    'text': 'Test',
}).encode()

request = urllib.request.Request('https://rest.nexmo.com/sms/json', data=data)
with urllib.request.urlopen(request) as response:
    body = response.read().decode('utf-8')
    print(body)
```

**Réponse attendue** :
```json
{
  "messages": [
    {
      "status": "0",  ← "0" = succès
      "message-id": "...",
      "to": "22892628287"
    }
  ]
}
```

Si `status != "0"`, voir les codes d'erreur :
- `1` : Throttled (trop de requêtes)
- `2` : Missing params
- `3` : Invalid params
- `4` : Invalid credentials
- `5` : Internal error
- `9` : Partner quota exceeded (plus de crédit)

---

## 📊 Vérifier l'historique en base

```bash
cd Back
python manage.py shell
```

```python
from billing.models import NotificationFacture

# Dernières notifications
notifs = NotificationFacture.objects.all().order_by('-date_envoi')[:10]

for n in notifs:
    print(f"{n.date_envoi} | {n.canal} | {n.statut} | {n.destinataire}")

# Statistiques
print(f"\nTotal: {NotificationFacture.objects.count()}")
print(f"Email envoyés: {NotificationFacture.objects.filter(canal='EMAIL', statut='ENVOYEE').count()}")
print(f"SMS envoyés: {NotificationFacture.objects.filter(canal='SMS', statut='ENVOYEE').count()}")
```

---

## 💰 Coûts Vonage

| Type | Coût unitaire | Notes |
|------|---------------|-------|
| SMS vers Togo | ~0.04-0.06€ | Variable selon opérateur |
| SMS vers France | ~0.08€ | Plus cher |
| Recharge minimum | 5€ | Recommandé : 10€ |

**Pour 10€** : ~200 SMS vers le Togo

---

## ✅ Checklist de validation

### Email
- [ ] Script `test_envoi_rapide.py` exécuté
- [ ] Email reçu sur yendoiboure@gmail.com
- [ ] Sujet correct
- [ ] Contenu correct
- [ ] Notification enregistrée en base

### SMS
- [ ] Script `test_envoi_rapide.py` exécuté
- [ ] SMS reçu sur +228 92 62 82 87
- [ ] Contenu correct
- [ ] Notification enregistrée en base
- [ ] Crédit Vonage suffisant

---

## 🎯 Commande rapide tout-en-un

Pour tester Email + SMS en une seule commande :

```bash
cd Back
python test_envoi_rapide.py
```

Puis vérifier :
- 📧 yendoiboure@gmail.com (+ spam)
- 📱 +228 92 62 82 87

---

**Créé le** : 6 août 2026  
**Destinataires de test** :
- Email : yendoiboure@gmail.com
- SMS : +228 92 62 82 87
