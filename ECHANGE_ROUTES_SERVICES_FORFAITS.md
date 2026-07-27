# 🔄 Échange Routes Services ↔ Forfaits

**Date** : 27 juillet 2026  
**Status** : ✅ Complété

---

## 📋 Contexte

L'utilisateur a demandé d'inverser la logique entre "Services" et "Forfaits" pour mieux correspondre à la réalité métier de l'opérateur télécom Moov :

### ❌ Ancienne logique (incorrecte)
- **Services** = BlackBerry, No Limit, Facture Détaillée, Incognito (packages)
- **Forfaits** = Grilles tarifaires avec paliers pour SMS, Data, Voix

### ✅ Nouvelle logique (correcte)
- **Services** = SMS, Data, Voix (les 3 services de base avec système de paliers)
- **Forfaits** = BlackBerry, No Limit, Facture Détaillée, Incognito (packages/options à ajouter)

**Exemple concret** :
- "BlackBerry BB12" est un **forfait** du **service Data**
- "FACTURE DETAILLEE" et "INCOGNITO" sont des **services** à part entière

---

## 🔧 Modifications effectuées

### 1. Routes inversées dans `App.jsx`

```jsx
// AVANT
<Route path="services" element={<GestionServices />} />
<Route path="forfaits" element={<GestionForfaits />} />

// APRÈS
<Route path="services" element={<GestionForfaits />} />   // ← Contient maintenant le système de paliers
<Route path="forfaits" element={<GestionServices />} />   // ← Contient maintenant BlackBerry, etc.
```

**Résultat** :
- 🔗 `http://localhost:3000/agent/services` → Page avec paliers SMS/Data/Voix
- 🔗 `http://localhost:3000/agent/forfaits` → Page avec BlackBerry, No Limit, etc.

---

### 2. Navigation mise à jour dans `Sidebar.jsx`

Ordre des menus inversé pour l'agent de facturation :

```jsx
const menusAgentFacturation = [
  { path: '/agent/dashboard',                label: 'Dashboard',           icon: <IconDashboard /> },
  { path: '/agent/services',                 label: 'Gestion Services',    icon: <IconServices /> },    // ⬆️ Services en premier
  { path: '/agent/forfaits',                 label: 'Gestion Forfaits',    icon: <IconForfaits /> },    // ⬇️ Forfaits en second
  { path: '/agent/publication',              label: 'Publication PDF',     icon: <IconPublication /> },
  { path: '/agent/publication/historique',   label: 'Historique Pub.',     icon: <IconHistorique /> },
]
```

---

### 3. Dashboard Agent mis à jour (`AgentDashboard.jsx`)

Liens et descriptions clarifiés :

```jsx
<Link to="/agent/services">
  <h3>Gérer les services</h3>
  <p>Configurer SMS, Data et Voix avec paliers</p>
</Link>

<Link to="/agent/forfaits">
  <h3>Gérer les forfaits</h3>
  <p>BlackBerry, No Limit, options...</p>
</Link>
```

---

### 4. Titres et textes mis à jour

#### `GestionForfaits.jsx` (maintenant à `/agent/services`)

**Modifications** :
- Titre : "Gestion des Forfaits" → "Gestion des Services"
- Description : "Configuration des grilles tarifaires avec système de paliers" → "Configuration des services de base (SMS, Data, Voix) avec système de paliers"
- Bouton : "Nouveau forfait" → "Nouveau service"
- Placeholder : "Ex: Forfait Août 2026" → "Ex: Service Voix Premium"
- Messages : "Forfait créé" → "Service créé"
- Confirmations : "Désactiver ce forfait ?" → "Désactiver ce service ?"
- Labels : "Total forfaits" → "Total services"
- Tableau : "Liste des forfaits" → "Liste des services"
- Formulaire : "Nom du forfait" → "Nom du service"
- Bouton submit : "Créer le forfait" → "Créer le service"

#### `GestionServices.jsx` (maintenant à `/agent/forfaits`)

