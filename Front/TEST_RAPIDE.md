# ⚡ Test Rapide - Dashboard Agent

## 🔥 Correction Appliquée
**Problème** : Directive `"use client"` invalide (propre à Next.js) dans React/Vite  
**Solution** : ✅ Supprimée de tous les fichiers

---

## ✅ Test en 4 Étapes

### 1️⃣ Redémarrer le serveur
```bash
# Dans le terminal où tourne le serveur
# Appuyer sur Ctrl+C pour arrêter
# Puis relancer :
npm run dev
```

### 2️⃣ Ouvrir la page
URL : **http://localhost:3000/agent/dashboard**

### 3️⃣ Vérifier l'affichage
**✅ Si ça marche, vous voyez** :
- En-tête "Facturation"
- Grande card avec gradient (vert ou orange)
- Badge "Traitée" avec icône ✓
- 3 petites cards "Alertes" avec chiffres
- Tables avec headers bleus
- Coins arrondis partout
- Effet hover sur les cards

**❌ Si ça ne marche pas, vous voyez** :
- Texte noir brut sans couleur
- Pas de cards arrondies
- Layout cassé

### 4️⃣ Vérifier la console
- Appuyer sur **F12**
- Onglet **Console**
- Regarder s'il y a des erreurs rouges

---

## 🐛 Si Erreur : Copier et Partager

**Dans la console (F12 → Console)** :
- Si texte rouge : copier le message complet
- Noter le numéro de ligne

**Erreurs courantes** :

### A. "Cannot read properties of null"
```
TypeError: Cannot read properties of null (reading 'statutPublication')
```
→ Les données ne chargent pas. Vérifier que `USE_MOCK = true` dans `adminService.js`

### B. "motion is not defined"
```
ReferenceError: motion is not defined
```
→ Installer Motion :
```bash
npm install motion
npm run dev
```

### C. Page blanche avec erreur "useAuth"
```
Error: useAuth must be used within AuthProvider
```
→ Problème d'authentification. Se déconnecter et se reconnecter.

---

## 🎯 Test Complet

Si la page fonctionne :

1. ✅ **Hover sur une card** → Doit grossir légèrement
2. ✅ **Cliquer sur "Gérer les forfaits"** → Redirige vers `/agent/forfaits`
3. ✅ **Cliquer sur "Nouvelle publication"** → Redirige vers `/agent/publication`
4. ✅ **Rétrécir la fenêtre** → Layout s'adapte (3 cols → 2 cols → 1 col)

---

## 📸 Capture d'Écran Attendue

```
╔═══════════════════════════════════════════╗
║ Facturation                               ║
║ Gestion des publications et opérations... ║
╠═══════════════════════════════════════════╣
║                                           ║
║  📊 Publication du mois                   ║
║  ┌─────────────────────────────────────┐ ║
║  │ 1,247 factures      [✓ Traitée]    │ ║
║  │ Publiée le 05/07/2026               │ ║
║  └─────────────────────────────────────┘ ║
║                                           ║
║  Alertes                                  ║
║  ┌────────┬────────┬────────────────┐    ║
║  │   0    │   2    │       5        │    ║
║  │ Non    │ Erreurs│ Lignes sans    │    ║
║  │ publiée│ PDF    │ forfait        │    ║
║  └────────┴────────┴────────────────┘    ║
║                                           ║
║  Services et tarifs actifs                ║
║  ┌─────────────────────────────────────┐ ║
║  │ Service    │ Tarif │ Lignes │ ●Actif│ ║
║  │ No Limit   │ 5000  │  342   │  ●   │ ║
║  │ BlackBerry │ 3500  │  128   │  ●   │ ║
║  └─────────────────────────────────────┘ ║
╚═══════════════════════════════════════════╝
```

---

## 🆘 Si Ça Ne Marche Toujours Pas

### Essayer le hard reset :
```bash
# Arrêter le serveur (Ctrl+C)
cd Front

# Supprimer le cache
rm -rf node_modules/.vite
rm -rf dist

# Rebuilder
npm run build

# Relancer
npm run dev
```

### Dans le navigateur :
- **Ctrl+Maj+R** (rechargement forcé)
- Ou vider le cache : F12 → Network → Décocher "Disable cache"

### Vérifier l'authentification :
```javascript
// Dans la console navigateur (F12 → Console)
localStorage.getItem('user')
// Doit afficher : {"id":"...", "role":"AGENT_FACTURATION", ...}
```

Si `null` ou rôle différent :
1. Aller sur http://localhost:3000/login
2. Se connecter : `agent@moov.tg` / `agent123`
3. Retourner sur `/agent/dashboard`

---

## ✅ Confirmation de Succès

La page fonctionne si vous voyez :
- ✅ Gradient vert sur la hero card
- ✅ Badge "Traitée" avec fond vert clair
- ✅ 3 cards alertes avec chiffres en gros
- ✅ Table avec header bleu foncé
- ✅ Effet hover qui agrandit les cards
- ✅ Pas d'erreurs dans la console

---

**Prochaine étape** : Si ça marche, tester les autres pages :
- `/agent/forfaits` - Gestion forfaits
- `/agent/services` - Gestion services
- `/agent/publication` - Publication PDF
