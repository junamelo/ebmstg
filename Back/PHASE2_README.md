# Phase 2 : Gestion Contrats & Lignes ✅

## 📋 Ce qui a été implémenté

### 1. API Gestion des Contrats (Companies)

#### Endpoints disponibles :

**GET `/api/billing/companies/`** - Liste des contrats
- Filtres : `?categorie=GE&statut=ACTIF&payeur={id}`
- Recherche : `?search=TOTAL`
- Tri : `?ordering=-date_creation`

**POST `/api/billing/companies/`** - Créer un contrat
```json
{
  "compte": "C26000123",
  "raison_sociale": "TOTAL TOGO",
  "categorie": "GE",
  "adresse": "123 Rue de Lomé",
  "adresse2": "contact@totaltogo.com",
  "payeur": 2,
  "lignes": [
    {
      "msisdn": "90123456",
      "utilisateur": "Marie JOHNSON",
      "cycle": "HYB",
      "forfait": "5000"
    }
  ]
}
```

**GET `/api/billing/companies/{id}/`** - Détail contrat avec lignes

**PUT/PATCH `/api/billing/companies/{id}/`** - Modifier contrat

**DELETE `/api/billing/companies/{id}/`** - Supprimer contrat

---

### 2. Actions Spéciales Contrats

**GET `/api/billing/companies/{id}/stats/`** - Statistiques contrat
```json
{
  "company_id": 1,
  "raison_sociale": "TOTAL TOGO",
  "nombre_lignes_total": 15,
  "nombre_lignes_actives": 12,
  "nombre_lignes_suspendues": 2,
  "nombre_lignes_inactives": 1,
  "lignes_par_cycle": {
    "HYB": 8,
    "OP": 7
  },
  "montant_forfaits_total": "125000.00"
}
```

**POST `/api/billing/companies/{id}/change_statut/`** - Changer statut
```json
{
  "nouveau_statut": "SUSPENDU",
  "raison": "Non-paiement"
}
```

**GET `/api/billing/companies/{id}/lignes/`** - Liste lignes du contrat
- Filtres : `?statut=ACTIF&cycle=HYB`

---

### 3. API Gestion des Lignes

#### Endpoints disponibles :

**GET `/api/billing/lines/`** - Liste des lignes
- Filtres : `?company={id}&statut=ACTIF&cycle=HYB&employe={id}`
- Recherche : `?search=90123456`
- Tri : `?ordering=-date_creation`

**POST `/api/billing/lines/`** - Créer une ligne
```json
{
  "company": 1,
  "msisdn": "90123456",
  "utilisateur": "Jean DUPONT",
  "cycle": "OP",
  "forfait": "10000",
  "option_blackberry": "BB1000",
  "est_incognito": false,
  "facture_detaillee": true,
  "employe": 5
}
```

**GET `/api/billing/lines/{id}/`** - Détail ligne

**PUT/PATCH `/api/billing/lines/{id}/`** - Modifier ligne

**DELETE `/api/billing/lines/{id}/`** - Supprimer ligne

---

### 4. Actions Spéciales Lignes

**POST `/api/billing/lines/{id}/assigner_employe/`** - Assigner employé
```json
{
  "employe_id": 5
}
```

**POST `/api/billing/lines/{id}/retirer_employe/`** - Retirer employé

**POST `/api/billing/lines/{id}/change_statut/`** - Changer statut
```json
{
  "nouveau_statut": "ACTIF",
  "raison": "Réactivation après paiement"
}
```

**POST `/api/billing/lines/{id}/change_cycle/`** - Changer cycle
```json
{
  "cycle": "OP"
}
```

---

## 🔐 Permissions par Rôle

### Contrats (Companies)

| Rôle | Liste | Créer | Modifier | Supprimer | Stats | Changer Statut |
|------|-------|-------|----------|-----------|-------|----------------|
| **SUPER_ADMIN** | ✅ Tous | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CHEF_FACTURATION** | ✅ Tous | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AGENT_FACTURATION** | ✅ Tous | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PAYEUR** | ✅ Siens | ❌ | ❌ | ❌ | ✅ | ❌ |
| **EMPLOYE** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### Lignes (Lines)

| Rôle | Liste | Créer | Modifier | Supprimer | Assigner Employé | Changer Statut |
|------|-------|-------|----------|-----------|------------------|----------------|
| **SUPER_ADMIN** | ✅ Toutes | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CHEF_FACTURATION** | ✅ Toutes | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AGENT_FACTURATION** | ✅ Toutes | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PAYEUR** | ✅ Siennes | ❌ | ❌ | ❌ | ❌ | ❌ |
| **EMPLOYE** | ✅ Sa ligne | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🧪 Tests Automatisés

### Contrats (10 tests)
- ✅ Liste contrats par rôle
- ✅ Filtrage payeur
- ✅ Création simple
- ✅ Création avec lignes
- ✅ Statistiques contrat
- ✅ Changement statut
- ✅ Liste lignes d'un contrat

