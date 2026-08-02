# Phase 4 : Facturation Complète ✅

Date : 30 juillet 2026  
Framework : Django 6.0.3 + Django REST Framework

---

## 📋 Ce qui a été implémenté

### 1. Service de Calcul Tarification

**Fichier** : `billing/services/calcul_tarification.py`

**Classe principale** : `CalculateurTarification`

#### Tarifs implémentés :

**DATA** - Paliers jusqu'à 275 Go :
- 0.5 Go → 1000 FCFA
- 1 Go → 2000 FCFA
- 2 Go → 3000 FCFA
- 3 Go → 4000 FCFA
- 5 Go → 5000 FCFA
- 10 Go → 8000 FCFA
- 20 Go → 12000 FCFA
- 50 Go → 20000 FCFA
- 100 Go → 35000 FCFA
- 150 Go → 45000 FCFA
- 200 Go → 55000 FCFA
- 250 Go → 65000 FCFA
- 275 Go → 75000 FCFA
- **> 275 Go** → 5 FCFA/Mo + 50000 FCFA fixe

**VOIX** :
- 79 FCFA/minute
- Facteur moyen 85% (simulation appels 0-30s / >30s)

**SMS** :
- 30 FCFA/unité

**TVA** :
- 18% (Togo)

#### Méthodes disponibles :

```python
# Calcul DATA
calculer_data(volume_mo, forfait_mo=0) -> Dict

# Calcul VOIX
calculer_voix(duree_secondes, forfait_minutes=0) -> Dict

# Calcul SMS
calculer_sms(nombre_sms, forfait_sms=0) -> Dict

# Calcul TVA
calculer_tva(montant_ht) -> Dict

# Calcul facture complète
calculer_facture_ligne(
    forfait_prix,
    forfait_data_mo=0,
    forfait_minutes=0,
    forfait_sms=0,
    conso_data_mo=0,
    conso_duree_secondes=0,
    conso_sms=0,
    services_supplementaires=None
) -> Dict
```

---

### 2. API Gestion des Factures

**ViewSet** : `InvoiceViewSet`

#### Endpoints disponibles :

**GET `/api/billing/invoices/`** - Liste des factures
- Filtres : `?company=1&statut=PUBLIEE&periode_debut=2026-07-01`
- Recherche : `?search=FAC-C26TEST001`
- Tri : `?ordering=-date_emission`

**POST `/api/billing/invoices/`** - Créer une facture manuelle
```json
{
  "company": 1,
  "numero_facture": "FAC-C26TEST-202607-001",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "montant_ht": "15000",
  "montant_tva": "2700",
  "montant_ttc": "17700",
  "date_echeance": "2026-08-30",
  "commentaire": "Facture manuelle"
}
```

**GET `/api/billing/invoices/{id}/`** - Détail facture

**PUT/PATCH `/api/billing/invoices/{id}/`** - Modifier facture brouillon

**DELETE `/api/billing/invoices/{id}/`** - Supprimer facture brouillon

**POST `/api/billing/invoices/generate/`** - **Générer factures en masse**
```json
{
  "cycle": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "company_ids": [1, 2, 3]  // Optionnel, vide = toutes
}
```

**POST `/api/billing/invoices/calculate_line/`** - Calculer facture ligne
```json
{
  "line_id": 1,
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "conso_data_mo": 2048,
  "conso_duree_secondes": 3600,
  "conso_sms": 100,
  "services_supplementaires": [
    {"nom": "BlackBerry", "prix": "1000"},
    {"nom": "No Limit 24h", "prix": "500"}
  ]
}
```

**POST `/api/billing/invoices/{id}/valider/`** - Valider facture
```json
{
  "commentaire": "Validation après vérification"
}
```

**POST `/api/billing/invoices/{id}/annuler/`** - Annuler facture
```json
{
  "raison": "Erreur de calcul, nouvelle facture à générer"
}
```

**POST `/api/billing/invoices/{id}/attach_pdf/`** - Attacher PDF
```
Content-Type: multipart/form-data
fichier: [PDF file]
```

**GET `/api/billing/invoices/stats/`** - Statistiques globales

---

### 3. API Gestion des Publications

**ViewSet** : `PublicationViewSet`

#### Endpoints disponibles :

