# Phase 3 : Tarification & Services ✅

## 📋 Ce qui a été implémenté

### 1. API Gestion des Forfaits (Packages)

#### Endpoints disponibles :

**GET `/api/billing/packages/`** - Liste des forfaits
- Filtres : `?type_forfait=DATA&est_actif=true`
- Recherche : `?search=Premium`
- Tri : `?ordering=-prix_mensuel`

**POST `/api/billing/packages/`** - Créer un forfait
```json
{
  "nom": "Forfait Premium",
  "code": "PREM5000",
  "type_forfait": "MIXTE",
  "prix_mensuel": "5000",
  "quota_data_mo": 5120,
  "quota_minutes": 200,
  "quota_sms": 100,
  "description": "Forfait complet avec data, voix et SMS"
}
```

**GET `/api/billing/packages/{id}/`** - Détail forfait

**PUT/PATCH `/api/billing/packages/{id}/`** - Modifier forfait

**DELETE `/api/billing/packages/{id}/`** - Supprimer forfait

**POST `/api/billing/packages/{id}/toggle_actif/`** - Activer/Désactiver

---

### 2. API Gestion des Services

#### Endpoints disponibles :

**GET `/api/billing/services/`** - Liste des services
- Filtres : `?type_service=OPTION&est_actif=true`
- Recherche : `?search=BlackBerry`

**POST `/api/billing/services/`** - Créer un service avec tarifs
```json
{
  "nom": "BlackBerry",
  "code": "BB",
  "type_service": "OPTION",
  "description": "Service BlackBerry avec plusieurs options",
  "tarifs": [
    {
      "nom_option": "BB 500 Mo",
      "prix": "1000",
      "duree_validite_heures": 720
    },
    {
      "nom_option": "BB 1 Go",
      "prix": "2000",
      "duree_validite_heures": 720
    }
  ]
}
```

**GET `/api/billing/services/{id}/`** - Détail service avec tarifs

**PUT/PATCH `/api/billing/services/{id}/`** - Modifier service

**DELETE `/api/billing/services/{id}/`** - Supprimer service

**POST `/api/billing/services/{id}/toggle_actif/`** - Activer/Désactiver

**GET `/api/billing/services/{id}/tarifs/`** - Liste tarifs du service
- Filtre : `?actif_only=true`

---

### 3. API Gestion des Tarifs de Services

#### Endpoints disponibles :

**GET `/api/billing/tarifs/`** - Liste des tarifs
- Filtres : `?service={id}&est_actif=true`
- Recherche : `?search=24h`

**POST `/api/billing/tarifs/`** - Créer un tarif
```json
{
  "service": "uuid-du-service",
  "nom_option": "No Limit 24h",
  "prix": "500",
  "duree_validite_heures": 24,
  "description": "Pass data illimité 24h"
}
```

**GET `/api/billing/tarifs/{id}/`** - Détail tarif

**PUT/PATCH `/api/billing/tarifs/{id}/`** - Modifier tarif

**DELETE `/api/billing/tarifs/{id}/`** - Supprimer tarif

**POST `/api/billing/tarifs/{id}/toggle_actif/`** - Activer/Désactiver

---

## 🔐 Permissions

### Forfaits (Packages)
| Rôle | Liste | Créer | Modifier | Supprimer | Toggle Actif |
|------|-------|-------|----------|-----------|--------------|
| **SUPER_ADMIN** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CHEF_FACTURATION** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AGENT_FACTURATION** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **PAYEUR** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **EMPLOYE** | ✅ | ❌ | ❌ | ❌ | ❌ |

### Services & Tarifs
| Rôle | Liste | Créer | Modifier | Supprimer | Toggle Actif |
|------|-------|-------|----------|-----------|--------------|
| **SUPER_ADMIN** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CHEF_FACTURATION** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **AGENT_FACTURATION** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **PAYEUR** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **EMPLOYE** | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 📊 Modèles de Données

### Package (Forfait)
```json
{
  "id": "uuid",
  "nom": "Forfait Premium",
  "code": "PREM5000",
  "type_forfait": "MIXTE",  // DATA, VOIX, SMS, MIXTE
  "prix_mensuel": "5000.00",
  "quota_data_mo": 5120,
  "quota_minutes": 200,
  "quota_sms": 100,
  "description": "Forfait complet",
  "est_actif": true,
  "date_creation": "2026-07-30T10:00:00Z",
  "date_modification": "2026-07-30T12:00:00Z"
}
```

### Service
```json
{
  "id": "uuid",
  "nom": "BlackBerry",
  "code": "BB",
  "type_service": "OPTION",  // PASS, OPTION, PROMO
  "description": "Service BlackBerry",
  "est_actif": true,
  "tarifs": [
    {
      "id": "uuid",
      "nom_option": "BB 500 Mo",
      "prix": "1000.00",
      "duree_validite_heures": 720,
      "est_actif": true
    }
  ],
  "nombre_tarifs": 2,
  "date_creation": "2026-07-30T10:00:00Z",
  "date_modification": "2026-07-30T12:00:00Z"
}
```

### TarifService (Option)
```json
{
  "id": "uuid",
  "service": "uuid-service",
  "service_name": "BlackBerry",
  "nom_option": "BB 1 Go",
  "prix": "2000.00",
  "duree_validite_heures": 720,
  "description": "Option 1 Go mensuelle",
  "est_actif": true,
  "date_creation": "2026-07-30T10:00:00Z",
  "date_modification": "2026-07-30T12:00:00Z"
}
```

