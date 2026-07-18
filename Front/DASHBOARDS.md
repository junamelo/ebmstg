# Dashboards du Portail e-Billings Moov Africa

## Vue d'ensemble

Le portail dispose de **4 dashboards différents** selon le rôle de l'utilisateur connecté :

1. **Dashboard Employé** — pour les utilisateurs avec une ligne individuelle
2. **Dashboard Payeur** — pour les responsables d'entreprise gérant une flotte
3. **Dashboard Agent Facturation** — pour les agents Moov gérant les publications
4. **Dashboard Super Admin** — pour l'administration globale de la plateforme

---

## 👤 Dashboard Employé

**Fichier :** `src/pages/dashboard/DashboardEmploye.jsx`

### Sections affichées

#### Ma ligne
- Numéro MSISDN
- Forfait souscrit
- Statut (Actif / Suspendu)
- Services actifs (badges : No Limit, BlackBerry, Incognito...)

#### Ma dernière facture
- Solde du mois en cours
- Jours restants avant fin de cycle
- Date de clôture

#### Consommation du mois en cours
- 3 jauges circulaires :
  - Data (Go consommés / Go inclus)
  - Appels (minutes consommées / minutes incluses)
  - SMS (nombre envoyés / inclus)
- Alerte si consommation > 90%

#### Historique de mes simulations
- Date de simulation
- Montant estimé
- Taux de consommation
- Bouton "Voir détails"

#### Accès rapides
- **Voir ma facture** → `/factures`
- **Simuler ma facturation** → `/simulation`

---

## 👔 Dashboard Payeur

**Fichier :** `src/pages/dashboard/DashboardPayeur.jsx`

### Sections affichées

#### Résumé du contrat
- Numéro de contrat
- Nombre de lignes actives
- Catégorie client (PE, GE, etc.)

#### Facture globale du mois en cours
- Montant total TTC (grand format avec gradient bleu)
- Statut (Payée / En attente)
- Boutons : Aperçu, Télécharger

#### Répartition par ligne
- Tableau des 5 premières lignes avec :
  - MSISDN
  - Utilisateur
  - Forfait
  - Montant TTC
  - Statut (Actif / Suspendu)

#### Lignes à surveiller
- S'affiche uniquement s'il y a des lignes suspendues ou en retard
- Alerte visuelle avec badge danger
- Bouton "Voir détails" pour chaque ligne

#### Accès rapides
- **Factures sommaires** → `/factures`
- **Simuler** → `/simulation`

---

## 🔧 Dashboard Agent Facturation

**Fichier :** `src/pages/dashboard/DashboardAgentFacturation.jsx`

### Sections affichées

#### Statut de la publication
- Badge statut (Traitée / En cours / Erreur)
- Nombre de factures générées
- Date de la dernière publication
- Alerte si erreur détectée

#### Alertes et anomalies
- 3 cartes avec compteurs :
  - Factures non publiées
  - Erreurs de découpage PDF
  - Lignes sans forfait
- Couleur dynamique (rouge si > 0, bleu sinon)

#### Services actifs et tarifs
- Tableau avec :
  - Nom du service (No Limit, BlackBerry...)
  - Tarif unitaire (FCFA)
  - Nombre de lignes actives
  - Statut (Actif)

#### Historique des publications
- Date
- Période (ex: Juin 2026)
- Nombre de factures générées
- Statut (badge)
- Bouton "Voir le rapport"

#### Action rapide
- **Nouvelle publication** → `/admin/publication`

---

## 🛡️ Dashboard Super Admin

**Fichier :** `src/pages/admin/AdminDashboard.jsx`

### Sections affichées

#### Statistiques plateforme
- 4 KPI cards :
  - **Contrats actifs** (total entreprises)
  - **Lignes actives** (total lignes téléphoniques)
  - **Utilisateurs actifs** (connectés récemment)
  - **Taux d'adoption** (% utilisateurs connectés / total)

#### Activité récente
- Tableau des dernières connexions :
  - Nom utilisateur
  - Rôle (badge coloré)
  - Date/heure
  - Adresse IP

#### Comptes utilisateurs
- Répartition par rôle (grille 4 colonnes) :
  - Payeurs
  - Employés
  - Agents Facturation
  - Super Admins
- Valeurs affichées en grand format avec couleurs différentes

#### Accès rapide
- **Créer un compte** → `/admin/comptes?action=nouveau`
- **Rechercher un contrat** → `/admin/comptes?recherche=contrat`
- **Rechercher une ligne** → `/admin/comptes?recherche=ligne`

---

## 🔐 Authentification et routing

### Comptes de test (mockés)

| Rôle | Login | Mot de passe |
|------|-------|--------------|
| Super Admin | `admin@moov.tg` | `admin123` |
| Agent Facturation | `agent@moov.tg` | `agent123` |
| Payeur | `CT-001234` | `payeur123` |
| Employé | `90123456` | `5678` |

### Logique de redirection

```javascript
// Connexion réussie → redirection automatique
- SUPER_ADMIN → /admin/dashboard
- AGENT_FACTURATION → /dashboard (affiche DashboardAgentFacturation)
- PAYEUR → /dashboard (affiche DashboardPayeur)
- EMPLOYE → /dashboard (affiche DashboardEmploye)
```

### Protection des routes

- `/` `/dashboard` `/factures` `/simulation` → accessible à tous les utilisateurs authentifiés
- `/admin/*` → réservé aux SUPER_ADMIN uniquement

---

## 🎨 Composants réutilisables

### Dashboard commun
- **KpiCard** — carte avec valeur + sous-titre + bordure colorée
- **SoldeCard** — affichage du solde avec alerte urgence
- **JaugeCirculaire** — cercle de progression SVG avec pourcentage

### Agent Facturation
- **StatutPublicationCard** — statut + badge + détails
- **AlerteCard** — compteur + texte + couleur dynamique

### Super Admin
- **Tendance** — flèche ▲/▼ avec pourcentage d'évolution

---

## 📊 Sources de données

Actuellement en mode **mock** (fichier `mockApi.js`).

Lorsque le backend Django sera prêt :
1. Changer `USE_MOCK = false` dans `adminService.js`
2. Les appels API réels prendront le relais automatiquement

### Endpoints attendus (backend)
- `GET /admin/statistiques` → stats Super Admin
- `GET /agent-facturation/statistiques` → stats Agent Facturation
- `GET /payeur/statistiques` → stats Payeur
- `GET /employe/statistiques` → stats Employé

---

## 🚀 Prochaines étapes

- [ ] Connecter au backend Django réel
- [ ] Ajouter filtres par date sur les dashboards Payeur/Agent
- [ ] Graphiques d'évolution (Chart.js ou Recharts)
- [ ] Export Excel/PDF des tableaux
- [ ] Notifications temps réel (WebSockets)