**GET `/api/billing/publications/`** - Liste des publications
- Filtres : `?agent=1&cycle_facturation=HYB&statut=PUBLIEE`
- Tri : `?ordering=-date_publication`

**POST `/api/billing/publications/`** - Créer une publication
```json
{
  "cycle_facturation": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "commentaire": "Publication cycle hybride juillet 2026"
}
```

**GET `/api/billing/publications/{id}/`** - Détail publication

**POST `/api/billing/publications/{id}/publish/`** - **Publier factures en masse**
```json
{
  "invoice_ids": [
    "uuid-facture-1",
    "uuid-facture-2",
    "uuid-facture-3"
  ],
  "commentaire": "Publication validée"
}
```

**GET `/api/billing/publications/{id}/stats/`** - Statistiques publication

---

## 🔐 Permissions Phase 4

### Matrice des Permissions

| Action | Admin | Chef | Agent | Payeur | Employé |
|--------|-------|------|-------|--------|---------|
| **Factures** |
| Voir toutes | ✅ | ✅ | ✅ | ❌ | ❌ |
| Voir siennes | - | - | - | ✅ | ❌ |
| Générer | ✅ | ✅ | ✅ | ❌ | ❌ |
| Calculer | ✅ | ✅ | ✅ | ❌ | ❌ |
| Créer manuellement | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modifier brouillon | ✅ | ✅ | ✅ | ❌ | ❌ |
| Valider | ✅ | ✅ | ✅ | ❌ | ❌ |
| Annuler | ✅ | ✅ | ✅ | ❌ | ❌ |
| Attacher PDF | ✅ | ✅ | ✅ | ❌ | ❌ |
| Télécharger PDF | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Publications** |
| Créer | ✅ | ✅ | ✅ | ❌ | ❌ |
| Publier factures | ✅ | ✅ | ✅ | ❌ | ❌ |
| Voir statistiques | ✅ | ✅ | ✅ | ❌ | ❌ |

### Classes de Permissions Créées

```python
CanGenerateInvoices      # Générer factures
CanManageInvoices        # Gérer factures (CRUD)
CanUploadPDF             # Upload PDF
CanValidateInvoices      # Valider/Annuler
```

---

## 📊 Workflow de Facturation

### Statuts des Factures

```
BROUILLON → EN_COURS → VALIDEE → PUBLIEE → PAYEE
                ↓
            ANNULEE
```

### Processus Complet

1. **Génération** (Agent)
   - `POST /api/billing/invoices/generate/`
   - Statut initial : `BROUILLON`
   - Modifiable, supprimable

2. **Validation** (Agent/Chef)
   - `POST /api/billing/invoices/{id}/valider/`
   - Passage à `EN_COURS`
   - Verrouillée pour modification

3. **Attachement PDF** (Agent)
   - `POST /api/billing/invoices/{id}/attach_pdf/`
   - Passage automatique à `VALIDEE`

4. **Publication** (Agent/Chef)
   - Créer publication : `POST /api/billing/publications/`
   - Publier factures : `POST /api/billing/publications/{id}/publish/`
   - Passage à `PUBLIEE`
   - Visible pour les clients

5. **Paiement** (Manuel - à venir)
   - Marquage en `PAYEE`
   - Suivi des paiements

### Historique & Audit

Chaque action sur une facture crée une entrée dans `HistoriqueFacturation` :
- Type d'action (CREATION, VALIDATION, PUBLICATION, etc.)
- Utilisateur
- Ancien et nouveau statut
- Commentaire
- Date/heure

---

## 🧪 Tests Automatisés

### Tests Calcul Tarification (10 tests)

**Fichier** : `CalculTarificationTests`

- ✅ Calcul DATA dans forfait
- ✅ Calcul DATA palier 1 Go
- ✅ Calcul DATA palier 5 Go
- ✅ Calcul DATA hors paliers (> 275 Go)
- ✅ Calcul VOIX dans forfait
- ✅ Calcul VOIX hors forfait
- ✅ Calcul SMS dans forfait
- ✅ Calcul SMS hors forfait
- ✅ Calcul TVA 18%
- ✅ Calcul facture ligne complète

### Tests API Factures (7 tests)

**Fichier** : `InvoiceTests`

