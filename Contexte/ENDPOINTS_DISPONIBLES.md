# ✅ TOUS LES ENDPOINTS DISPONIBLES - À TESTER AVEC SWAGGER

## 🎯 ACCÈS SWAGGER

**URL :** http://localhost:8000/api/docs/

**Prérequis :** 
1. Serveur Django démarré : `python manage.py runserver`
2. Se connecter d'abord avec `/api/auth/login/`
3. Cliquer sur "Authorize" et coller le token

---

## 🔐 AUTHENTIFICATION (3 endpoints)

### 1. POST `/api/auth/login/` ✅
**Description :** Se connecter et obtenir un token JWT  
**Authentification :** ❌ Non requise  
**Body :**
```json
{
  "email": "admin@moov.tg",
  "password": "admin123"
}
```
**Réponse :**
```json
{
  "user": {...},
  "access": "eyJ0eXAiOiJKV1Q...",
  "refresh": "eyJ0eXAiOiJKV1Q..."
}
```

### 2. POST `/api/auth/register/` ✅
**Description :** Créer un nouveau compte  
**Authentification :** ❌ Non requise  
**Body :**
```json
{
  "email": "nouveau@moov.tg",
  "username": "nouveau",
  "password": "motdepasse123",
  "password_confirm": "motdepasse123",
  "first_name": "Jean",
  "last_name": "Dupont",
  "role": "EMPLOYE",
  "telephone": "90123456"
}
```

### 3. GET `/api/auth/profile/` ✅
**Description :** Voir son profil  
**Authentification :** ✅ Requise  
**Pas de paramètres**

---

## 🏢 ENTREPRISES (5 endpoints)

### 1. GET `/api/billing/companies/` ✅
**Description :** Liste de toutes les entreprises  
**Authentification :** ✅ Requise  
**Pas de paramètres**

### 2. POST `/api/billing/companies/` ✅
**Description :** Créer une entreprise  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "compte": "CT-TEST-001",
  "raison_sociale": "Entreprise Test",
  "code_commercial": "7000",
  "nom_commercial": "Test Company",
  "categorie": "PE",
  "adresse": "123 Rue Test",
  "adresse2": "test@example.com",
  "statut": "ACTIF"
}
```

### 3. GET `/api/billing/companies/{id}/` ✅
**Description :** Détail d'une entreprise  
**Authentification :** ✅ Requise  
**Paramètre :** ID de l'entreprise

### 4. PUT `/api/billing/companies/{id}/` ✅
**Description :** Modifier une entreprise  
**Authentification :** ✅ Requise  
**Paramètre :** ID de l'entreprise  
**Body :** Tous les champs de l'entreprise

### 5. DELETE `/api/billing/companies/{id}/` ✅
**Description :** Supprimer une entreprise  
**Authentification :** ✅ Requise  
**Paramètre :** ID de l'entreprise

---

## 📱 LIGNES (5 endpoints)

### 1. GET `/api/billing/lines/` ✅
**Description :** Liste de toutes les lignes  
**Authentification :** ✅ Requise

### 2. POST `/api/billing/lines/` ✅
**Description :** Créer une ligne  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "company": "uuid-de-l-entreprise",
  "msisdn": "79123456",
  "utilisateur": "Jean Dupont",
  "forfait": 15000.00,
  "cycle": "HYB",
  "option_blackberry": "BB15_6",
  "option_nolimit": "AI50",
  "est_incognito": false,
  "facture_detaillee": true,
  "est_non_revenu": false,
  "statut": "ACTIF"
}
```

### 3. GET `/api/billing/lines/{id}/` ✅
**Description :** Détail d'une ligne  
**Authentification :** ✅ Requise

### 4. PUT `/api/billing/lines/{id}/` ✅
**Description :** Modifier une ligne  
**Authentification :** ✅ Requise

### 5. DELETE `/api/billing/lines/{id}/` ✅
**Description :** Supprimer une ligne  
**Authentification :** ✅ Requise

---

## 📦 FORFAITS (6 endpoints)