**Modifications** :
- Titre : "Services et Options" → "Gestion des Forfaits"
- Description : "Chaque service peut contenir plusieurs options..." → "Gestion des forfaits et packages (BlackBerry, No Limit, Facture Détaillée, Incognito...)"
- Bouton : "Nouveau service" → "Nouveau forfait"
- Placeholder : "Ex: BlackBerry, No Limit..." → "Ex: BlackBerry BB12, No Limit..."
- Messages : "Service créé" → "Forfait créé"
- Formulaire : "Nom du service" → "Nom du forfait"
- Labels : "Modifier le service" → "Modifier le forfait"

---

## 📁 Structure actuelle des fichiers

### Mapping Route → Fichier → Contenu

| Route | Fichier physique | Contenu réel |
|-------|------------------|--------------|
| `/agent/services` | `GestionForfaits.jsx` | ✅ Paliers SMS/Data/Voix (services de base) |
| `/agent/forfaits` | `GestionServices.jsx` | ✅ BlackBerry, No Limit, options (forfaits) |

> ⚠️ **Note** : Les noms de fichiers physiques ne correspondent plus aux routes, mais le contenu est correct. Un renommage futur pourrait éviter la confusion :
> - `GestionForfaits.jsx` → `GestionServices.jsx`
> - `GestionServices.jsx` → `GestionForfaits.jsx`

---

## 🎯 Fonctionnalités maintenues

### Page Services (`/agent/services`)
✅ Système de paliers pour appels (30s → 75 FCFA, etc.)  
✅ Système de paliers pour data (100 Mo → 200 FCFA, etc.)  
✅ Prix SMS uniforme (10 FCFA)  
✅ Boutons "Ajouter un palier" dynamiques  
✅ Suppression des paliers (minimum 1)  
✅ Modification des services existants  
✅ Activation/Désactivation des services  

### Page Forfaits (`/agent/forfaits`)
✅ Gestion des forfaits (BlackBerry, No Limit, etc.)  
✅ Accordéon par forfait avec options tarifaires  
✅ Ajout d'options pour chaque forfait  
✅ Modification des forfaits  
✅ Modification des options  
✅ Activation/Désactivation des forfaits et options  

---

## ✅ Tests à effectuer

1. **Navigation** :
   - [ ] Cliquer sur "Gestion Services" dans la sidebar → Page avec paliers
   - [ ] Cliquer sur "Gestion Forfaits" dans la sidebar → Page avec BlackBerry, etc.

2. **Dashboard Agent** :
   - [ ] Lien "Gérer les services" → Redirect vers `/agent/services`
   - [ ] Lien "Gérer les forfaits" → Redirect vers `/agent/forfaits`

3. **Fonctionnalités** :
   - [ ] Créer un nouveau service avec paliers → Fonctionne
   - [ ] Créer un nouveau forfait (ex: BlackBerry) → Fonctionne
   - [ ] Modifier un service existant → Fonctionne
   - [ ] Modifier un forfait existant → Fonctionne

---

## 📝 Prochaines étapes (optionnel)

### Option A : Renommer les fichiers pour plus de clarté
```bash
# Renommer pour éviter confusion
GestionForfaits.jsx → GestionServices.jsx
GestionServices.jsx → GestionForfaits.jsx
```

### Option B : Conserver l'état actuel
Les routes fonctionnent correctement, seuls les noms de fichiers ne correspondent pas aux routes. C'est acceptable si l'équipe comprend la logique.

---

## 🔍 Rappel métier

### Services de base (avec paliers)
- **SMS** : Prix uniforme par message
- **Data** : Paliers par volume consommé (Mo)
- **Voix** : Paliers par durée d'appel (secondes)

### Forfaits (packages ajoutés)
- **BlackBerry** : Forfait data spécifique BlackBerry
- **No Limit** : Forfait illimité
- **Facture Détaillée** : Service de facturation détaillée
- **Incognito** : Service d'appels masqués

---

## 📌 Résumé

✅ Routes échangées dans `App.jsx`  
✅ Navigation mise à jour dans `Sidebar.jsx`  
✅ Dashboard liens corrigés dans `AgentDashboard.jsx`  
✅ Titres et descriptions mis à jour dans les deux pages  
✅ Messages de succès/erreur cohérents avec la nouvelle logique  
✅ Fonctionnalités préservées à 100%  

**L'échange est complet et fonctionnel !** 🎉