- ✅ Liste factures (agent)
- ✅ Liste factures (payeur - filtrage)
- ✅ Génération factures en masse
- ✅ Calcul facture ligne
- ✅ Validation facture
- ✅ Annulation facture
- ✅ Statistiques factures

### Tests API Publications (3 tests)

**Fichier** : `PublicationTests`

- ✅ Création publication
- ✅ Publication factures en masse
- ✅ Statistiques publication

**Total Phase 4** : **20 tests** ✅

### Lancer les Tests

```bash
# Tous les tests billing (Phases 2, 3, 4)
python manage.py test billing

# Tests Phase 4 uniquement
python manage.py test billing.tests.CalculTarificationTests
python manage.py test billing.tests.InvoiceTests
python manage.py test billing.tests.PublicationTests

# Test spécifique
python manage.py test billing.tests.InvoiceTests.test_generate_invoices
```

---

## 🎯 Scénarios d'Utilisation

### Scénario 1 : Génération Mensuelle (Cycle HYB)

```bash
# 1. Générer toutes les factures du mois
POST /api/billing/invoices/generate/
{
  "cycle": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31"
}

# 2. Vérifier les factures générées
GET /api/billing/invoices/?statut=BROUILLON&periode_debut=2026-07-01

# 3. Valider une par une après vérification
POST /api/billing/invoices/{id}/valider/
{
  "commentaire": "Montants vérifiés"
}

# 4. Attacher les PDF
POST /api/billing/invoices/{id}/attach_pdf/
[Upload fichier PDF]

# 5. Créer une publication
POST /api/billing/publications/
{
  "cycle_facturation": "HYB",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31"
}

# 6. Publier toutes les factures validées
POST /api/billing/publications/{pub-id}/publish/
{
  "invoice_ids": ["uuid1", "uuid2", "uuid3", ...]
}
```

### Scénario 2 : Calcul Facture Ligne Individuelle

```bash
# Calculer pour une ligne spécifique
POST /api/billing/invoices/calculate_line/
{
  "line_id": 42,
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "conso_data_mo": 15360,  // 15 Go
  "conso_duree_secondes": 7200,  // 2 heures
  "conso_sms": 250,
  "services_supplementaires": [
    {"nom": "BlackBerry 1Go", "prix": "2000"},
    {"nom": "No Limit 24h", "prix": "500"}
  ]
}

# Réponse :
{
  "ligne": {
    "msisdn": "90123456",
    "utilisateur": "Jean Dupont",
    "company": "Entreprise XYZ"
  },
  "calcul": {
    "forfait": {
      "prix": "10000",
      "data_mo": 5120,
      "minutes": 200,
      "sms": 100
    },
    "consommations": {
      "data": {
        "volume_hors_forfait_mo": 10240,
        "palier_applique": "10.0 Go",
        "montant_ht": "8000"
      },
      "voix": {
        "duree_hors_forfait_minutes": 0,
        "montant_ht": "0"
      },
      "sms": {
        "nombre_hors_forfait_sms": 150,
        "montant_ht": "4500"
      }
    },
    "hors_forfait": {
      "total": "12500"
    },
    "services_supplementaires": {
      "montant": "2500"
    },
    "totaux": {
      "forfait": "10000",
      "hors_forfait": "12500",
      "services": "2500",
      "montant_ht": "25000",
      "montant_tva": "4500",
      "montant_ttc": "29500"
    }
  }
}
```

### Scénario 3 : Annulation et Correction

```bash
# 1. Détecter une erreur dans une facture
GET /api/billing/invoices/{id}/

# 2. Annuler la facture erronée
POST /api/billing/invoices/{id}/annuler/
{
  "raison": "Erreur de saisie consommation DATA"
}

# 3. Générer une nouvelle facture corrigée
POST /api/billing/invoices/
{
  "company": 1,
  "numero_facture": "FAC-C26TEST-202607-001-CORR",
  "periode_debut": "2026-07-01",
  "periode_fin": "2026-07-31",
  "montant_ht": "20000",
  "montant_tva": "3600",
  "montant_ttc": "23600",
  "date_echeance": "2026-08-30",
  "commentaire": "Facture corrective suite erreur FAC-xxx-001"
}
```