---

## 🚀 Scénarios d'Utilisation

### Scénario 1 : Créer un forfait simple

```bash
POST /api/billing/packages/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nom": "Forfait Data 5Go",
  "code": "DATA5GB",
  "type_forfait": "DATA",
  "prix_mensuel": "3000",
  "quota_data_mo": 5120,
  "description": "Forfait data uniquement 5 Go"
}
```

### Scénario 2 : Créer un service avec options tarifaires

```bash
POST /api/billing/services/
Authorization: Bearer {token}
Content-Type: application/json

{
  "nom": "No Limit",
  "code": "NL",
  "type_service": "PASS",
  "description": "Pass data illimité",
  "tarifs": [
    {
      "nom_option": "NL 24h",
      "prix": "500",
      "duree_validite_heures": 24
    },
    {
      "nom_option": "NL 7j",
      "prix": "2000",
      "duree_validite_heures": 168
    },
    {
      "nom_option": "NL 30j",
      "prix": "5000",
      "duree_validite_heures": 720
    }
  ]
}
```

### Scénario 3 : Ajouter un tarif à un service existant

```bash
POST /api/billing/tarifs/
Authorization: Bearer {token}
Content-Type: application/json

{
  "service": "uuid-du-service-no-limit",
  "nom_option": "NL Weekend",
  "prix": "1000",
  "duree_validite_heures": 48,
  "description": "Pass weekend vendredi-dimanche"
}
```

### Scénario 4 : Désactiver un forfait obsolète

```bash
POST /api/billing/packages/{package-id}/toggle_actif/
Authorization: Bearer {token}
```

### Scénario 5 : Consulter les tarifs actifs d'un service

```bash
GET /api/billing/services/{service-id}/tarifs/?actif_only=true
Authorization: Bearer {token}
```

---

## 🔍 Filtres et Recherche

### Filtrer les forfaits
```bash
# Par type
GET /api/billing/packages/?type_forfait=DATA

# Actifs uniquement
GET /api/billing/packages/?est_actif=true

# Recherche par nom
GET /api/billing/packages/?search=Premium

# Tri par prix
GET /api/billing/packages/?ordering=prix_mensuel
```

### Filtrer les services
```bash
# Par type
GET /api/billing/services/?type_service=OPTION

# Actifs uniquement
GET /api/billing/services/?est_actif=true

# Recherche par nom/code
GET /api/billing/services/?search=BlackBerry
```

### Filtrer les tarifs
```bash
# Par service
GET /api/billing/tarifs/?service={service-id}

# Actifs uniquement
GET /api/billing/tarifs/?est_actif=true

# Recherche par option
GET /api/billing/tarifs/?search=24h
```

---

## 🧪 Tests Automatisés

### Forfaits (3 tests)
- ✅ Liste forfaits
- ✅ Création forfait
- ✅ Toggle actif/inactif

### Services (4 tests)
- ✅ Liste services
- ✅ Création service avec tarifs
- ✅ Récupération tarifs d'un service
- ✅ Toggle actif/inactif

### Tarifs (3 tests)
- ✅ Liste tarifs
- ✅ Création tarif
- ✅ Toggle actif/inactif

**Total Phase 3** : **10 tests** ✅

**Lancer les tests** :
```bash
python manage.py test billing.tests.PackageTests
python manage.py test billing.tests.ServiceTests
python manage.py test billing.tests.TarifServiceTests
```

---

## 📁 Structure des Fichiers

```
billing/
├── models.py
│   ├── Package (Forfait)
│   ├── Service
│   └── TarifService (Options)
├── serializers.py
│   ├── PackageSerializer (+ List, Create)
│   ├── ServiceSerializer (+ List, Create)
│   └── TarifServiceSerializer (+ Create)
├── views.py
│   ├── PackageViewSet
│   ├── ServiceViewSet
│   └── TarifServiceViewSet
├── urls.py (router avec 3 nouveaux viewsets)
└── tests.py (+ 10 tests Phase 3)
```

---

## 💡 Cas d'Usage Métier

### Configuration initiale du système

1. **Chef crée les forfaits de base**
```bash
POST /api/billing/packages/
# Forfait Starter, Premium, Business, etc.
```

2. **Chef crée les services optionnels**
```bash
POST /api/billing/services/
# BlackBerry, No Limit, Roaming, etc.
```

3. **Agent consulte lors de création de contrat**
```bash
GET /api/billing/packages/?est_actif=true
GET /api/billing/services/?est_actif=true
```

### Mise à jour tarifaire

1. **Chef désactive anciens tarifs**
```bash
POST /api/billing/tarifs/{old-tarif-id}/toggle_actif/
```

2. **Chef crée nouveaux tarifs**
```bash
POST /api/billing/tarifs/
# Nouveau pricing pour service existant
```

### Simulation client

1. **Client consulte forfaits disponibles**
```bash
GET /api/billing/packages/?est_actif=true
```

2. **Client consulte services optionnels**
```bash
GET /api/billing/services/?est_actif=true
```

3. **Client voit options d'un service**
```bash
GET /api/billing/services/{service-id}/tarifs/?actif_only=true
```

---

## ✅ Prêt pour Phase 4

**Phase 4** : Facturation (Génération, Calcul, Publication)

Date : 30 juillet 2026
