# 📖 GUIDE COMPLET - Tester l'API avec Swagger

## 🎯 Qu'est-ce que Swagger ?

Swagger est une interface web interactive qui permet de :
- ✅ Voir tous les endpoints de ton API
- ✅ Tester les endpoints directement depuis le navigateur
- ✅ Voir les paramètres requis et optionnels
- ✅ Voir les réponses de l'API en temps réel
- ✅ S'authentifier avec des tokens JWT

---

## 🚀 ÉTAPE 1 : Démarrer le serveur Django

```bash
# 1. Ouvrir un terminal
# 2. Se placer dans le dossier Back
cd "c:\Users\Benoit\Documents\BURRO\Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026\Back"

# 3. Démarrer le serveur
python manage.py runserver
```

✅ Tu dois voir :
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🌐 ÉTAPE 2 : Ouvrir Swagger dans le navigateur

1. Ouvrir ton navigateur (Chrome, Firefox, Edge...)
2. Aller sur : **http://localhost:8000/api/docs/**

✅ Tu vas voir une belle interface avec tous tes endpoints !

---

## 🔐 ÉTAPE 3 : S'authentifier (IMPORTANT)

Avant de tester les endpoints, il faut se connecter pour obtenir un token JWT.

### 3.1 - Trouver l'endpoint de connexion

