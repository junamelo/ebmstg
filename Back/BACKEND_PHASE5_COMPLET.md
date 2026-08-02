# 📊 PHASE 5 : DASHBOARDS & STATS - DOCUMENTATION COMPLÈTE

## 🎯 Vue d'ensemble

Cette phase implémente les endpoints de statistiques et dashboards personnalisés pour chaque type d'utilisateur du système.

---

## 🏗️ Architecture

### Fichiers créés/modifiés
```
Back/
├── billing/
│   ├── stats_views.py          # ✅ CRÉÉ - Views des statistiques
│   └── urls.py                 # ✅ MODIFIÉ - Routes stats ajoutées
```

---

## 📡 API ENDPOINTS

### Base URL
```
/api/billing/stats/
```

### Endpoints par rôle

| Rôle | Endpoint | Méthode | Permission |
|------|----------|---------|------------|
| **Admin** | `/stats/admin/` | GET | IsAdmin |
| **Chef Facturation** | `/stats/chef/` | GET | IsChefFacturation |
| **Agent Facturation** | `/stats/agent/` | GET | IsAgentFacturation |
| **Payeur** | `/stats/payeur/` | GET | IsPayeur |
| **Employé** | `/stats/employe/` | GET | IsEmploye |

---

## 🔐 1. STATS ADMIN

### Endpoint
```http
GET /api/billing/stats/admin/
Authorization: Bearer {token}
```

### Description
Statistiques globales du système pour l'administrateur.

### Réponse
```json
{
  "statistiques_globales": {
    "total_entreprises": 150,
    "total_lignes": 3500,
    "total_factures": 1200,
    "montant_total_facture": 450000000.00
  },
  "factures_par_statut": {
    "BROUILLON": 10,
    "EN_COURS": 25,
    "VALIDEE": 30,
    "PUBLIEE": 50,
    "PAYEE": 1085
  },
  "montant_par_statut": {
    "VALIDEE": 12000000.00,
    "PUBLIEE": 25000000.00,
    "PAYEE": 413000000.00
  },
  "evolution_mensuelle": [
    {
      "mois": "2026-01",
      "nombre_factures": 95,
      "montant_total": 38500000.00
    },
    {
      "mois": "2026-02",
      "nombre_factures": 98,
      "montant_total": 39200000.00
    }
  ],
  "top_entreprises": [
    {
      "id": "uuid",
      "compte": "A0000106",
      "raison_sociale": "WACEM SA",
      "total_facture": 85000000.00,
      "nombre_factures": 12
    }
  ],
  "top_lignes": [
    {
      "id": "uuid",
      "msisdn": "79300739",
      "utilisateur": "WACEM SA",
      "company__raison_sociale": "WACEM SA",
      "total_facture": 5500000.00
    }
  ],
  "stats_agents": {
    "total_agents": 15,
    "agents_actifs": 12,
    "total_publications": 450
  },
  "stats_utilisateurs": {
    "total_payeurs": 85,
    "total_employes": 2500,
    "total_simulations": 350
  }
}
```

### Fonctionnalités
- ✅ Vue d'ensemble complète du système
- ✅ Évolution sur 12 derniers mois
- ✅ Top 10 entreprises par chiffre d'affaires
- ✅ Top 10 lignes par consommation
- ✅ Statistiques des agents et utilisateurs

---

## 👔 2. STATS CHEF FACTURATION

### Endpoint
```http
GET /api/billing/stats/chef/
Authorization: Bearer {token}
```

### Description
Statistiques des agents sous la responsabilité du chef facturation.

### Réponse
```json
{
  "agents": [
    {
      "id": "uuid",
      "email": "agent1@moov.tg",
      "nom_complet": "Koffi ATTIOGBE",
      "est_actif": true,
      "nombre_publications": 45,
      "montant_total_publie": 18500000.00,
      "lignes_traitees": 450
    }
  ],
  "performance_equipe": {
    "nombre_agents": 8,
    "agents_actifs": 7,
    "total_publications": 320,
    "montant_total": 125000000.00,
    "moyenne_par_agent": 15625000.00
  },
  "publications_periode": [
    {
      "date": "2026-07-01",
      "nombre": 12,
      "montant": 4500000.00
    },
    {
      "date": "2026-07-02",
      "nombre": 8,
      "montant": 3200000.00
    }
  ]
}
```