### Lignes (10 tests)
- ✅ Liste lignes par rôle
- ✅ Filtrage employé
- ✅ Création ligne
- ✅ Assignation employé
- ✅ Retrait employé
- ✅ Changement statut
- ✅ Changement cycle

**Lancer les tests** :
```bash
python manage.py test billing
```

---

## 📊 Modèles de Données

### Company (Contrat)
```python
{
  "id": 1,
  "compte": "C26000123",
  "raison_sociale": "TOTAL TOGO",
  "code_commercial": "TOT",
  "nom_commercial": "Total",
  "categorie": "GE",  # GE, PE, P, OI, EP, A, NR
  "adresse": "123 Rue Lomé",
  "adresse2": "contact@total.tg",
  "statut": "ACTIF",  # ACTIF, INACTIF, SUSPENDU
  "payeur": 2,
  "payeur_info": {
    "id": 2,
    "nom": "Jean DUPONT",
    "email": "j.dupont@total.tg"
  },
  "nombre_lignes": 15,
  "nombre_lignes_actives": 12,
  "date_creation": "2026-07-30T10:00:00Z",
  "date_modification": "2026-07-30T12:00:00Z"
}
```

### Line (Ligne)
```python
{
  "id": 1,
  "company": 1,
  "company_name": "TOTAL TOGO",
  "msisdn": "90123456",
  "utilisateur": "Marie JOHNSON",
  "forfait": "5000.00",
  "cycle": "HYB",  # HYB ou OP
  "option_blackberry": "BB1000",
  "option_nolimit": null,
  "est_incognito": false,
  "facture_detaillee": true,
  "est_non_revenu": false,
  "statut": "ACTIF",
  "employe": 5,
  "employe_info": {
    "id": 5,
    "nom": "Marie JOHNSON",
    "email": "m.johnson@total.tg"
  },
  "date_creation": "2026-07-30T10:00:00Z",
  "date_modification": "2026-07-30T12:00:00Z"
}
```

---

## 🚀 Scénarios d'Utilisation

### Scénario 1 : Créer un contrat complet

```bash
# 1. Créer d'abord le compte payeur
POST /api/accounts/users/
{
  "email": "payeur@total.tg",
  "username": "A26000123",
  "password": "Moov@20260730",
  "first_name": "Jean",
  "last_name": "DUPONT",
  "role": "PAYEUR"
}

# 2. Créer le contrat avec lignes
POST /api/billing/companies/
{
  "compte": "C26000123",
  "raison_sociale": "TOTAL TOGO",
  "categorie": "GE",
  "payeur": {id_du_payeur},
  "lignes": [
    {
      "msisdn": "90123456",
      "utilisateur": "Marie JOHNSON",
      "cycle": "HYB",
      "forfait": "5000"
    }
  ]
}

# 3. Créer compte employé pour la ligne
POST /api/accounts/users/
{
  "email": "m.johnson@total.tg",
  "username": "90123456",
  "password": "Moov@20260730",
  "first_name": "Marie",
  "last_name": "JOHNSON",
  "role": "EMPLOYE"
}

# 4. Assigner l'employé à la ligne
POST /api/billing/lines/{line_id}/assigner_employe/
{
  "employe_id": {employe_id}
}
```

### Scénario 2 : Ajouter une ligne à un contrat existant

```bash
POST /api/billing/lines/
{
  "company": 1,
  "msisdn": "90999888",
  "utilisateur": "Paul MARTIN",
  "cycle": "OP",
  "forfait": "10000"
}
```

### Scénario 3 : Suspendre un contrat

```bash
POST /api/billing/companies/1/change_statut/
{
  "nouveau_statut": "SUSPENDU",
  "raison": "Non-paiement facture juillet"
}
```

### Scénario 4 : Consulter les stats d'un contrat

```bash
GET /api/billing/companies/1/stats/
```

---

## 🔍 Filtres et Recherche

### Filtrer les contrats
```bash
# Par catégorie
GET /api/billing/companies/?categorie=GE

# Par statut
GET /api/billing/companies/?statut=ACTIF

# Par payeur
GET /api/billing/companies/?payeur=2

# Recherche texte
GET /api/billing/companies/?search=TOTAL

# Tri
GET /api/billing/companies/?ordering=-date_creation
```

### Filtrer les lignes
```bash
# Par contrat
GET /api/billing/lines/?company=1

# Par statut
GET /api/billing/lines/?statut=ACTIF

# Par cycle
GET /api/billing/lines/?cycle=HYB

# Par employé
GET /api/billing/lines/?employe=5

# Recherche MSISDN
GET /api/billing/lines/?search=90123
```

---

## 📁 Structure des Fichiers

```
billing/
├── models.py (Company, Line + enums)
├── serializers.py (8 serializers)
├── views.py (CompanyViewSet, LineViewSet)
├── urls.py (router avec 2 viewsets)
├── tests.py (20 tests)
└── migrations/
```

---

## ✅ Prêt pour Phase 3

**Phase 3** : Tarification & Services

Date : 30 juillet 2026
