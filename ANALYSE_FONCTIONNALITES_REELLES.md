# 📊 Analyse des Fonctionnalités Réelles par Acteur
## Basée sur le code implémenté

**Date :** 9 août 2026  
**Source :** Analyse du code Back + Front

---

## 🔍 Méthodologie

Analyse basée sur :
1. **Permissions backend** (`ROLE_PERMISSIONS` dans `accounts/models.py`)
2. **ViewSets Django REST** (endpoints disponibles par rôle)
3. **Pages frontend React** (interfaces accessibles)
4. **Statistiques** (`stats_views.py`)

---

## 1️⃣ SUPER_ADMIN

### Permissions définies
```python
'SUPER_ADMIN': ['*']  # Toutes les permissions
```

### Fonctionnalités réelles
- ✅ **Gestion utilisateurs** : Créer/Modifier/Supprimer tous utilisateurs (tous rôles)
- ✅ **Gestion contrats** : CRUD complet contrats
- ✅ **Gestion factures** : Publier, Annuler, Consulter tout
- ✅ **Gestion tarifs** : CRUD complet forfaits et services
- ✅ **Statistiques** : Dashboard admin complet (`stats_admin`)
- ✅ **Configuration** : Paramètres système, logs
- ✅ **Audit** : Accès à tous les audits
- ✅ **Export** : Exporter toutes les données

### Pages frontend
- `/admin/dashboard` - Dashboard administrateur
- Accès à toutes les pages

---

## 2️⃣ CHEF_FACTURATION

### Permissions définies
```python
'CHEF_FACTURATION': [
    'accounts.create_agent',          # Créer agents
    'accounts.view_all',              # Voir tous
    'accounts.edit_agents',           # Modifier agents
    'accounts.change_status_agents',  # Changer statut agents
    'accounts.reset_password_agents', # Reset password agents
    'billing.publish',                # Publier factures
    'billing.cancel',                 # Annuler factures
    'billing.view_all',               # Voir toutes factures
    'billing.export',                 # Exporter factures
    'tarifs.create',                  # Créer tarifs
    'tarifs.edit',                    # Modifier tarifs
    'tarifs.activate',                # Activer/désactiver tarifs
    'services.create',                # Créer services
    'services.edit',                  # Modifier services
    'services.activate',              # Activer/désactiver services
    'reports.view_all',               # Voir tous rapports
    'reports.export',                 # Exporter rapports
    'system.view_logs',               # Voir logs système
]
```