### 1. GET `/api/billing/packages/` ✅
**Description :** Liste de tous les forfaits  
**Authentification :** ✅ Requise  
**Teste avec :** Rien à remplir, juste Execute !

### 2. POST `/api/billing/packages/` ✅
**Description :** Créer un forfait  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "nom": "Formule Moon 2",
  "code": "MOON2",
  "type_forfait": "MIXTE",
  "prix_mensuel": 15000,
  "quota_data_mo": 2000,
  "quota_minutes": 100,
  "quota_sms": 50,
  "description": "Forfait mixte complet",
  "est_actif": true
}
```
**Types disponibles :** DATA, VOIX, SMS, MIXTE

### 3. GET `/api/billing/packages/{id}/` ✅
**Description :** Détail d'un forfait  
**Authentification :** ✅ Requise  
**Paramètre :** ID du forfait (copie l'ID depuis la liste)

### 4. PUT `/api/billing/packages/{id}/` ✅
**Description :** Modifier un forfait  
**Authentification :** ✅ Requise  
**Paramètre :** ID du forfait  
**Body :** Tous les champs du forfait

### 5. PATCH `/api/billing/packages/{id}/toggle_actif/` ✅
**Description :** Activer/désactiver un forfait  
**Authentification :** ✅ Requise  
**Paramètre :** ID du forfait  
**Pas de body requis !** Juste Execute !

### 6. DELETE `/api/billing/packages/{id}/` ✅
**Description :** Supprimer un forfait  
**Authentification :** ✅ Requise  
**Paramètre :** ID du forfait

---

## 🔧 SERVICES (7 endpoints)

### 1. GET `/api/billing/services/` ✅
**Description :** Liste de tous les services  
**Authentification :** ✅ Requise

### 2. POST `/api/billing/services/` ✅
**Description :** Créer un service  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "nom": "International",
  "code": "INT",
  "type_service": "PASS",
  "description": "Pass appels internationaux",
  "est_actif": true
}
```
**Types disponibles :** PASS, OPTION, PROMO

### 3. GET `/api/billing/services/{id}/` ✅
**Description :** Détail d'un service  
**Authentification :** ✅ Requise

### 4. PUT `/api/billing/services/{id}/` ✅
**Description :** Modifier un service  
**Authentification :** ✅ Requise

### 5. PATCH `/api/billing/services/{id}/toggle_actif/` ✅
**Description :** Activer/désactiver un service  
**Authentification :** ✅ Requise  
**Pas de body !**

### 6. GET `/api/billing/services/{id}/tarifs/` ✅
**Description :** Récupérer tous les tarifs d'un service  
**Authentification :** ✅ Requise  
**Paramètre :** ID du service

### 7. DELETE `/api/billing/services/{id}/` ✅
**Description :** Supprimer un service  
**Authentification :** ✅ Requise

---

## 💰 TARIFS DES SERVICES (5 endpoints)

### 1. GET `/api/billing/tarifs-services/` ✅
**Description :** Liste de tous les tarifs  
**Authentification :** ✅ Requise

### 2. POST `/api/billing/tarifs-services/` ✅
**Description :** Créer un tarif pour un service  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "service": "uuid-du-service",
  "nom_option": "Pass 48h",
  "prix": 2000,
  "duree_validite_heures": 48,
  "description": "Accès illimité pendant 48h",
  "est_actif": true
}
```
**⚠️ Important :** Créer d'abord un service, copier son ID, puis créer le tarif !

### 3. GET `/api/billing/tarifs-services/{id}/` ✅
**Description :** Détail d'un tarif  
**Authentification :** ✅ Requise

### 4. PUT `/api/billing/tarifs-services/{id}/` ✅
**Description :** Modifier un tarif  
**Authentification :** ✅ Requise

### 5. DELETE `/api/billing/tarifs-services/{id}/` ✅
**Description :** Supprimer un tarif  
**Authentification :** ✅ Requise

---

## 📄 FACTURES (6 endpoints)

### 1. GET `/api/billing/invoices/` ✅
**Description :** Liste de toutes les factures  
**Authentification :** ✅ Requise

### 2. POST `/api/billing/invoices/` ✅
**Description :** Créer une facture  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "company": "uuid-de-l-entreprise",
  "numero_facture": "FAC-2026-001",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "montant_ht": 20000.00,
  "montant_tva": 3600.00,
  "montant_ttc": 23600.00,
  "statut": "BROUILLON",
  "date_echeance": "2026-08-15",
  "commentaire": "Facture du mois de juillet"
}
```
**Statuts disponibles :** BROUILLON, EN_COURS, VALIDEE, PUBLIEE, PAYEE, ANNULEE

