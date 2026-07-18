# 🚀 Démarrage Rapide - Agent Facturation

## En 3 étapes seulement

### 1️⃣ Lancer le serveur
```bash
cd Front
npm run dev
```
**Attendez ce message** :
```
➜  Local:   http://localhost:3001/
```

### 2️⃣ Ouvrir le navigateur
URL : **http://localhost:3001**

### 3️⃣ Se connecter
```
Identifiant : agent@moov.tg
Mot de passe : agent123
```

**C'est tout !** Vous serez automatiquement redirigé vers le dashboard agent.

---

## 📍 Accès Direct

Si le serveur tourne déjà :
- Dashboard Agent : http://localhost:3001/agent/dashboard
- Gestion Forfaits : http://localhost:3001/agent/forfaits
- Gestion Services : http://localhost:3001/agent/services
- Publication PDF : http://localhost:3001/agent/publication

---

## ✅ Vérification Rapide

### Le dashboard doit afficher :
- ✅ En-tête "Dashboard Agent Facturation"
- ✅ Card hero avec "X factures" et badge statut (vert/orange)
- ✅ 4 cards statistiques en grille (Alerte Retard, Échéance Proche, Contacts Divers, Réclamations Urgentes)
- ✅ Coins arrondis, gradients subtils, effet hover sur les cards

### Si vous voyez du texte noir brut sans style :
```bash
# Arrêter le serveur (Ctrl+C)
# Vider le cache
rm -rf node_modules/.vite
# Relancer
npm run dev
# Dans le navigateur : Ctrl+Maj+R
```

---

## 🆘 Problème ?

**Serveur ne démarre pas** → `npm install` puis `npm run dev`

**Port 3001 occupé** → Le serveur essaiera 3002, vérifier le message terminal

**Page blanche** → F12 pour ouvrir Console, lire l'erreur

**Styles cassés** → Lire [VERIFICATION.md](./VERIFICATION.md)

---

## 📚 Documentation Complète

Pour plus de détails, lire :
- **[README_AGENT_FACTURATION.md](./README_AGENT_FACTURATION.md)** - Guide complet
- **[GUIDE_VISUEL.md](./GUIDE_VISUEL.md)** - Design system
- **[VERIFICATION.md](./VERIFICATION.md)** - Checklist technique

---

**🎯 Objectif** : Vous devez voir un dashboard moderne avec des cards stylées et des animations douces. Si ce n'est pas le cas, Tailwind ne charge pas correctement (voir VERIFICATION.md).
