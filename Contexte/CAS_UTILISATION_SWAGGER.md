# 🎯 CAS D'UTILISATION COMPLET - Swagger avec Gestion des Erreurs

## 📖 SCÉNARIO

**Tu es un Agent de Facturation Moov Africa.**  
Tu dois créer un nouveau forfait "Formule Star 5G" avec un service optionnel "Data Boost" et tester une simulation de facturation.

---

## 🚀 ÉTAPE 0 : PRÉPARATION

### Démarrer le serveur Django

```bash
cd "c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"
python manage.py runserver
```

**✅ Résultat attendu :**
```
Starting development server at http://127.0.0.1:8000/
```

**❌ ERREUR POSSIBLE 1 :**
```
Error: That port is already in use.
```
**Solution :**
```bash
# Utiliser un autre port
python manage.py runserver 8001
```

**❌ ERREUR POSSIBLE 2 :**
```
ModuleNotFoundError: No module named 'rest_framework'
```
**Solution :**
```bash
pip install djangorestframework
```

---

### Ouvrir Swagger

**URL :** http://localhost:8000/api/docs/

**❌ ERREUR POSSIBLE 3 :**
```
Page ne charge pas / ERR_CONNECTION_REFUSED
```
**Solution :**
- Vérifier que le serveur Django est bien démarré
- Vérifier l'URL : `localhost:8000` pas `localhost:3000`

---

## 🔐 ÉTAPE 1 : CONNEXION

### 1.1 - Trouver l'endpoint de login

1. Dans Swagger, chercher la section **"auth"**
2. Cliquer sur **POST `/api/auth/login/`**
3. Cliquer sur **"Try it out"**

### 1.2 - Tenter de se connecter (PREMIER ESSAI - ÉCHEC)

**Body à envoyer :**
```json
{
  "email": "admin@moov.tg",
  "password": "mauvais_mot_de_passe"
}
```

**Cliquer sur "Execute"**

**❌ ERREUR ATTENDUE :**
```json
{
  "error": "Email ou mot de passe incorrect"
}
```
**Code HTTP :** `401 Unauthorized`

**💡 Analyse :** Le mot de passe est incorrect.

---

### 1.3 - Se connecter correctement (DEUXIÈME ESSAI - SUCCÈS)

**Body correct :**
```json
{
  "email": "admin@moov.tg",
  "password": "admin123"
}
```

**Cliquer sur "Execute"**

**✅ RÉPONSE ATTENDUE :**
```json
{
  "user": {
    "id": 1,
    "email": "admin@moov.tg",
    "username": "admin",
    "first_name": "",
    "last_name": "",
    "role": "SUPER_ADMIN",
    "telephone": null,
    "est_actif": true
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxNjY4ODAwLCJpYXQiOjE3MjE2NjE2MDAsImp0aSI6IjEyMzQ1Njc4OTBhYmNkZWYiLCJ1c2VyX2lkIjoxfQ.abc123def456..."
}
```
**Code HTTP :** `200 OK`

**💡 Action :** Copier le contenu du champ **"access"** (le long token)

---

### 1.4 - Autoriser Swagger avec le token

1. En haut à droite, cliquer sur le bouton **"Authorize"** 🔓
2. Une popup s'ouvre
3. **Coller le token** APRÈS le mot "Bearer " :
   ```
   Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```
4. Cliquer sur **"Authorize"**
5. Cliquer sur **"Close"**

**✅ Résultat :** Le cadenas 🔓 devient 🔒

**❌ ERREUR POSSIBLE 4 :**
Si tu oublies "Bearer " avant le token, les requêtes suivantes retourneront `401 Unauthorized`.

**Solution :** Toujours mettre `Bearer ` (avec un espace) avant le token.

---

## 📦 ÉTAPE 2 : CRÉER UN FORFAIT

### 2.1 - Trouver l'endpoint

1. Chercher la section **"billing"**
2. Trouver **POST `/api/billing/packages/`**
3. Cliquer dessus
4. Cliquer sur **"Try it out"**

---