### Fonctionnalités réelles
- ✅ **Gestion agents** : Créer, modifier, changer statut, reset password de SES agents
- ✅ **Gestion contrats** : CRUD complet contrats (hérité d'Agent)
- ✅ **Gestion factures** : Publier + **Annuler** factures
- ✅ **Gestion tarifs** : Créer + **Modifier** + **Activer/Désactiver** forfaits
- ✅ **Gestion services** : Créer + **Modifier** + **Activer/Désactiver** services
- ✅ **Statistiques** : Dashboard chef (`stats_chef_facturation`)
- ✅ **Audit** : Consulter audits contrats
- ✅ **Export** : Exporter toutes données
- ✅ **Logs** : Consulter logs système

### Pages frontend
- `/chef/dashboard` - Dashboard chef
- Accès aux pages Agent + fonctions supervision

---

## 3️⃣ AGENT_FACTURATION

### Permissions définies
```python
'AGENT_FACTURATION': [
    'billing.publish',     # Publier factures
    'billing.view_all',    # Voir toutes factures
    'tarifs.create',       # Créer tarifs
    'services.create',     # Créer services
    'reports.view_all',    # Voir tous rapports
]
```

### Fonctionnalités réelles
- ✅ **Gestion contrats** : Créer, modifier contrats entreprises
- ✅ **Gestion lignes** : Créer, modifier, affecter employés aux lignes
- ✅ **Gestion commerciaux** : CRUD commerciaux
- ✅ **Publication factures** : Uploader PDF, parser, publier factures
- ✅ **Consultation factures** : Voir toutes les factures
- ✅ **Gestion tarifs** : Créer forfaits (pas modifier)
- ✅ **Gestion services** : Créer services (pas modifier)
- ✅ **Statistiques** : Dashboard agent (`stats_agent_facturation`)
- ✅ **Export** : Export contrats/factures

### Pages frontend
- `/agent/dashboard` - Dashboard agent
- `/agent/contrats` - Gestion contrats
- `/agent/publier` - Publication factures
- `/agent/commerciaux` - Gestion commerciaux

### Endpoints backend utilisés
- `CompanyViewSet` : CRUD contrats
- `LineViewSet` : CRUD lignes
- `InvoiceViewSet` : Publication et consultation factures
- `PackageViewSet` : Créer forfaits
- `ServiceViewSet` : Créer services
- `CommercialViewSet` : CRUD commerciaux

---

## 4️⃣ COMMERCIAL

### Permissions définies
```python
'COMMERCIAL': [
    'billing.view_own',  # Voir ses propres données
]
```

### Fonctionnalités réelles
**⚠️ ATTENTION : Rôle NON implémenté dans le front**

Backend préparé mais pas d'interface :
- ❓ **Consultation contrats** : Théoriquement ses contrats prospectés
- ❓ **Consultation factures** : Factures de ses contrats
- ❓ **Statistiques** : Pas de stats_commercial implémenté

### Pages frontend
- ❌ Aucune page dédiée
- ❌ Pas de dashboard

### Statut
🔴 **Rôle prévu mais non implémenté dans l'application actuelle**

---

## 5️⃣ PAYEUR

### Permissions définies
```python
'PAYEUR': [
    'billing.view_own',     # Voir ses factures
    'billing.export_own',   # Exporter ses factures
]
```

### Fonctionnalités réelles
- ✅ **Consultation contrats** : Voir SES contrats d'entreprise
- ✅ **Consultation factures** : Voir TOUTES les factures de SES contrats
  - Factures GLOBALES (GLO)
  - Factures SOMMAIRES (SOM) de toutes les lignes
- ✅ **Exploration** : Navigation Type → Année → Mois → Factures
- ✅ **Téléchargement** : PDF des factures
- ✅ **Statistiques** : Dashboard payeur (`stats_payeur`)
  - Nombre contrats
  - Nombre lignes
  - Montant total factures
  - Répartition par mois
- ✅ **Export** : Exporter ses factures
- ✅ **Simulation** : Simuler coût services

### Pages frontend
- `/dashboard` - Dashboard payeur (`DashboardPayeur.jsx`)
- `/factures` - Exploration factures avec types (GLO/SOM)
- `/profil` - Gestion profil

### Filtrages backend
```python
def get_queryset(self):
    if user.role == 'PAYEUR':
        return Invoice.objects.filter(company__payeur=user)
```

---

## 6️⃣ EMPLOYE

### Permissions définies
```python
'EMPLOYE': [
    'billing.view_own',  # Voir sa facture
]
```

### Fonctionnalités réelles
- ✅ **Consultation facture** : Voir UNIQUEMENT sa facture individuelle (SOM)
  - Facture de SA ligne téléphonique
- ✅ **Exploration** : Navigation Année → Mois → SA facture
- ✅ **Téléchargement** : PDF de sa facture
- ✅ **Statistiques** : Dashboard employé (`stats_employe`)
  - Montant de sa facture
  - Historique mensuel
- ✅ **Simulation** : Simuler coût services
- ✅ **Profil** : Modifier mot de passe

### Pages frontend
- `/dashboard` - Dashboard employé (`DashboardEmploye.jsx`)
- `/factures` - Exploration factures (sans navigation par type)
- `/profil` - Gestion profil

### Filtrages backend
```python
def get_queryset(self):
    if user.role == 'EMPLOYE':
        return Invoice.objects.filter(line__employe=user)
```

### Condition d'accès
⚠️ L'employé DOIT être affecté à une ligne (`line.employe = user`)

---

## 📊 Comparatif Réel des Fonctionnalités

| Fonctionnalité | Admin | Chef | Agent | Commercial | Payeur | Employé |
|----------------|-------|------|-------|------------|--------|---------|
| **GESTION UTILISATEURS** |
| Créer agent | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Modifier agent | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Créer tous rôles | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Reset password | ✅ | ✅ (agents) | ❌ | ❌ | ❌ | ❌ |
| **GESTION CONTRATS** |
| Créer contrat | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Modifier contrat | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Consulter tous | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Consulter siens | - | - | - | 🔴 | ✅ | ❌ |
| **GESTION LIGNES** |
| Créer ligne | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Modifier ligne | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Affecter employé | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **GESTION COMMERCIAUX** |
| CRUD commerciaux | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **FACTURATION** |
| Publier PDF | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Annuler facture | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Voir toutes | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Voir siennes (contrats) | - | - | - | 🔴 | ✅ | ❌ |
| Voir sa facture (ligne) | - | - | - | - | - | ✅ |
| Télécharger PDF | ✅ | ✅ | ✅ | 🔴 | ✅ | ✅ |
| **TARIFS & SERVICES** |
| Créer forfait | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Modifier forfait | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Activer/Désactiver | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Créer service | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Modifier service | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **STATISTIQUES** |
| Dashboard Admin | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Dashboard Chef | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Dashboard Agent | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Dashboard Commercial | - | - | - | 🔴 | - | - |
| Dashboard Payeur | - | - | - | - | ✅ | ❌ |
| Dashboard Employé | - | - | - | - | - | ✅ |
| **EXPORT** |
| Exporter tout | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Exporter sien | - | - | - | 🔴 | ✅ | ❌ |
| **SIMULATION** |
| Simuler services | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| **AUDIT & LOGS** |
| Consulter audit | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Consulter logs | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

**Légende :**
- ✅ Implémenté et fonctionnel
- ❌ Non accessible
- 🔴 Prévu mais NON implémenté
- `-` Non applicable

---

## 🎯 Différences Clés Identifiées

### 1. **Portée des consultations**

| Rôle | Portée | Détails |
|------|--------|---------|
| **Admin/Chef/Agent** | Globale | Toutes les factures, tous les contrats |
| **Commercial** | 🔴 Ses contrats | Contrats où `commercial_id = user.commercial.id` (non implémenté) |
| **Payeur** | Ses entreprises | Contrats où `payeur_id = user.id` (TOUTES factures GLO + SOM) |
| **Employé** | Sa ligne | Facture où `line.employe_id = user.id` (UNE facture SOM) |

### 2. **Navigation factures**

**Payeur** :
```
Type (GLO/SOM) → Année → Mois → Factures
```

**Employé** :
```
Année → Mois → Sa facture
```

### 3. **Gestion vs Consultation**

**Gestion (Admin/Chef/Agent)** :
- CRUD contrats, lignes, factures
- Publication factures
- Gestion tarifs

**Consultation (Payeur/Employé)** :
- Lecture seule
- Téléchargement PDF
- Simulation (optionnel)

---

## 🔴 Rôle COMMERCIAL - Non implémenté

**Prévu mais manquant :**
- ❌ Aucune page frontend
- ❌ Pas de dashboard
- ❌ Pas de stats_commercial
- ❌ Filtrage par commercial_id pas utilisé
- ❌ Pas de lien avec table `Commercial`

**Pour implémenter :**
1. Créer `DashboardCommercial.jsx`
2. Créer `stats_commercial` dans `stats_views.py`
3. Ajouter filtrage dans `CompanyViewSet` et `InvoiceViewSet`
4. Lier `User.commercial` → `Commercial`

---

## ✅ Conclusion

### Hiérarchies réelles :

**1. Hiérarchie Administration/Facturation**
```
Super Admin (wildcard *)
    ↑
Chef Facturation (15 permissions)
    ↑
Agent Facturation (5 permissions)
```

**2. Hiérarchie Consultation** 
```
Payeur (2 permissions, portée : entreprise)
    ↑
Employé (1 permission, portée : ligne)
```

**3. Acteur indépendant**
```
Commercial (1 permission, 🔴 non implémenté)
```

---

**FIN DE L'ANALYSE**
