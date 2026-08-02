# Implémentation Gestion des Identifiants

## 📋 Résumé

Système complet de gestion des identifiants lors de la création de comptes par les agents et chefs de facturation.

---

## ✅ Fichiers créés

### 1. **`passwordUtils.js`**
**Emplacement** : `Front/src/utils/passwordUtils.js`

**Fonctions** :
```javascript
// Génération MDP par défaut (Moov@AAAAMMJJ)
genererMotDePasseDefaut()

// Génération MDP aléatoire sécurisé
genererMotDePasseAleatoire(longueur = 12)

// Validation avec règles de sécurité
validerMotDePasse(mdp)

// Génération login payeur (A26XXXXXX)
genererLoginPayeur()

// Génération login employé (numéro sans espaces)
genererLoginEmploye(numeroLigne)

// Couleurs selon force du MDP
getCouleurForce(force)
```

### 2. **`PasswordInput.jsx`**
**Emplacement** : `Front/src/components/common/PasswordInput.jsx`

**Composant réutilisable** avec :
- 👁️ Bouton Voir/Cacher
- 🔄 Bouton Générer aléatoire
- 📊 Indicateur de force (barre de progression)
- ✓ Liste des exigences en temps réel
- 🎨 Validation visuelle (vert = validé)

---

## 🔧 Modifications apportées

### **GestionComptesClients.jsx**

#### Nouveaux états :
```javascript
const [login, setLogin] = useState('')
const [motDePasse, setMotDePasse] = useState('')
const [forcerChangement, setForcerChangement] = useState(true)
const [envoyerEmail, setEnvoyerEmail] = useState(true)
```

#### Génération automatique à l'ouverture du modal :
```javascript
const ouvrirModal = (type) => {
  // Générer login
  if (type === 'PAYEUR') {
    setLogin(genererLoginPayeur()) // Ex: A2600001
  }
  
  // Générer MDP par défaut
  setMotDePasse(genererMotDePasseDefaut()) // Ex: Moov@20260730
  
  // Options par défaut
  setForcerChangement(true)
  setEnvoyerEmail(true)
}
```

#### Nouvelle section "Identifiants de connexion" dans le formulaire :
- Login (auto-généré, modifiable pour payeur)
- Mot de passe avec composant PasswordInput
- Info bulle sur le format par défaut
- Checkboxes : Forcer changement, Envoyer email

---

## 🎯 Comportement

### Création d'un compte PAYEUR

1. **Agent clique sur "+ Nouveau Payeur"**
   - Modal s'ouvre

2. **Système génère automatiquement** :
   - Login : `A2600001` (année + séquence)
   - MDP : `Moov@20260730` (date du jour)