### Fonctionnalités
- ✅ Liste des agents avec leurs performances
- ✅ Performance globale de l'équipe
- ✅ Publications sur les 30 derniers jours
- ✅ Suivi de la productivité

---

## 📋 3. STATS AGENT FACTURATION

### Endpoint
```http
GET /api/billing/stats/agent/
Authorization: Bearer {token}
```

### Description
Statistiques personnelles de l'agent de facturation.

### Réponse
```json
{
  "statistiques": {
    "total_publications": 45,
    "montant_total": 18500000.00,
    "lignes_traitees": 450,
    "moyenne_par_publication": 411111.11
  },
  "publications_par_cycle": {
    "HYB": 25,
    "OP": 20
  },
  "evolution_quotidienne": [
    {
      "date": "2026-07-01",
      "nombre": 3,
      "montant": 1200000.00,
      "lignes": 45
    }
  ],
  "dernieres_publications": [
    {
      "id": "uuid",
      "cycle_facturation": "OP",
      "periode_debut": "2026-06-01",
      "periode_fin": "2026-06-30",
      "date_publication": "2026-07-01T10:30:00Z",
      "nombre_lignes_traitees": 25,
      "montant_total": 950000.00,
      "statut": "PUBLIEE"
    }
  ]
}
```

### Fonctionnalités
- ✅ Mes statistiques de performance
- ✅ Évolution sur 30 derniers jours
- ✅ Publications par cycle
- ✅ Historique des 10 dernières publications

---

## 💼 4. STATS PAYEUR

### Endpoint
```http
GET /api/billing/stats/payeur/
Authorization: Bearer {token}
```

### Description
Statistiques de consommation pour le payeur d'une ou plusieurs entreprises.

### Réponse
```json
{
  "statistiques": {
    "nombre_entreprises": 2,
    "nombre_lignes": 45,
    "total_factures": 24,
    "montant_total": 12500000.00,
    "montant_paye": 10000000.00,
    "montant_en_attente": 2500000.00
  },
  "factures_par_statut": {
    "PAYEE": 20,
    "PUBLIEE": 3,
    "VALIDEE": 1
  },
  "evolution_mensuelle": [
    {
      "mois": "2026-02",
      "nombre": 2,
      "montant": 2100000.00
    },
    {
      "mois": "2026-03",
      "nombre": 2,
      "montant": 2050000.00
    }
  ],
  "lignes_a_surveiller": [
    {
      "id": "uuid",
      "msisdn": "79300739",
      "utilisateur": "Direction Générale",
      "cycle": "OP",
      "company__raison_sociale": "WACEM SA",
      "montant_facture": 850000.00
    }
  ],
  "repartition_par_entreprise": [
    {
      "id": "uuid",
      "raison_sociale": "WACEM SA",
      "compte": "A0000106",
      "montant_total": 8500000.00,
      "nombre_lignes": 30
    },
    {
      "id": "uuid",
      "raison_sociale": "CAFE INFORMATIQUE",
      "compte": "A0000009",
      "montant_total": 4000000.00,
      "nombre_lignes": 15
    }
  ]
}
```

### Fonctionnalités
- ✅ Vue d'ensemble de mes contrats
- ✅ Consommation totale et par entreprise
- ✅ Montants payés vs en attente
- ✅ Top 10 lignes à forte consommation
- ✅ Évolution sur 6 derniers mois

---

## 👤 5. STATS EMPLOYÉ

### Endpoint
```http
GET /api/billing/stats/employe/
Authorization: Bearer {token}
```

### Description
Statistiques de consommation personnelle de l'employé.

