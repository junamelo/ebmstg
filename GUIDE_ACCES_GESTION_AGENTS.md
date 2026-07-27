# 🚀 Guide d'accès - Gestion des Agents

---

## 📝 Compte Chef Facturation créé

Un compte **Chef Facturation** a été ajouté dans les données mock pour tester la fonctionnalité.

### 🔑 Identifiants de connexion

```
Login       : chef@moov.tg
Mot de passe: chef123
Rôle        : CHEF_FACTURATION
```

---

## 🎯 Comment accéder à la page de gestion des agents

### Étape 1 : Se connecter

1. Ouvrir votre navigateur
2. Aller sur : `http://localhost:3000/login`
3. Entrer les identifiants :
   - **Login** : `chef@moov.tg`
   - **Mot de passe** : `chef123`
4. Cliquer sur **"Se connecter"**

### Étape 2 : Accéder à la page Gestion Agents

**Option A : Via la sidebar (menu latéral)**
1. Après connexion, vous verrez la sidebar à gauche
2. Le bandeau affiche **"Chef Facturation"** en bleu
3. Dans le menu, cliquez sur **"Gestion Agents"** 📋

**Option B : Via l'URL directe**
1. Tapez directement dans la barre d'adresse : `http://localhost:3000/chef/agents`
2. Appuyez sur Entrée

---

## 🎨 Ce que vous verrez

### Dashboard avec KPI
```
┌──────────────┬──────────────┬─────────────────┐
│ Total agents │ Agents actifs│ Avec permissions│
│      2       │      2       │        0        │
└──────────────┴──────────────┴─────────────────┘
```

### Bouton "Nouvel agent"
- Bouton bleu en haut à droite : **"+ Nouvel agent"**
- Cliquez dessus pour ouvrir le formulaire de création

### Tableau des agents existants
Vous verrez les 2 agents mock déjà créés :
- **Jean Dupont** (@agent.dupont)
- **Marie Martin** (@agent.martin)

---

## ✅ Actions disponibles

### 1. Créer un nouvel agent
1. Cliquer sur **"+ Nouvel agent"**
2. Remplir le formulaire :
   - Nom d'utilisateur (ex: `agent.kouassi`)
   - Email (ex: `agent.kouassi@moov.africa`)
   - Prénom (ex: `Kwame`)
   - Nom (ex: `Kouassi`)
   - Mot de passe (min. 6 caractères)
   - Confirmer le mot de passe
   - ☑️ Cocher "Créer d'autres agents" pour donner la permission
3. Cliquer sur **"Créer l'agent"**

### 2. Modifier un agent existant
1. Cliquer sur **"Modifier"** dans la ligne d'un agent
2. Le formulaire s'ouvre pré-rempli
3. Modifier les informations souhaitées
4. Ajouter/Retirer la permission "Créer d'autres agents"
5. Cliquer sur **"Enregistrer les modifications"**

### 3. Activer/Désactiver un agent
1. Cliquer sur **"Désactiver"** pour un agent actif
2. Confirmer dans la popup
3. Le statut passe à **"Inactif"** (badge gris)
4. Cliquer sur **"Activer"** pour réactiver

### 4. Rechercher un agent
1. Utiliser la barre de recherche en haut à droite
2. Taper le nom, email ou username
3. Le tableau se filtre en temps réel

---

## 📊 Badges et indicateurs

### Badge "Étendues" (violet)
- Signifie que l'agent a la permission de **créer d'autres agents**
- Apparaît dans la colonne "Permissions"

### Badge "Standard" (gris)
- Agent sans permissions spéciales
- Ne peut PAS créer d'autres agents

### Badge "Actif" (vert)
- Compte actif et fonctionnel
- L'agent peut se connecter

### Badge "Inactif" (gris)
- Compte désactivé
- L'agent ne peut PAS se connecter

---

## 🎯 Scénario de test complet

### Test 1 : Créer un agent standard
```
1. Cliquer "Nouvel agent"
2. Remplir :
   - Username: agent.test1
   - Email: test1@moov.africa
   - Prénom: Test
   - Nom: Agent1
   - Password: test123
   - Confirmer: test123
   - ❌ NE PAS cocher "Créer d'autres agents"
3. Soumettre
4. ✅ Vérifier que l'agent apparaît avec badge "Standard"
```

### Test 2 : Créer un agent avec permissions
```
1. Cliquer "Nouvel agent"
2. Remplir les champs
3. ✅ COCHER "Créer d'autres agents"
4. Soumettre
5. ✅ Vérifier que l'agent apparaît avec badge "Étendues" violet
```

### Test 3 : Modifier un agent
```
1. Cliquer "Modifier" sur agent.test1
2. Changer le prénom en "TestModifié"
3. ✅ COCHER "Créer d'autres agents"
4. Soumettre
5. ✅ Vérifier changement de nom ET badge "Étendues"
```

### Test 4 : Désactiver puis réactiver
```
1. Cliquer "Désactiver" sur un agent actif
2. Confirmer
3. ✅ Badge passe à "Inactif"
4. Cliquer "Activer"
5. ✅ Badge repasse à "Actif"
```

---

## 🗂️ Tous les comptes de test disponibles

| Rôle | Login | Mot de passe | Description |
|------|-------|--------------|-------------|
| **Super Admin** | `admin@moov.tg` | `admin123` | Accès complet système |
| **Chef Facturation** ⭐ | `chef@moov.tg` | `chef123` | Gère les agents |
| **Agent Facturation** | `agent@moov.tg` | `agent123` | Opérations de facturation |
| **Payeur** | `A0007612` | `payeur123` | Entreprise BIOSPARTNERS |
| **Employé** | `79342735` | `5678` | Ligne individuelle |

---

## 🔧 En cas de problème

### Problème : Page blanche
**Solution** : Vérifiez la console du navigateur (F12)
- Si erreur de syntaxe → Vérifiez les fichiers modifiés
- Si 404 → Vérifiez que le serveur React tourne sur port 3000

### Problème : Bouton "Nouvel agent" invisible
**Cause** : Compte sans permission
**Solution** : 
1. Se déconnecter
2. Se reconnecter avec `chef@moov.tg` / `chef123`

### Problème : "Aucun agent trouvé"
**Cause** : Les données mock n'ont pas les agents
**Solution** : Créez vos premiers agents via le formulaire

### Problème : Sidebar icône coupée
**Cause** : Ancienne version du CSS
**Solution** : 
1. Hard refresh : `Ctrl + Shift + R` (Windows) ou `Cmd + Shift + R` (Mac)
2. Vider le cache du navigateur

---

## 📱 Navigation complète Chef Facturation

Une fois connecté en tant que Chef Facturation, vous avez accès à :

```
┌─────────────────────────────────────┐
│  🛡️ Chef Facturation               │
├─────────────────────────────────────┤
│  📊 Dashboard                       │
│  👥 Gestion Agents          ⭐ ICI  │
│  ⚙️  Gestion Services               │
│  📦 Gestion Forfaits                │
│  ☁️  Publication PDF                │
│  📜 Historique Pub.                 │
└─────────────────────────────────────┘
```

---

## 🎉 Résumé rapide

1. **Connexion** : `chef@moov.tg` / `chef123`
2. **URL directe** : `http://localhost:3000/chef/agents`
3. **Ou** : Sidebar → "Gestion Agents"
4. **Créer** : Bouton "+ Nouvel agent"
5. **Permissions** : Cocher "Créer d'autres agents" si besoin

**C'est prêt à tester ! 🚀**

---

**Date** : 27 juillet 2026  
**Version** : 1.0.0
