# 🔍 Diagnostic - Dashboard Agent

## ✅ Corrections Appliquées

### Problème 1 : Directive `"use client"` invalide
**Symptôme** : La directive `"use client"` est propre à Next.js (React Server Components). Dans React/Vite, elle cause des erreurs.

**Fichiers corrigés** :
- ✅ `AgentDashboard.jsx`
- ✅ `GestionForfaits.jsx`
- ✅ `GestionServices.jsx`
- ✅ `AdminDashboard.jsx`

**Action** : Supprimé la ligne `"use client"` de tous les fichiers.

### Résultat
- ✅ Build réussi : `npm run build` → OK
- ✅ Pas d'erreurs de syntaxe
- ✅ Toutes les dépendances présentes

---

## 🧪 Tests à Effectuer

### 1. Arrêter et redémarrer le serveur
```bash
# Arrêter le serveur actuel (Ctrl+C dans le terminal)
cd Front
npm run dev
```

**Attendu** : Le serveur démarre sans erreurs

### 2. Vider le cache navigateur
- Ouvrir http://localhost:3000/agent/dashboard
- Appuyer sur **F12** (ouvrir DevTools)
- Appuyer sur **Ctrl+Maj+R** (rechargement forcé)

**Attendu** : La page se charge avec le design moderne

### 3. Vérifier la console navigateur
- F12 → Onglet **Console**
- Regarder s'il y a des erreurs en rouge

**Erreurs possibles** :

#### A. Erreur : "Cannot read properties of null"
```
TypeError: Cannot read properties of null (reading 'statutPublication')
```
**Cause** : `stats` est null lors du premier rendu
**Solution** : Déjà implémentée (vérification `if (chargement)` ligne 89-98)

#### B. Erreur : "motion is not defined"
```
ReferenceError: motion is not defined
```
**Cause** : Package Motion non importé correctement
**Solution** :
```bash
npm install motion
npm run dev
```

#### C. Erreur : Classe Tailwind non appliquée
**Symptôme** : La page affiche du texte brut sans style
**Cause** : Tailwind ne compile pas
**Solution** :
```bash
rm -rf node_modules/.vite
npm run dev
```

### 4. Vérifier les données chargées
- Ouvrir DevTools → Onglet **Network**
- Rafraîchir la page
- Regarder si `getStatsAgentFacturation` est appelé

**Attendu** : Après 400ms, les données apparaissent

---

## 🎯 Symptômes Possibles et Solutions

### Symptôme 1 : Page blanche
**Causes possibles** :
1. Erreur JavaScript non catchée
2. Route non trouvée
3. Contexte AuthContext cassé

**Diagnostic** :
```bash
# Dans la console navigateur (F12)
# Regarder l'onglet Console pour erreurs
```

**Solution** :
- Si erreur `useAuth is not defined` → Vérifier AuthContext
- Si erreur `Cannot read properties of undefined` → Vérifier les props
- Si erreur `Module not found` → Vérifier les imports

### Symptôme 2 : Spinner infini (chargement sans fin)
**Cause** : `getStatsAgentFacturation()` ne résout jamais la promesse

**Diagnostic** :
```javascript
// Dans la console navigateur
import { getStatsAgentFacturation } from './services/adminService'
getStatsAgentFacturation().then(console.log).catch(console.error)
```

**Solution** :
- Vérifier que `USE_MOCK = true` dans `adminService.js`
- Vérifier que `mockGetStatsAgentFacturation` existe dans `mockApi.js`

### Symptôme 3 : Styles non appliqués
**Cause** : Tailwind ne compile pas les classes

**Diagnostic** :
```bash
# Vérifier que le CSS contient les classes Tailwind
cat dist/assets/index-*.css | grep "rounded-2xl"
```

**Solution** :
```bash
# Vider le cache Vite
rm -rf node_modules/.vite

# Vérifier tailwind.config.js existe
ls tailwind.config.js

# Vérifier global.css contient @tailwind
head -n 10 src/styles/global.css

# Relancer
npm run dev
```

### Symptôme 4 : Redirection vers /login
**Cause** : Authentification échoue

**Diagnostic** :
```javascript
// Dans la console navigateur
localStorage.getItem('user')
// Doit retourner un objet JSON avec role: 'AGENT_FACTURATION'
```

**Solution** :
1. Se déconnecter : http://localhost:3000/login
2. Se reconnecter avec `agent@moov.tg` / `agent123`
3. Vérifier que le rôle est correct dans localStorage

### Symptôme 5 : Erreur 404 sur la route
**Cause** : Route `/agent/dashboard` non définie

**Diagnostic** :
```bash
# Vérifier App.jsx contient la route
grep -A 5 "path=\"/agent\"" src/App.jsx
```

**Solution** :
- Déjà implémentée dans App.jsx lignes 50-63

---

## 📸 Ce que vous devriez voir

### Dashboard Agent (normal)
```
┌─────────────────────────────────────┐
│ Facturation                         │
│ Gestion des publications...         │
├─────────────────────────────────────┤
│ [HERO CARD - Gradient vert/orange] │
│   1,247 factures      [✓ Traitée]  │
│   Publiée le 05/07/2026             │
└─────────────────────────────────────┘
┌────────────────────────────────────┐
│ Alertes                            │
├────────┬────────┬──────────────────┤
│   0    │   2    │       5          │
│ Non    │ Erreurs│ Lignes sans      │
│ publiée│ PDF    │ forfait          │
└────────┴────────┴──────────────────┘
[...]
```

### Dashboard Agent (si Tailwind cassé)
```
Facturation
Gestion des publications et opérations de facturation

Publication du mois
1247 factures
✓
Traitée
Publiée le 05/07/2026

Alertes
Factures non publiées
0
[...]
```
→ Texte brut, pas de style, pas de cards arrondies

---

## 🚀 Actions Recommandées (dans l'ordre)

### 1. Redémarrer le serveur
```bash
# Ctrl+C dans le terminal
npm run dev
```

### 2. Ouvrir la page avec DevTools ouvert
```bash
# URL : http://localhost:3000/agent/dashboard
# F12 avant de charger la page
# Onglet Console ouvert
```

### 3. Copier l'erreur exacte
Si erreur rouge dans la Console :
- Copier le message complet
- Copier la stack trace (lignes en gris sous l'erreur)

### 4. Vérifier l'onglet Network
- DevTools → Onglet Network
- Rafraîchir la page
- Regarder si des fichiers sont en rouge (404 ou 500)

---

## 📞 Prochaines Étapes

**Si le problème persiste** :
1. Copier le message d'erreur exact de la console
2. Faire une capture d'écran de la page
3. Partager ces informations pour diagnostic plus précis

**Si la page fonctionne maintenant** :
- ✅ Le problème était la directive `"use client"`
- ✅ Les pages devraient s'afficher correctement
- ✅ Vous pouvez naviguer entre les pages agent

---

## 🔧 Commandes Utiles

```bash
# Vérifier que Tailwind est installé
npm list tailwindcss

# Vérifier que Motion est installé
npm list motion

# Voir les logs détaillés du serveur
npm run dev -- --debug

# Vider tous les caches
rm -rf node_modules/.vite
rm -rf dist
npm run build
npm run dev

# Vérifier les routes disponibles
grep -r "path=" src/App.jsx
```

---

**Status** : ✅ Corrections appliquées  
**Build** : ✅ Réussi  
**Prochaine étape** : Redémarrer le serveur et tester dans le navigateur