### 2.2 - Première tentative (ÉCHEC - Données incomplètes)

**Body avec données manquantes :**
```json
{
  "nom": "Formule Star 5G",
  "type_forfait": "MIXTE",
  "prix_mensuel": 25000
}
```

**Cliquer sur "Execute"**

**❌ ERREUR ATTENDUE :**
```json
{
  "code": [
    "Ce champ est obligatoire."
  ]
}
```
**Code HTTP :** `400 Bad Request`

**💡 Analyse :** Le champ "code" est obligatoire et manque.

---

### 2.3 - Deuxième tentative (ÉCHEC - Type invalide)

**Body avec type incorrect :**
```json
{
  "nom": "Formule Star 5G",
  "code": "STAR5G",
  "type_forfait": "ULTRA",
  "prix_mensuel": 25000
}
```

**❌ ERREUR ATTENDUE :**
```json
{
  "type_forfait": [
    "\"ULTRA\" n'est pas un choix valide."
  ]
}
```
**Code HTTP :** `400 Bad Request`

**💡 Analyse :** Les types valides sont : DATA, VOIX, SMS, MIXTE

---

### 2.4 - Troisième tentative (SUCCÈS)

**Body correct et complet :**
```json
{
  "nom": "Formule Star 5G",
  "code": "STAR5G",
  "type_forfait": "MIXTE",
  "prix_mensuel": 25000,
  "quota_data_mo": 5000,
  "quota_minutes": 200,
  "quota_sms": 100,
  "description": "Forfait premium avec 5G",
  "est_actif": true
}
```

**Cliquer sur "Execute"**

**✅ RÉPONSE ATTENDUE :**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nom": "Formule Star 5G",
  "code": "STAR5G",
  "type_forfait": "MIXTE",
  "prix_mensuel": "25000.00",
  "quota_data_mo": 5000,
  "quota_minutes": 200,
  "quota_sms": 100,
  "description": "Forfait premium avec 5G",
  "est_actif": true,
  "date_creation": "2026-07-22T16:30:00Z",
  "date_modification": "2026-07-22T16:30:00Z"
}
```
**Code HTTP :** `201 Created`

**💡 Action :** **COPIER L'ID** du forfait créé (le UUID) pour plus tard !

---

### 2.5 - Quatrième tentative (ÉCHEC - Doublon)

**Essayer de créer le même forfait :**
```json
{
  "nom": "Formule Star 5G",
  "code": "STAR5G",
  "type_forfait": "MIXTE",
  "prix_mensuel": 25000
}
```

**❌ ERREUR ATTENDUE :**
```json
{
  "code": [
    "package avec ce code existe déjà."
  ]
}
```
**Code HTTP :** `400 Bad Request`

**💡 Analyse :** Le code doit être unique. Le forfait existe déjà.

---

## 🔧 ÉTAPE 3 : CRÉER UN SERVICE

### 3.1 - Trouver l'endpoint

1. Dans **"billing"**, trouver **POST `/api/billing/services/`**
2. Cliquer sur **"Try it out"**

---

### 3.2 - Première tentative (ÉCHEC - Sans authentification)

**Supposons que le token a expiré (après 2h)...**

**❌ ERREUR POSSIBLE :**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```
**Code HTTP :** `401 Unauthorized`

**Solution :**
1. Retourner à **POST `/api/auth/login/`**
2. Se reconnecter
3. Copier le nouveau token "access"
4. Cliquer sur **"Authorize"** 🔒
5. Coller le nouveau token
6. Réessayer

---

### 3.3 - Deuxième tentative (SUCCÈS)

**Body :**
```json
{
  "nom": "Data Boost",
  "code": "BOOST",
  "type_service": "OPTION",
  "description": "Booster de data haute vitesse",
  "est_actif": true
}
```

**✅ RÉPONSE ATTENDUE :**
```json
{
  "id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
  "nom": "Data Boost",
  "code": "BOOST",
  "type_service": "OPTION",
  "description": "Booster de data haute vitesse",
  "est_actif": true,
  "nombre_tarifs": 0,
  "date_creation": "2026-07-22T16:35:00Z",
  "date_modification": "2026-07-22T16:35:00Z"
}
```
**Code HTTP :** `201 Created`