1. Chercher la section **"auth"** dans Swagger
2. Cliquer sur **POST /api/auth/login/**
3. Cliquer sur le bouton **"Try it out"** (en haut à droite)

### 3.2 - Remplir les informations de connexion

Dans le champ **Request body**, tu vas voir :
```json
{
  "email": "string",
  "password": "string"
}
```

✏️ **Remplacer par :**
```json
{
  "email": "admin@moov.tg",
  "password": "admin123"
}
```

### 3.3 - Exécuter la requête

1. Cliquer sur le gros bouton bleu **"Execute"**
2. Attendre 1-2 secondes

✅ Tu vas voir la **Response** en bas :
```json
{
  "user": {
    "id": 1,
    "email": "admin@moov.tg",
    "username": "admin",
    "role": "SUPER_ADMIN",
    ...
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3.4 - Copier le token d'accès

**IMPORTANT :** Copie le contenu du champ **"access"** (le long texte qui commence par "eyJ...")

Exemple :
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzIxNjY...
```

### 3.5 - Autoriser Swagger avec le token

1. En haut à droite de la page Swagger, cliquer sur le bouton **"Authorize"** (🔓)
2. Dans la popup qui s'ouvre, tu vas voir :
   ```
   Value: Bearer <token>
   ```
3. **Coller ton token** après "Bearer " :
   ```
   Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```
4. Cliquer sur **"Authorize"**
5. Cliquer sur **"Close"**

✅ Le cadenas 🔓 devient fermé 🔒 - Tu es maintenant authentifié !

---

## 📦 ÉTAPE 4 : Tester la création d'un forfait

Maintenant que tu es authentifié, testons la création d'un forfait.

### 4.1 - Trouver l'endpoint

1. Chercher la section **"billing"** dans Swagger
2. Trouver **POST /api/billing/packages/**
3. Cliquer dessus pour l'ouvrir
4. Cliquer sur **"Try it out"**

### 4.2 - Remplir les données du forfait

Tu vas voir le schéma :
```json
{
  "nom": "string",
  "code": "string",
  "type_forfait": "DATA",
  "prix_mensuel": 0,
  "quota_data_mo": 0,
  "quota_minutes": 0,
  "quota_sms": 0,
  "description": "string",
  "est_actif": true
}
```

✏️ **Remplacer par un vrai forfait :**
```json
{
  "nom": "Formule Moon 2",
  "code": "MOON2",
  "type_forfait": "MIXTE",
  "prix_mensuel": 15000,
  "quota_data_mo": 2000,
  "quota_minutes": 100,
  "quota_sms": 50,
  "description": "Forfait complet avec data, appels et SMS",
  "est_actif": true
}
```

### 4.3 - Exécuter

1. Cliquer sur **"Execute"**
2. Regarder la **Response**

✅ **Réponse attendue (201 Created) :**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nom": "Formule Moon 2",
  "code": "MOON2",
  "type_forfait": "MIXTE",
  "prix_mensuel": "15000.00",
  "quota_data_mo": 2000,
  "quota_minutes": 100,
  "quota_sms": 50,
  "description": "Forfait complet avec data, appels et SMS",
  "est_actif": true,
  "date_creation": "2026-07-22T15:30:00Z",
  "date_modification": "2026-07-22T15:30:00Z"
}
```

🎉 **Ton forfait a été créé !**

---

## 📋 ÉTAPE 5 : Lister les forfaits

Vérifions que le forfait a bien été créé.

### 5.1 - Trouver l'endpoint

1. Dans la section **"billing"**
2. Trouver **GET /api/billing/packages/**
3. Cliquer dessus
4. Cliquer sur **"Try it out"**

### 5.2 - Exécuter

1. Cliquer directement sur **"Execute"** (pas besoin de paramètres)
2. Regarder la **Response**

✅ **Tu vas voir la liste de tous les forfaits**, incluant celui que tu viens de créer !

---

## 🔧 ÉTAPE 6 : Tester un service

Créons maintenant un service optionnel.

### 6.1 - Créer un service

1. Trouver **POST /api/billing/services/**
2. Cliquer sur **"Try it out"**
3. Remplir :
```json
{
  "nom": "International",
  "code": "INT",
  "type_service": "PASS",
  "description": "Pass appels internationaux",
  "est_actif": true
}
```
4. Cliquer sur **"Execute"**

✅ **Service créé !** Note son **ID** (tu en auras besoin)

### 6.2 - Créer un tarif pour ce service

1. Trouver **POST /api/billing/tarifs-services/**
2. Cliquer sur **"Try it out"**
3. Remplir (remplace `service_id` par l'ID du service créé) :
```json
{
  "service": "550e8400-e29b-41d4-a716-446655440000",
  "nom_option": "Pass 48h",
  "prix": 2000,
  "duree_validite_heures": 48,
  "description": "Accès illimité pendant 48h",
  "est_actif": true
}
```
4. Cliquer sur **"Execute"**

✅ **Tarif créé pour le service !**

### 6.3 - Récupérer les tarifs d'un service

1. Trouver **GET /api/billing/services/{id}/tarifs/**
2. Cliquer sur **"Try it out"**
3. Dans **id**, coller l'ID du service créé
4. Cliquer sur **"Execute"**

✅ **Tu vas voir tous les tarifs du service !**

---

## 🧮 ÉTAPE 7 : Créer une simulation

Testons maintenant l'historique des simulations.

### 7.1 - Créer une simulation

1. Trouver **POST /api/billing/simulations/**
2. Cliquer sur **"Try it out"**
3. Remplir :
```json
{
  "montant_estime": 25000,
  "services_selectionnes": [
    {
      "nom": "International",
      "code": "INT",
      "prix": 2000
    },
    {
      "nom": "Data Boost",
      "code": "BOOST",
      "prix": 3000
    }
  ],
  "resultat_detaille": {
    "forfait_base": 15000,
    "services_optionnels": 5000,
    "montant_ht": 20000,
    "tva": 3600,
    "montant_ttc": 25000
  }
}
```
4. Cliquer sur **"Execute"**

✅ **Simulation enregistrée !**

### 7.2 - Voir mes simulations

1. Trouver **GET /api/billing/simulations/mes_simulations/**
2. Cliquer sur **"Try it out"**
3. Cliquer sur **"Execute"**

✅ **Tu vas voir toutes tes simulations !**

---

## 🔄 ÉTAPE 8 : Activer/Désactiver un forfait

Testons la fonction toggle.

### 8.1 - Toggle un forfait

1. Trouver **PATCH /api/billing/packages/{id}/toggle_actif/**
2. Cliquer sur **"Try it out"**
3. Dans **id**, coller l'ID d'un forfait
4. Cliquer sur **"Execute"**

✅ **Le forfait change d'état** (actif → inactif ou vice-versa)

---

## 🗑️ ÉTAPE 9 : Supprimer un élément

### 9.1 - Supprimer un forfait

1. Trouver **DELETE /api/billing/packages/{id}/**
2. Cliquer sur **"Try it out"**
3. Dans **id**, coller l'ID d'un forfait
4. Cliquer sur **"Execute"**

✅ **Réponse 204 No Content** = Suppression réussie !

---

## 📊 RÉSUMÉ DES ENDPOINTS À TESTER

| Endpoint | Méthode | Description | Authentification |
|----------|---------|-------------|-----------------|
| `/api/auth/login/` | POST | Se connecter | ❌ Non |
| `/api/auth/profile/` | GET | Mon profil | ✅ Oui |
| `/api/billing/packages/` | GET | Liste forfaits | ✅ Oui |
| `/api/billing/packages/` | POST | Créer forfait | ✅ Oui |
| `/api/billing/packages/{id}/` | GET | Détail forfait | ✅ Oui |
| `/api/billing/packages/{id}/` | PUT | Modifier forfait | ✅ Oui |
| `/api/billing/packages/{id}/toggle_actif/` | PATCH | Toggle actif | ✅ Oui |
| `/api/billing/packages/{id}/` | DELETE | Supprimer forfait | ✅ Oui |
| `/api/billing/services/` | GET/POST | Services | ✅ Oui |
| `/api/billing/services/{id}/tarifs/` | GET | Tarifs service | ✅ Oui |
| `/api/billing/tarifs-services/` | GET/POST | Tarifs | ✅ Oui |
| `/api/billing/simulations/` | GET/POST | Simulations | ✅ Oui |
| `/api/billing/simulations/mes_simulations/` | GET | Mes simulations | ✅ Oui |
| `/api/billing/publications/` | GET/POST | Publications | ✅ Oui |
| `/api/billing/invoices/` | GET/POST | Factures | ✅ Oui |
| `/api/billing/invoices/{id}/changer_statut/` | POST | Changer statut | ✅ Oui |

---

## ❌ ERREURS COURANTES

### Erreur 401 Unauthorized
**Problème :** Tu n'es pas authentifié ou le token a expiré  
**Solution :** 
1. Se reconnecter avec `/api/auth/login/`
2. Copier le nouveau token "access"
3. Cliquer sur "Authorize" et coller le token

### Erreur 400 Bad Request
**Problème :** Données invalides  
**Solution :** Vérifier que tu as rempli tous les champs requis correctement

### Erreur 404 Not Found
**Problème :** L'ID n'existe pas  
**Solution :** Vérifier l'ID de l'élément

### Erreur 500 Internal Server Error
**Problème :** Erreur serveur  
**Solution :** Regarder la console Django pour voir l'erreur détaillée

---

## 💡 ASTUCES

### 1. Swagger garde tes données
- Les champs restent remplis entre les tests
- Pratique pour retester rapidement

### 2. Copier la commande curl
- En bas de chaque réponse, il y a un bouton "curl"
- Tu peux copier la commande pour l'utiliser dans ton terminal

### 3. Voir le schéma
- Cliquer sur "Schema" pour voir la structure complète des données
- Utile pour comprendre les champs disponibles

### 4. Token expire après 2h
- Si tu as une erreur 401 après longtemps, reconnecte-toi

### 5. Format UUID
- Les IDs sont au format UUID (ex: `550e8400-e29b-41d4-a716-446655440000`)
- Copie-colle toujours l'ID complet

---

## 🎯 EXERCICE PRATIQUE

Essaie de faire cette séquence complète :

1. ✅ Se connecter
2. ✅ Créer un forfait "Formule Star"
3. ✅ Créer un service "Data Boost"
4. ✅ Créer un tarif pour "Data Boost"
5. ✅ Lister tous les forfaits
6. ✅ Lister tous les services
7. ✅ Créer une simulation
8. ✅ Voir mes simulations
9. ✅ Désactiver le forfait "Formule Star"
10. ✅ Supprimer le forfait

---

## 🆘 BESOIN D'AIDE ?

Si quelque chose ne fonctionne pas :

1. **Vérifier que le serveur tourne** : Regarder la console Django
2. **Vérifier l'authentification** : Token bien copié avec "Bearer " ?
3. **Vérifier les données** : Tous les champs requis sont remplis ?
4. **Regarder la console Django** : Les erreurs détaillées s'affichent là

---

## 🎉 FÉLICITATIONS !

Tu sais maintenant utiliser Swagger pour tester ton API ! 

**Avantages de Swagger :**
- ✅ Pas besoin d'installer Postman
- ✅ Interface visuelle claire
- ✅ Documentation à jour automatiquement
- ✅ Facilite les tests rapides
- ✅ Génère des exemples de code

**Bonne chance pour tes tests ! 🚀**