### Réponse
```json
{
  "ma_ligne": {
    "msisdn": "79300739",
    "utilisateur": "Benoit BANLEPO",
    "cycle": "OP",
    "forfait": 15000.00,
    "entreprise": "WACEM SA"
  },
  "statistiques": {
    "total_factures": 12,
    "montant_total": 850000.00,
    "moyenne_mensuelle": 141666.67
  },
  "evolution_mensuelle": [
    {
      "mois": "2026-02",
      "montant": 145000.00
    },
    {
      "mois": "2026-03",
      "montant": 138000.00
    }
  ],
  "historique_factures": [
    {
      "id": "uuid",
      "numero_facture": "A20260679300739",
      "periode_debut": "2026-06-01",
      "periode_fin": "2026-06-30",
      "montant_ttc": 142000.00,
      "statut": "PAYEE",
      "date_emission": "2026-07-01",
      "date_echeance": "2026-07-30"
    }
  ],
  "simulations": {
    "total": 5,
    "dernieres": [
      {
        "id": "uuid",
        "date_simulation": "2026-07-15T14:30:00Z",
        "montant_estime": 155000.00,
        "services_selectionnes": ["DATA_5GB", "APPELS_ILLIMITES"]
      }
    ]
  }
}
```

### Fonctionnalités
- ✅ Informations de ma ligne
- ✅ Ma consommation personnelle
- ✅ Évolution sur 6 derniers mois
- ✅ Historique de mes 12 dernières factures
- ✅ Mes simulations récentes

---

## 🧪 TESTS

### Test Admin Stats
```bash
curl -X GET http://localhost:8000/api/billing/stats/admin/ \
  -H "Authorization: Bearer {admin_token}"
```

### Test Chef Stats
```bash
curl -X GET http://localhost:8000/api/billing/stats/chef/ \
  -H "Authorization: Bearer {chef_token}"
```

### Test Agent Stats
```bash
curl -X GET http://localhost:8000/api/billing/stats/agent/ \
  -H "Authorization: Bearer {agent_token}"
```

### Test Payeur Stats
```bash
curl -X GET http://localhost:8000/api/billing/stats/payeur/ \
  -H "Authorization: Bearer {payeur_token}"
```

### Test Employé Stats
```bash
curl -X GET http://localhost:8000/api/billing/stats/employe/ \
  -H "Authorization: Bearer {employe_token}"
```

---

## 📊 INDICATEURS CALCULÉS

### Pour tous les rôles
- **Montants totaux** : Somme des factures
- **Évolution temporelle** : Groupement par mois/jour
- **Répartition par statut** : Comptage des factures

### Spécifiques Admin
- **Top entreprises** : Tri par montant facturé décroissant
- **Top lignes** : Tri par consommation décroissante
- **Performance agents** : Agrégation des publications

### Spécifiques Chef
- **Performance équipe** : Moyenne par agent
- **Suivi quotidien** : Publications sur 30 jours

### Spécifiques Payeur
- **Lignes à surveiller** : Top 10 consommation
- **Répartition entreprises** : Si plusieurs contrats

---

## 🔄 ÉVOLUTION FUTURE

### Possibilités d'amélioration
1. **Cache** : Mettre en cache les stats avec Redis
2. **Export** : Exporter les stats en PDF/Excel
3. **Alertes** : Notifications sur dépassements
4. **Prédictions** : ML pour prédire la consommation
5. **Comparaisons** : Comparer avec période précédente
6. **Drill-down** : Stats détaillées par clic

---

## 🎯 RÉSUMÉ

### ✅ Implémenté
- 5 endpoints de statistiques (1 par rôle)
- Permissions spécifiques par rôle
- Agrégations SQL optimisées
- Évolutions temporelles (quotidiennes/mensuelles)
- Top N avec tri

### 📊 Métriques disponibles
- **Admin** : Vue globale système
- **Chef** : Performance équipe
- **Agent** : Performance personnelle
- **Payeur** : Consommation contrats
- **Employé** : Consommation personnelle

### 🚀 Prêt pour
- Intégration frontend (dashboards)
- Tests avec données réelles
- Optimisation des requêtes si besoin
- Extension avec nouvelles métriques

---

**Date** : 30 Juillet 2026  
**Statut** : ✅ PHASE 5 COMPLÈTE  
**Prochaine étape** : Tester les endpoints avec les différents rôles
