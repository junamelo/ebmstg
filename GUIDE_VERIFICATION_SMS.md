# 📱 GUIDE DE VÉRIFICATION SMS - Étape par étape

**Objectif** : Vérifier si le SMS est bien livré au destinataire +228 92 62 82 87

---

## ✅ ÉTAPE 1 : Vérifier que le SMS a été envoyé

Le diagnostic montre que le SMS a été **envoyé avec succès** :
```
✅ Status code: 0 (Message envoyé avec succès)
✅ Message ID: 81a17456-687e-4ca5-8138-c1c230a5a08c
✅ Prix: 0.47 EUR
✅ Solde restant: 1.53 EUR
```

**→ Cette étape est VALIDÉE** ✅

---

## 📱 ÉTAPE 2 : Vérifier le téléphone destinataire

### Checklist téléphone

Demandez au destinataire (+228 92 62 82 87) de vérifier :

- [ ] **Le téléphone est allumé**
- [ ] **Le téléphone a du réseau** (au moins 1 barre)
- [ ] **Le numéro est actif** (peut recevoir des appels)
- [ ] **La boîte SMS n'est pas pleine** (supprimer des vieux SMS si nécessaire)
- [ ] **Aucun filtre anti-spam actif** (vérifier les paramètres SMS)
- [ ] **Pas de mode "Ne pas déranger"** (peut bloquer les notifications)

### Message attendu

Le SMS devrait contenir :
```
Votre facture FAC-TEST-YENDOI-20260806 est disponible dans votre portail Moov Africa.
```

---

## ⏱️ ÉTAPE 3 : Attendre le délai de livraison

Les SMS internationaux peuvent prendre du temps :

| Scénario | Délai |
|----------|-------|
| **Normal** | 5 secondes à 2 minutes |
| **Retard modéré** | 2 à 10 minutes |
| **Retard important** | 10 à 30 minutes |
| **Échec** | Après 30 minutes, considérer comme échec |

**→ Attendre au moins 30 minutes avant de conclure à un échec**

---

## 🔍 ÉTAPE 4 : Consulter les logs Vonage

### 4.1 Se connecter au dashboard Vonage

1. Aller sur : https://dashboard.nexmo.com
2. Se connecter avec les identifiants Vonage
3. Aller dans : **Reports** > **SMS logs**

### 4.2 Rechercher le message

Dans les logs SMS, rechercher :
- **Message ID** : `81a17456-687e-4ca5-8138-c1c230a5a08c`
- **Destinataire** : `22892628287`
- **Date** : 6 août 2026

### 4.3 Vérifier le statut de livraison

Le dashboard Vonage affichera l'un de ces statuts :

| Statut | Signification | Action |
|--------|---------------|--------|
| **delivered** | ✅ SMS livré | Le SMS est arrivé, vérifier le téléphone |
| **buffered** | ⏱️ En attente | Attendre encore un peu |
| **failed** | ❌ Échec | Voir la raison de l'échec |
| **expired** | ⏰ Expiré | Le délai max est dépassé (72h) |
| **rejected** | 🚫 Rejeté | L'opérateur a refusé le SMS |
| **unknown** | ❓ Inconnu | Pas d'info de livraison disponible |

### 4.4 Si le statut est "failed" ou "rejected"

Vérifier le **code d'erreur détaillé** dans les logs :

| Code erreur | Signification | Solution |
|-------------|---------------|----------|
| **1** | Numéro invalide | Vérifier le format du numéro |
| **2** | Numéro barré par l'opérateur | Contacter l'opérateur télécom |
| **3** | Numéro inexistant | Vérifier que le numéro est actif |
| **4** | Porteur ne supporte pas les SMS | Vérifier le téléphone |
| **5** | Boîte SMS pleine | Vider la boîte du destinataire |
| **6** | Problème opérateur | Réessayer plus tard |
| **7** | SMS bloqué par filtre spam | Utiliser un expéditeur enregistré |

---

## 🧪 ÉTAPE 5 : Test alternatif (si le SMS n'arrive pas)

### Option A : Tester avec votre propre numéro

