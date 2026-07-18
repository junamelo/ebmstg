# Accès au Dashboard Agent Facturation

## ✅ Configuration Terminée

Tailwind CSS est maintenant installé et configuré. Les pages modifiées devraient s'afficher correctement.

## 🔑 Connexion Agent Facturation

### 1. Ouvrir l'application
- URL : **http://localhost:3001**
- Le serveur doit être lancé avec `npm run dev`

### 2. Se connecter en tant qu'Agent Facturation
Sur la page de connexion, utilisez ces identifiants :

```
Identifiant : agent@moov.tg
Mot de passe : agent123
```

### 3. Accès automatique
Après connexion, vous serez **automatiquement redirigé** vers :
```
/agent/dashboard
```

## 📍 Pages Agent Facturation Disponibles

Une fois connecté, vous avez accès à :

| Page | URL | Description |
|------|-----|-------------|
| **Dashboard** | `/agent/dashboard` | Vue d'ensemble stats + graphiques |
| **Gestion Forfaits** | `/agent/forfaits` | Gestion des forfaits (prépayés/postpayés) |
| **Gestion Services** | `/agent/services` | Gestion des services (No Limit, BlackBerry, etc.) |
| **Publication PDF** | `/agent/publication-pdf` | Envoi des PDF de factures |

## 🎨 Pages Modernes Redesignées

Les pages suivantes ont été redesignées avec Tailwind + Motion :
- ✅ AgentDashboard.jsx (bento grid, glassmorphism, stats animées)
- ✅ GestionForfaits.jsx (tables modernes, modals)
- ✅ GestionServices.jsx (toggle switches, badges)
- ✅ AdminDashboard.jsx (complètement refait)

## 🔧 Si les pages ne s'affichent pas correctement

### Vérifier que le serveur tourne
```bash
cd Front
npm run dev
```

### Vider le cache du navigateur
1. Ouvrir la console (F12)
2. Faire un **Ctrl+Maj+R** (rechargement forcé)
3. Ou vider le cache dans les paramètres du navigateur

### Vérifier la console pour des erreurs
Ouvrir les DevTools (F12) et regarder l'onglet Console pour d'éventuelles erreurs.

## 🆘 Comptes de Test

### Agent Facturation (vous)
```
Email : agent@moov.tg
Password : agent123
Rôle : AGENT_FACTURATION
Accès : /agent/*
```

### Super Admin
```
Email : admin@moov.tg
Password : admin123
Rôle : SUPER_ADMIN
Accès : /admin/*
```

### Payeur (Client entreprise)
```
Identifiant : CT-001234
Password : payeur123
Rôle : PAYEUR
Accès : /dashboard, /factures, /simulation
```

### Employé (Client individuel)
```
Identifiant : 90123456
Password : 5678
Rôle : EMPLOYE
Accès : /dashboard, /factures, /simulation
```

## 🎯 Navigation dans l'application

Une fois connecté en tant qu'Agent Facturation, utilisez la navigation latérale :

```
📊 Dashboard
   ↳ Vue d'ensemble des stats

💳 Gestion Forfaits
   ↳ Créer/Modifier/Supprimer forfaits

🔧 Gestion Services
   ↳ Activer/Désactiver services

📄 Publication PDF
   ↳ Envoyer factures par email/sms

🚪 Déconnexion
```

## 🚀 Prochaines Étapes

Les pages suivantes seront modernisées prochainement :
- ⏳ DashboardEmploye.jsx
- ⏳ DashboardPayeur.jsx
- ⏳ Factures.jsx
- ⏳ Simulation.jsx

---

**Note** : Si vous voyez encore des problèmes d'affichage, vérifiez que :
1. Tailwind est bien installé (`npm list tailwindcss` → devrait montrer la version 3.x)
2. Le fichier `global.css` contient les directives `@tailwind`
3. Le serveur a été redémarré après l'installation