**💡 Action :** **COPIER L'ID** du service créé !

---

## 💰 ÉTAPE 4 : CRÉER UN TARIF POUR LE SERVICE

### 4.1 - Trouver l'endpoint

1. Dans **"billing"**, trouver **POST `/api/billing/tarifs-services/`**
2. Cliquer sur **"Try it out"**

---

### 4.2 - Première tentative (ÉCHEC - Service inexistant)

**Body avec un faux UUID :**
```json
{
  "service": "00000000-0000-0000-0000-000000000000",
  "nom_option": "Pass 24h",
  "prix": 3000,
  "duree_validite_heures": 24,
  "est_actif": true
}
```

**❌ ERREUR ATTENDUE :**
```json
{
  "service": [
    "Objet avec id=00000000-0000-0000-0000-000000000000 n'existe pas."
  ]
}
```
**Code HTTP :** `400 Bad Request`

**💡 Analyse :** L'ID du service n'existe pas dans la base.

---

### 4.3 - Deuxième tentative (SUCCÈS)

**Body avec le bon UUID du service créé à l'étape 3.3 :**
```json
{
  "service": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
  "nom_option": "Pass 24h",
  "prix": 3000,
  "duree_validite_heures": 24,
  "description": "Accès illimité pendant 24h",
  "est_actif": true
}
```

**✅ RÉPONSE ATTENDUE :**
```json
{
  "id": "c3d4e5f6-g7h8-9012-cdef-123456789012",
  "service": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
  "service_nom": "Data Boost",
  "nom_option": "Pass 24h",
  "prix": "3000.00",
  "duree_validite_heures": 24,
  "description": "Accès illimité pendant 24h",
  "est_actif": true,
  "date_creation": "2026-07-22T16:40:00Z",
  "date_modification": "2026-07-22T16:40:00Z"
}
```
**Code HTTP :** `201 Created`

---

## 🧮 ÉTAPE 5 : CRÉER UNE SIMULATION

### 5.1 - Trouver l'endpoint

1. Dans **"billing"**, trouver **POST `/api/billing/simulations/`**
2. Cliquer sur **"Try it out"**

---

### 5.2 - Première tentative (ÉCHEC - JSON mal formé)

**Body avec erreur de syntaxe :**
```json
{
  "montant_estime": 30000,
  "services_selectionnes": [
    {
      "nom": "Data Boost",
      "prix": 3000
    }
  
  "resultat_detaille": {
    "forfait": 25000,
    "services": 3000
  }
}
```

**❌ ERREUR ATTENDUE :**
```
Parse error: Expected ',' or ']' after array element
```
**Code HTTP :** Erreur avant l'envoi

**💡 Analyse :** Il manque une `]` après le premier tableau.

---

### 5.3 - Deuxième tentative (SUCCÈS)

**Body correct :**
```json
{
  "montant_estime": 30000,
  "services_selectionnes": [
    {
      "nom": "Data Boost",
      "code": "BOOST",
      "prix": 3000
    },
    {
      "nom": "International",
      "code": "INT",
      "prix": 2000
    }
  ],
  "resultat_detaille": {
    "forfait_base": 25000,
    "services_optionnels": 5000,
    "montant_ht": 30000,
    "tva": 5400,
    "montant_ttc": 35400
  }
}
```

**✅ RÉPONSE ATTENDUE :**
```json
{
  "id": "d4e5f6g7-h8i9-0123-defg-234567890123",
  "utilisateur": 1,
  "utilisateur_nom": " ",
  "date_simulation": "2026-07-22T16:45:00Z",
  "montant_estime": "30000.00",
  "services_selectionnes": [
    {
      "nom": "Data Boost",
      "code": "BOOST",
      "prix": 3000
    },
    {
      "nom": "International",
      "code": "INT",
      "prix": 2000
    }
  ],
  "resultat_detaille": {
    "forfait_base": 25000,
    "services_optionnels": 5000,
    "montant_ht": 30000,
    "tva": 5400,
    "montant_ttc": 35400
  }
}
```
**Code HTTP :** `201 Created`