3. **Agent peut** :
   - ✏️ Modifier le login (bouton "Regénérer")
   - ✏️ Modifier le MDP (édition directe)
   - 🔄 Générer un MDP aléatoire (bouton dans l'input)
   - 👁️ Voir/Cacher le MDP
   - ☑️ Cocher/Décocher "Forcer changement"
   - ☑️ Cocher/Décocher "Envoyer email"

4. **Validation en temps réel** :
   - Barre de force du MDP (Faible → Excellent)
   - Exigences marquées ✓ ou ○
   - Couleurs : Rouge → Orange → Bleu → Vert

5. **À la soumission** :
   - Compte créé avec login et MDP
   - Flag `doitChangerMotDePasse` = true (si coché)
   - Email envoyé (si coché) avec identifiants

---

### Création d'un compte EMPLOYÉ

1. **Agent clique sur "+ Nouvel Employé"**
   - Modal s'ouvre

2. **Agent entre le numéro de ligne** :
   - Ex: `79 34 27 35`

3. **Login généré automatiquement** :
   - Depuis le numéro : `79342735`
   - Affiché en temps réel
   - Non modifiable

4. **MDP géré comme pour Payeur** :
   - Généré automatiquement : `Moov@20260730`
   - Modifiable par l'agent
   - Validation en temps réel

---

## 🔐 Formats et Règles

### **Mot de passe par défaut**
```
Format : Moov@AAAAMMJJ
Exemple : Moov@20260730

Avantages :
✅ Respecte les exigences de sécurité
✅ Simple à retenir pour l'agent
✅ Unique par jour
✅ Préfixe "Moov" identifiable
```

### **Mot de passe aléatoire**
```
Format : 12 caractères aléatoires
Exemple : Zk9@mP2vX4qR

Composition garantie :
✅ Au moins 1 majuscule
✅ Au moins 1 minuscule
✅ Au moins 1 chiffre
✅ Au moins 1 caractère spécial
```

### **Validation (exigences)**
- ✓ Longueur ≥ 8 caractères
- ✓ 1 majuscule (A-Z)
- ✓ 1 minuscule (a-z)
- ✓ 1 chiffre (0-9)
- ✓ 1 caractère spécial (@#$%^&*!)

### **Force du mot de passe**
```
Score 1-2 : Faible (rouge)
Score 3-4 : Moyen (orange)
Score 5, <12 car : Fort (bleu)
Score 5, ≥12 car : Excellent (vert)
```

---

## 📧 Email automatique

Lorsque "Envoyer les identifiants par email" est coché :

```
De : Moov Africa <noreply@moov.tg>
À : contact@biospartners.com
Objet : Vos identifiants de connexion Moov Africa

Bonjour,

Votre compte Moov Africa a été créé avec succès.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vos identifiants de connexion :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Login : A2600001
Mot de passe temporaire : Moov@20260730

Lien de connexion : https://moov.tg/login

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ IMPORTANT :
Pour des raisons de sécurité, vous devrez 
changer votre mot de passe lors de votre 
première connexion.

Cordialement,
L'équipe Moov Africa
```

---

## 🎨 Captures d'écran (conceptuelles)

### Modal création Payeur

```
┌─────────────────────────────────────────┐
│ Créer un compte Payeur            [X]   │
├─────────────────────────────────────────┤
│                                         │
│ Raison sociale *                        │
│ [BIOSPARTNERS                    ]      │
│                                         │
│ Email *                                 │
│ [contact@biospartners.com        ]      │
│                                         │
│ ━━━ 🔑 Identifiants de connexion ━━━   │
│                                         │
│ Login *                                 │
│ [A2600001                        ]      │
│ 🔄 Regénérer le login                   │
│                                         │
│ Mot de passe temporaire *               │
│ [Moov@20260730          ] 👁️ 🔄        │
│ ████████░░ Fort                         │
│ ✓ 8 caractères  ✓ Majuscule            │
│ ✓ Minuscule     ✓ Chiffre              │
│ ✓ Caractère spécial                    │
│                                         │
│ 💡 MDP par défaut : Moov@AAAAMMJJ      │
│    (ex: Moov@20260730)                 │
│                                         │
│ ☑ Forcer changement à la 1ère connexion│
│ ☑ Envoyer les identifiants par email   │
│                                         │
│ [Annuler]              [Créer]          │
└─────────────────────────────────────────┘
```

---

## 🔄 Workflow complet

### Scénario : Agent crée un compte Payeur

```
1. Agent → Clic "+ Nouveau Payeur"
   ↓
2. Modal s'ouvre
   - Login auto-généré : A2600001
   - MDP auto-généré : Moov@20260730
   ↓
3. Agent remplit les infos
   - Raison sociale
   - Email
   ↓
4. Agent vérifie/modifie les identifiants
   - Garde le MDP par défaut OU
   - Le modifie manuellement OU
   - Clique "Générer" pour MDP aléatoire
   ↓
5. Agent coche les options
   ☑ Forcer changement
   ☑ Envoyer email
   ↓
6. Agent clique "Créer"
   ↓
7. Système crée le compte
   - Stocke login + MDP hashé
   - Flag doitChangerMotDePasse = true
   ↓
8. Si email coché → Email envoyé
   ↓
9. Confirmation affichée
   "✓ Compte créé avec succès"
```

---

## 📊 Données stockées

```javascript
{
  id: '4',
  role: 'PAYEUR',
  raisonSociale: 'BIOSPARTNERS',
  email: 'contact@biospartners.com',
  
  // Identifiants
  login: 'A2600001',
  motDePasse: '$2b$10$...', // Hash du MDP
  
  // Flags de sécurité
  doitChangerMotDePasse: true,
  motDePasseTemporaire: true,
  
  // Traçabilité
  dateCreation: '2026-07-30T14:30:00Z',
  dateEnvoiIdentifiants: '2026-07-30T14:30:00Z',
  creePar: 'agent@moov.tg',
  
  // Connexions
  premiereConnexion: null,
  derniereConnexion: null,
  nbTentativesEchouees: 0,
  
  estActif: true
}
```

---

## 🚀 Prochaines étapes

### Phase 2 - Page Gestion des Accès
- Liste de tous les comptes
- Recherche et filtres
- Actions : Réinitialiser MDP, Bloquer, Débloquer
- Historique des connexions

### Phase 3 - Changement MDP obligatoire
- Écran de première connexion
- Formulaire de changement avec validation
- Redirection automatique depuis login

### Phase 4 - Sécurité avancée
- Politique d'expiration des MDP temporaires (7 jours)
- Blocage après 5 tentatives
- Historique des changements de MDP
- Notifications email automatiques

---

## ✅ Points de contrôle

- [x] Utilitaire passwordUtils.js créé
- [x] Composant PasswordInput.jsx créé
- [x] GestionComptesClients.jsx modifié
- [x] Génération auto login et MDP
- [x] Validation en temps réel
- [x] Indicateur de force
- [x] Boutons Voir/Générer
- [x] Checkboxes options
- [x] Info bulle format par défaut
- [ ] Tests de validation
- [ ] Intégration backend
- [ ] Envoi email réel
- [ ] Page changement MDP obligatoire

---

## 🎯 Résultat

Les agents peuvent maintenant créer des comptes avec :
- ✅ Identifiants générés automatiquement
- ✅ Possibilité de personnalisation
- ✅ Validation de sécurité en temps réel
- ✅ Options de gestion (forcer changement, email)
- ✅ Interface claire et intuitive

**Implémentation frontend terminée ! 🎉**

Pour tester :
1. Connectez-vous comme agent
2. Allez sur "Comptes Clients"
3. Cliquez sur "+ Nouveau Payeur" ou "+ Nouvel Employé"
4. Observez la génération automatique des identifiants
5. Testez la modification du mot de passe
6. Regardez la validation en temps réel