### 3. GET `/api/billing/invoices/{id}/` ✅
**Description :** Détail d'une facture  
**Authentification :** ✅ Requise

### 4. PUT `/api/billing/invoices/{id}/` ✅
**Description :** Modifier une facture  
**Authentification :** ✅ Requise

### 5. POST `/api/billing/invoices/{id}/changer_statut/` ✅
**Description :** Changer le statut d'une facture (enregistre l'historique)  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "statut": "VALIDEE",
  "commentaire": "Facture validée par l'agent"
}
```

### 6. DELETE `/api/billing/invoices/{id}/` ✅
**Description :** Supprimer une facture  
**Authentification :** ✅ Requise

---

## 📜 HISTORIQUE FACTURATION (3 endpoints)

### 1. GET `/api/billing/historique-facturation/` ✅
**Description :** Liste complète de l'historique  
**Authentification :** ✅ Requise

### 2. GET `/api/billing/historique-facturation/{id}/` ✅
**Description :** Détail d'une entrée d'historique  
**Authentification :** ✅ Requise

### 3. GET `/api/billing/historique-facturation/par_facture/` ✅
**Description :** Historique d'une facture spécifique  
**Authentification :** ✅ Requise  
**Query Parameter :** `invoice_id=uuid-de-la-facture`

**💡 Astuce :** L'historique se remplit automatiquement quand tu utilises `/changer_statut/` !

---

## 🔄 CYCLES LIGNE-SERVICE (6 endpoints)

### 1. GET `/api/billing/cycles/` ✅
**Description :** Liste de tous les cycles  
**Authentification :** ✅ Requise

### 2. POST `/api/billing/cycles/` ✅
**Description :** Créer un cycle (activer un service sur une ligne)  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "line": "uuid-de-la-ligne",
  "service": "uuid-du-service",
  "date_debut": "2026-07-22T10:00:00Z",
  "date_fin": null,
  "est_actif": true
}
```

### 3. GET `/api/billing/cycles/{id}/` ✅
**Description :** Détail d'un cycle  
**Authentification :** ✅ Requise

### 4. PUT `/api/billing/cycles/{id}/` ✅
**Description :** Modifier un cycle  
**Authentification :** ✅ Requise

### 5. GET `/api/billing/cycles/par_ligne/` ✅
**Description :** Récupérer tous les cycles actifs d'une ligne  
**Authentification :** ✅ Requise  
**Query Parameter :** `line_id=uuid-de-la-ligne`

### 6. DELETE `/api/billing/cycles/{id}/` ✅
**Description :** Supprimer un cycle  
**Authentification :** ✅ Requise

---

## 🧮 SIMULATIONS (5 endpoints)

### 1. GET `/api/billing/simulations/` ✅
**Description :** Liste de toutes les simulations  
**Authentification :** ✅ Requise

### 2. POST `/api/billing/simulations/` ✅
**Description :** Créer une simulation  
**Authentification :** ✅ Requise  
**Body :**
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
**⚠️ L'utilisateur est automatiquement celui connecté !**

### 3. GET `/api/billing/simulations/{id}/` ✅
**Description :** Détail d'une simulation  
**Authentification :** ✅ Requise

### 4. GET `/api/billing/simulations/mes_simulations/` ✅
**Description :** Mes simulations (utilisateur connecté uniquement)  
**Authentification :** ✅ Requise  
**Pas de paramètres !**