1. Modifier le numéro dans `Back/test_sms_final.py` :
   ```python
   'telephone': 'VOTRE_NUMERO',  # Format: 22879xxxxxx (sans le +)
   ```

2. Exécuter le test :
   ```bash
   python Back\test_sms_final.py
   ```

3. Si vous recevez le SMS → Le système fonctionne, le problème est avec le numéro +228 92 62 82 87

### Option B : Utiliser un expéditeur alphanumérique

Certains opérateurs préfèrent les expéditeurs alphanumériques.

1. Modifier dans `.env` :
   ```env
   VONAGE_SMS_FROM=MoovAfrica
   ```
   (au lieu de `VONAGE_SMS_FROM=22879983759`)

2. Relancer le test :
   ```bash
   python Back\test_sms_final.py
   ```

⚠️ **Note** : Les expéditeurs alphanumériques peuvent coûter plus cher

### Option C : Tester avec un autre opérateur

Si le destinataire a un autre numéro (d'un autre opérateur), essayer avec celui-ci.

Par exemple :
- Moov Togo vs Togocel
- Réseau 4G vs réseau 2G

---

## 📊 ÉTAPE 6 : Vérifier le compte Vonage

### 6.1 Vérifier le solde

1. Dashboard > **Billing** > **Balance**
2. Solde actuel : **1.53 EUR** (après l'envoi du diagnostic)
3. Minimum requis : **0.05 EUR** par SMS

✅ Le solde est suffisant

### 6.2 Vérifier le mode du compte

1. Dashboard > **Settings** > **API Settings**
2. Vérifier : **Account mode**
   - ✅ **Production** : Tous les numéros sont autorisés
   - ⚠️ **Sandbox/Test** : Seuls les numéros whitelistés sont autorisés

Si le compte est en mode **Sandbox** :
- Aller dans : Settings > Test numbers
- Ajouter le numéro `22892628287` à la whitelist

### 6.3 Vérifier les restrictions géographiques

1. Dashboard > **Settings** > **Restrictions**
2. Vérifier que **Togo (TG)** n'est pas bloqué
3. Si bloqué, activer l'envoi vers le Togo

---

## 🛠️ ÉTAPE 7 : Dépannage avancé

### Si le SMS n'arrive toujours pas après toutes ces vérifications :

#### 1. Vérifier la configuration dans le code

Vérifier `Back/billing/services/notification_service.py` ligne 38-57 :
```python
# Le numéro doit être sans le +
telephone = (getattr(user, 'telephone', '') or '').strip()
# Format attendu: 22892628287
```

#### 2. Vérifier la base de données

Exécuter ce script Python pour voir l'historique :
```python
from billing.models import NotificationFacture

# Voir les 5 dernières notifications SMS
notifs = NotificationFacture.objects.filter(
    canal='SMS'
).order_by('-date_envoi')[:5]

for n in notifs:
    print(f"{n.date_envoi} - {n.destinataire} - {n.statut}")
    if n.detail:
        print(f"  Détail: {n.detail}")
```

#### 3. Activer les logs détaillés Vonage

Dans le code de `notification_service.py`, ajouter après l'envoi :
```python
import json
print("Réponse Vonage:", body)  # Afficher la réponse brute
```

#### 4. Contacter le support Vonage

Si aucune des solutions ne fonctionne :

1. Aller sur : https://api.support.vonage.com
2. Créer un ticket avec ces informations :
   - **Message ID** : `81a17456-687e-4ca5-8138-c1c230a5a08c`
   - **Destinataire** : `22892628287`
   - **Date** : 6 août 2026
   - **Question** : "Pourquoi mon SMS n'est pas livré au Togo ?"

Le support Vonage pourra voir :
- Les détails de routage
- Le statut de livraison réel
- Les raisons d'échec détaillées
- Les restrictions sur le compte

---

## 📋 CHECKLIST COMPLÈTE

Avant de conclure à un échec, vérifiez :

### Configuration
- [x] VONAGE_API_KEY configuré dans .env
- [x] VONAGE_API_SECRET configuré dans .env
- [x] VONAGE_SMS_FROM configuré dans .env
- [x] Solde Vonage suffisant (1.53 EUR)

### Envoi
- [x] SMS envoyé avec succès (status code 0)
- [x] Message ID reçu (81a17456...)
- [x] Format du numéro correct (22892628287 sans le +)

### Réception
- [ ] Téléphone allumé et avec du réseau
- [ ] Numéro actif (peut recevoir des appels)
- [ ] Boîte SMS pas pleine
- [ ] Pas de filtre anti-spam
- [ ] Attente de 30 minutes respectée

### Logs Vonage
- [ ] Logs consultés sur dashboard.nexmo.com
- [ ] Message ID recherché dans les logs
- [ ] Statut de livraison vérifié
- [ ] Code d'erreur analysé (si échec)

### Tests alternatifs
- [ ] Test avec votre propre numéro
- [ ] Test avec expéditeur alphanumérique
- [ ] Test avec un autre opérateur

---

## 🎯 RÉSULTAT ATTENDU

### ✅ Scénario 1 : SMS livré avec succès

Le destinataire reçoit :
```
Votre facture FAC-TEST-YENDOI-20260806 est disponible dans votre portail Moov Africa.
```

**→ Le système fonctionne parfaitement !** 🎉

### ⚠️ Scénario 2 : SMS non livré malgré l'envoi Vonage

Le SMS est envoyé par Vonage (status 0) mais :
- Pas reçu par le destinataire
- Statut "failed" ou "rejected" dans les logs Vonage

**→ Problème au niveau de l'opérateur télécom ou du téléphone**

Solutions :
1. Contacter l'opérateur télécom au Togo
2. Tester avec un autre numéro
3. Utiliser un expéditeur enregistré
4. Contacter le support Vonage

---

## 📞 CONTACTS UTILES

### Support Technique
- **Vonage Support** : https://api.support.vonage.com
- **Documentation SMS** : https://developer.vonage.com/messaging/sms/overview

### Dashboard Vonage
- **Accueil** : https://dashboard.nexmo.com
- **SMS Logs** : https://dashboard.nexmo.com/sms
- **Balance** : https://dashboard.nexmo.com/billing
- **Settings** : https://dashboard.nexmo.com/settings

---

## 💬 QUESTIONS FRÉQUENTES

### Q1 : Le SMS a status "0" mais n'est pas reçu, pourquoi ?

**R** : Le status "0" signifie que Vonage a **accepté** le SMS et l'a **transmis** à l'opérateur télécom. Mais l'opérateur peut :
- Le mettre en attente (buffered)
- Le bloquer (rejected)
- Le perdre (network issue)

→ Consulter les logs Vonage pour voir le statut de livraison final.

### Q2 : Combien de temps attendre avant de conclure à un échec ?

**R** : Attendre **30 minutes**. Les SMS internationaux peuvent être lents, surtout vers certains pays africains.

### Q3 : Le SMS coûte combien ?

**R** : Pour le Togo, le prix est d'environ **0.47 EUR** par SMS (visible dans la réponse Vonage).

### Q4 : Peut-on envoyer des SMS gratuits ?

**R** : Non, tous les SMS via Vonage sont payants. Le prix varie selon le pays de destination.

### Q5 : Que faire si le solde est insuffisant ?

**R** :
1. Aller sur : https://dashboard.nexmo.com
2. Menu : Billing > Add credit
3. Minimum recommandé : 5 EUR (≈ 10 SMS vers le Togo)

### Q6 : Le numéro expéditeur peut-il être personnalisé ?

**R** : Oui, mais cela dépend du pays :
- **Numérique** : `22879983759` (actuel, fonctionne partout)
- **Alphanumérique** : `MoovAfrica` (peut ne pas fonctionner partout)
- **Numéro court** : Nécessite un enregistrement spécial

---

## ✅ CONCLUSION

Le système SMS est **fonctionnel** :
- ✅ Configuration correcte
- ✅ Solde suffisant
- ✅ SMS envoyé par Vonage (status 0)

Si le SMS n'est pas reçu, suivre ce guide étape par étape pour identifier où se situe le problème (téléphone, opérateur, ou restrictions Vonage).

**Prochaine action** : Consulter les logs Vonage pour voir le statut de livraison réel du message ID `81a17456-687e-4ca5-8138-c1c230a5a08c`.