### Scénario 4 : Statistiques Globales

```bash
# Voir les stats de toutes les factures
GET /api/billing/invoices/stats/

# Réponse :
{
  "total_factures": 150,
  "factures_par_statut": {
    "BROUILLON": 10,
    "EN_COURS": 5,
    "VALIDEE": 15,
    "PUBLIEE": 115,
    "PAYEE": 5
  },
  "montant_total_ttc": "12500000",
  "montant_par_statut": {
    "PUBLIEE": "10000000",
    "PAYEE": "2000000",
    ...
  }
}
```

---

## 📁 Structure des Fichiers Phase 4

```
billing/
├── services/
│   ├── __init__.py
│   └── calcul_tarification.py (NEW - Service calcul tarifs)
├── models.py (déjà existants : Invoice, Publication, etc.)
├── serializers.py
│   ├── InvoiceSerializer (NEW)
│   ├── InvoiceListSerializer (NEW)
│   ├── InvoiceCreateSerializer (NEW)
│   ├── GenerateInvoiceSerializer (NEW)
│   ├── CalculLineInvoiceSerializer (NEW)
│   ├── ValiderInvoiceSerializer (NEW)
│   ├── AnnulerInvoiceSerializer (NEW)
│   ├── HistoriqueFacturationSerializer (NEW)
│   ├── PublicationSerializer (NEW)
│   ├── PublicationListSerializer (NEW)
│   ├── PublicationCreateSerializer (NEW)
│   ├── PublishInvoicesSerializer (NEW)
│   ├── UploadPDFSerializer (NEW)
│   └── InvoiceStatsSerializer (NEW)
├── views.py
│   ├── InvoiceViewSet (NEW)
│   └── PublicationViewSet (NEW)
├── urls.py (ajout 2 routes)
└── tests.py
    ├── CalculTarificationTests (NEW - 10 tests)
    ├── InvoiceTests (NEW - 7 tests)
    └── PublicationTests (NEW - 3 tests)
```

```
accounts/
└── permissions.py
    ├── CanGenerateInvoices (NEW)
    ├── CanManageInvoices (NEW)
    ├── CanUploadPDF (NEW)
    └── CanValidateInvoices (NEW)
```

---

## 📈 Métriques Phase 4

### Code
- **1 Service** : calcul_tarification.py
- **14 Serializers** nouveaux
- **2 ViewSets** : Invoice, Publication
- **4 Permissions** personnalisées
- **~25 Endpoints** REST

### Tests
- **20 Tests** automatisés
- **3 Suites** de tests (Calcul, Invoice, Publication)

### Fonctionnalités
- ✅ Calcul tarification DATA/VOIX/SMS avec paliers
- ✅ Génération factures en masse
- ✅ Calcul facture ligne individuelle
- ✅ Workflow complet (BROUILLON → PUBLIEE)
- ✅ Validation et annulation
- ✅ Upload et attachement PDF
- ✅ Publication en masse
- ✅ Historique complet avec audit
- ✅ Statistiques globales
- ✅ Filtrage par rôle (Agent, Payeur)

---

## 🚀 Prochaines Étapes

### Phase 4.1 - Upload & Découpage PDF (À venir)
- Service de découpage PDF automatique
- Extraction par MSISDN/numéro client
- Génération PDF individuels
- Compression et optimisation

### Phase 4.2 - Notifications (À venir)
- Email de notification après publication
- SMS de notification
- Templates personnalisables

### Phase 4.3 - Paiements (À venir)
- Suivi des paiements
- Marquage PAYEE
- Historique paiements
- Rapprochement bancaire

---

## ✅ Checklist Phase 4

- ✅ Service calcul tarification
- ✅ API génération factures
- ✅ API gestion factures (CRUD)
- ✅ API publications
- ✅ Workflow statuts complets
- ✅ Permissions granulaires
- ✅ Historique & audit
- ✅ Upload PDF (base)
- ✅ Tests automatisés (20 tests)
- ✅ Documentation complète

---

**Développé pour** : Moov Africa Togo  
**Projet** : Portail e-Billings  
**Framework** : Django 6.0.3 + Django REST Framework  
**Phase** : 4/4 - Facturation Complète ✅  
**Date** : 30 juillet 2026