### 5. DELETE `/api/billing/simulations/{id}/` ✅
**Description :** Supprimer une simulation  
**Authentification :** ✅ Requise

---

## 📰 PUBLICATIONS (5 endpoints)

### 1. GET `/api/billing/publications/` ✅
**Description :** Liste de toutes les publications  
**Authentification :** ✅ Requise

### 2. POST `/api/billing/publications/` ✅
**Description :** Créer une publication  
**Authentification :** ✅ Requise  
**Body :**
```json
{
  "cycle_facturation": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "statut": "PUBLIEE",
  "nombre_lignes_traitees": 150,
  "montant_total": 2500000,
  "commentaire": "Publication du mois de juillet 2026"
}
```
**⚠️ L'agent est automatiquement celui connecté !**

### 3. GET `/api/billing/publications/{id}/` ✅
**Description :** Détail d'une publication  
**Authentification :** ✅ Requise

### 4. GET `/api/billing/publications/mes_publications/` ✅
**Description :** Mes publications (agent connecté uniquement)  
**Authentification :** ✅ Requise

### 5. DELETE `/api/billing/publications/{id}/` ✅
**Description :** Supprimer une publication  
**Authentification :** ✅ Requise

---

## 📊 RÉCAPITULATIF COMPLET

| Catégorie | Nombre d'endpoints | Tous fonctionnels |
|-----------|-------------------|-------------------|
| **Authentification** | 3 | ✅ |
| **Entreprises** | 5 | ✅ |
| **Lignes** | 5 | ✅ |
| **Forfaits** | 6 | ✅ |
| **Services** | 7 | ✅ |
| **Tarifs Services** | 5 | ✅ |
| **Factures** | 6 | ✅ |
| **Historique Facturation** | 3 | ✅ |
| **Cycles** | 6 | ✅ |
| **Simulations** | 5 | ✅ |
| **Publications** | 5 | ✅ |
| **TOTAL** | **56 endpoints** | ✅ **100%** |

---

## 🎯 SCÉNARIOS DE TEST COMPLETS

### Scénario 1 : Gestion des forfaits
1. ✅ Se connecter
2. ✅ Créer un forfait "Formule Moon 2"
3. ✅ Lister les forfaits
4. ✅ Désactiver le forfait
5. ✅ Réactiver le forfait
6. ✅ Modifier le forfait
7. ✅ Supprimer le forfait

### Scénario 2 : Services et tarifs
1. ✅ Créer un service "International"
2. ✅ Créer un tarif "Pass 24h" pour ce service
3. ✅ Créer un tarif "Pass 48h" pour ce service
4. ✅ Lister les tarifs du service
5. ✅ Désactiver le service

### Scénario 3 : Facturation complète
1. ✅ Créer une entreprise
2. ✅ Créer une facture pour cette entreprise
3. ✅ Changer le statut : BROUILLON → EN_COURS
4. ✅ Changer le statut : EN_COURS → VALIDEE
5. ✅ Voir l'historique de la facture
6. ✅ Changer le statut : VALIDEE → PUBLIEE

### Scénario 4 : Simulation
1. ✅ Créer une simulation
2. ✅ Voir mes simulations
3. ✅ Supprimer la simulation

### Scénario 5 : Cycle de service
1. ✅ Créer une ligne
2. ✅ Créer un service
3. ✅ Activer le service sur la ligne (créer un cycle)
4. ✅ Voir les cycles de la ligne

---

## 💡 CONSEILS POUR TESTER

1. **Toujours se connecter en premier** → Récupérer le token
2. **Copier les IDs** → Les UUID sont longs, copie-colle !
3. **Tester dans l'ordre** → Créer avant de modifier
4. **Regarder les réponses** → Code 201 = création OK, 200 = OK, 204 = suppression OK
5. **Utiliser "Schema"** → Voir tous les champs disponibles

---

## 🎉 RÉSULTAT

**TU AS MAINTENANT 56 ENDPOINTS FONCTIONNELS À TESTER !**

Tous les modèles du diagramme de classes sont implémentés et accessibles via Swagger.

**Bon test ! 🚀**