---

## 📋 ÉTAPE 6 : VÉRIFIER LES SIMULATIONS

### 6.1 - Récupérer MES simulations

1. Trouver **GET `/api/billing/simulations/mes_simulations/`**
2. Cliquer sur **"Try it out"**
3. Cliquer sur **"Execute"** (pas de paramètres requis)

**✅ RÉPONSE ATTENDUE :**
```json
[
  {
    "id": "d4e5f6g7-h8i9-0123-defg-234567890123",
    "utilisateur": 1,
    "utilisateur_nom": " ",
    "date_simulation": "2026-07-22T16:45:00Z",
    "montant_estime": "30000.00",
    "services_selectionnes": [...],
    "resultat_detaille": {...}
  }
]
```
**Code HTTP :** `200 OK`

---

## 🔄 ÉTAPE 7 : DÉSACTIVER LE FORFAIT

### 7.1 - Toggle le forfait

1. Trouver **PATCH `/api/billing/packages/{id}/toggle_actif/`**
2. Cliquer sur **"Try it out"**
3. Dans **id**, coller l'UUID du forfait (étape 2.4)
4. Cliquer sur **"Execute"**

**✅ RÉPONSE ATTENDUE :**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nom": "Formule Star 5G",
  "code": "STAR5G",
  "type_forfait": "MIXTE",
  "prix_mensuel": "25000.00",
  "quota_data_mo": 5000,
  "quota_minutes": 200,
  "quota_sms": 100,
  "description": "Forfait premium avec 5G",
  "est_actif": false,
  "date_creation": "2026-07-22T16:30:00Z",
  "date_modification": "2026-07-22T16:50:00Z"
}
```
**Code HTTP :** `200 OK`

**💡 Remarque :** `est_actif` est maintenant `false` !

---

### 7.2 - Essayer avec un ID inexistant (ÉCHEC)

**ID bidon :**
```
99999999-9999-9999-9999-999999999999
```

**❌ ERREUR ATTENDUE :**
```json
{
  "detail": "Pas trouvé."
}
```
**Code HTTP :** `404 Not Found`

---

## 📊 RÉCAPITULATIF DES ERREURS

| Code | Erreur | Cause | Solution |
|------|--------|-------|----------|
| **400** | Bad Request | Données invalides/manquantes | Vérifier les champs requis |
| **401** | Unauthorized | Pas de token ou token expiré | Se reconnecter |
| **403** | Forbidden | Pas les permissions | Vérifier le rôle utilisateur |
| **404** | Not Found | ID inexistant | Vérifier l'UUID |
| **500** | Internal Server Error | Erreur serveur | Regarder la console Django |

---

## ✅ RÉSULTAT FINAL

**Ce que tu as fait :**
1. ✅ Connexion réussie
2. ✅ Forfait "Formule Star 5G" créé
3. ✅ Service "Data Boost" créé
4. ✅ Tarif "Pass 24h" créé pour le service
5. ✅ Simulation de facturation créée
6. ✅ Liste des simulations récupérée
7. ✅ Forfait désactivé

**Erreurs gérées :**
- ❌ Mot de passe incorrect → Corrigé
- ❌ Champ obligatoire manquant → Ajouté
- ❌ Type invalide → Corrigé
- ❌ Code en doublon → Identifié
- ❌ Token expiré → Reconnexion
- ❌ Service inexistant → UUID corrigé
- ❌ JSON mal formé → Syntaxe corrigée
- ❌ ID inexistant → Identifié

---

## 🎯 PROCHAINS CAS À TESTER

1. **Créer une entreprise** → Créer une facture → Changer le statut → Voir l'historique
2. **Créer une ligne** → Activer un service (cycle) → Voir les cycles de la ligne
3. **Créer une publication** → Voir mes publications
4. **Lister les tarifs** d'un service spécifique

---

**Bon test ! 🚀**
