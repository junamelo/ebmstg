# Guide de test - Création de comptes utilisateurs

## Vue d'ensemble

La fonctionnalité de création de comptes permet aux agents de créer des comptes **Payeur** (entreprises) et **Employé** (utilisateurs de lignes) avec génération automatique des identifiants de connexion.

## Accès à la fonctionnalité

1. Se connecter avec un compte Agent :
   - **Email** : `agent@moov.tg`
   - **Mot de passe** : `agent123`

2. Dans le menu latéral, cliquer sur **"Gestion des Comptes Clients"**

## Scénarios de test

### Test 1 : Création d'un compte Payeur (Entreprise)

1. Cliquer sur le bouton **"+ Nouveau Payeur"** (orange)
2. Le modal s'ouvre avec un formulaire scrollable
3. Remplir les champs :
   - **Raison sociale** : Ex. "TOTAL TOGO"
   - **Numéro de contrat** : Ex. "C26000123"
   - **Email** : Ex. "contact@totaltogo.com"

4. **Section Identifiants de connexion** (en bas du formulaire) :
   - **Login** : Généré automatiquement au format `A26XXXXXX`
     - Bouton "Regénérer" pour obtenir un nouveau login
   - **Mot de passe temporaire** : Généré automatiquement `Moov@AAAAMMJJ`
     - Bouton œil pour voir/cacher
     - Bouton refresh pour générer un mot de passe aléatoire sécurisé
     - Barre de force du mot de passe (faible/moyen/fort/excellent)
     - Liste des exigences avec checkmarks
   - **Checkboxes** :
     - ☑ Forcer changement à la première connexion (coché par défaut)
     - ☑ Envoyer les identifiants par email (coché par défaut)

5. Cliquer sur **"Créer"**
6. Vérifier :
   - Le compte apparaît dans la liste avec un badge "Payeur" orange
   - Si "Envoyer email" coché → message dans la console (F12)

### Test 2 : Création d'un compte Employé

1. Cliquer sur le bouton **"+ Nouvel Employé"** (bleu)
2. Remplir les champs :
   - **Nom** : Ex. "JOHNSON"
   - **Prénom** : Ex. "Marie"
   - **Numéro de ligne** : Ex. "90 12 34 56"
   - **Entreprise** : Ex. "TOTAL TOGO"
   - **Email** : Ex. "m.johnson@totaltogo.com"

3. **Section Identifiants de connexion** :
   - **Login** : Généré AUTOMATIQUEMENT depuis le numéro (sans espaces)
     - Ex: "90123456" pour "90 12 34 56"
     - Champ grisé (lecture seule)
   - **Mot de passe temporaire** : Même fonctionnement que Payeur
   - **Checkboxes** : Identique

4. Cliquer sur **"Créer"**
5. Vérifier :
   - Le compte apparaît avec un badge "Employé" bleu
   - Le login est le numéro sans espaces

### Test 3 : Génération de mots de passe

#### Mot de passe par défaut
- Format : `Moov@AAAAMMJJ`
- Exemple aujourd'hui (30/07/2026) : `Moov@20260730`
- Généré automatiquement à l'ouverture du modal

#### Mot de passe aléatoire
1. Cliquer sur l'icône **refresh** (🔄) à droite du champ
2. Un mot de passe fort est généré automatiquement :
   - 12 caractères minimum
   - Majuscules + minuscules + chiffres + caractères spéciaux
   - Barre de force à 100% (Excellent)

#### Mot de passe personnalisé
1. Effacer le champ et taper un mot de passe
2. Voir en temps réel :
   - La barre de force évoluer
   - Les exigences se valider (✓ ou ○)
   - Couleur : rouge (faible) → orange (moyen) → bleu (fort) → vert (excellent)

### Test 4 : Validation du formulaire

#### Champs obligatoires - Payeur
- Raison sociale
- Numéro de contrat
- Email
- Login
- Mot de passe

#### Champs obligatoires - Employé
- Nom
- Prénom
- Numéro de ligne
- Entreprise
- Email
- Mot de passe

#### Tests de validation
1. Essayer de soumettre sans remplir les champs → message d'erreur
2. Email invalide → validation HTML5
3. Mot de passe trop faible → visible mais accepté (pour flexibilité agent)

### Test 5 : Scroll du modal

Le formulaire est long (surtout Employé avec section identifiants) :

1. Ouvrir le modal de création
2. Vérifier que :
   - L'en-tête reste fixe en haut
   - Le corps du formulaire défile (scroll)
   - Les boutons "Créer" / "Annuler" restent visibles en bas
   - Pas de coupure du contenu

### Test 6 : Options d'envoi

#### Forcer changement à la première connexion
- **Si coché** : L'utilisateur devra changer son mot de passe à sa première connexion
- **Si décoché** : L'utilisateur peut garder le mot de passe temporaire

#### Envoyer les identifiants par email
- **Si coché** : Un email avec login et mot de passe est envoyé (simulé en console pour le moment)
- **Si décoché** : Pas d'email envoyé, l'agent doit transmettre manuellement

### Test 7 : Responsive et interactions

1. **Bouton "Voir/Cacher"** (œil) :
   - Cliquer → mot de passe affiché en clair
   - Re-cliquer → masqué à nouveau

2. **Bouton "Générer"** (refresh) :
   - Cliquer plusieurs fois → nouveau mot de passe à chaque fois
   - Vérifier que la barre de force se met à jour

3. **Bouton "Regénérer le login"** (Payeur uniquement) :
   - Génère un nouveau login A26XXXXXX
   - Le numéro change à chaque clic

## Messages et retours visuels

### Indicateur de force du mot de passe

| Force | Couleur | Barre | Critères |
|-------|---------|-------|----------|
| Faible | Rouge | 25% | Moins de 4 critères |
| Moyen | Orange | 50% | 4 critères remplis |
| Fort | Bleu | 75% | 5 critères, <12 caractères |
| Excellent | Vert | 100% | 5 critères, ≥12 caractères |

### Exigences du mot de passe
- ○ → ✓ Au moins 8 caractères
- ○ → ✓ Une majuscule
- ○ → ✓ Une minuscule
- ○ → ✓ Un chiffre
- ○ → ✓ Un caractère spécial (@#$%^&*!)

### Badges dans la liste
- **Payeur** : Badge orange "Payeur"
- **Employé** : Badge bleu "Employé"
- **Statut** : Badge vert "Actif" / rouge "Inactif"

## Console navigateur (F12)

Lors de la création avec "Envoyer email" coché, vérifier dans la console :

```
📧 Email envoyé à: contact@totaltogo.com
Login: A2600123
Mot de passe temporaire: Moov@20260730
```

## Problèmes connus et solutions

### Le modal ne s'affiche pas complètement
- **Solution** : Vérifier que `max-h-[90vh]` et `overflow-y-auto` sont présents
- **Corrigé** : Oui, dans cette version

### Les illustrations ne s'affichent pas
- **Solution** : Composant `ImageWithFallback` appliqué
- **Fallback** : Icône SVG placeholder si erreur
- **Corrigé** : Oui, sur toutes les pages

### Le login Employé ne se génère pas
- **Cause** : Numéro de ligne vide
- **Solution** : Remplir d'abord le numéro de ligne
- **Note** : Le login se met à jour automatiquement

### La barre de force ne s'affiche pas
- **Cause** : Champ mot de passe vide
- **Normal** : La barre apparaît dès qu'on tape des caractères

## Données de test

### Comptes Payeur exemples
```
Raison sociale: TOTAL TOGO
Numéro contrat: C26000123
Email: contact@totaltogo.com
Login: A26001234
MDP: Moov@20260730

Raison sociale: ECOBANK TOGO
Numéro contrat: C26000456
Email: contact@ecobank.tg
Login: A26005678
MDP: Moov@20260730
```

### Comptes Employé exemples
```
Nom: JOHNSON
Prénom: Marie
Numéro: 90 12 34 56
Entreprise: TOTAL TOGO
Email: m.johnson@totaltogo.com
Login: 90123456
MDP: Moov@20260730

Nom: ADAMA
Prénom: Koffi
Numéro: 79 98 76 54
Entreprise: ECOBANK TOGO
Email: k.adama@ecobank.tg
Login: 79987654
MDP: Moov@20260730
```

## Checklist de validation

- [ ] Modal s'ouvre correctement (animation)
- [ ] Tous les champs sont visibles (avec scroll)
- [ ] Login généré automatiquement pour Payeur
- [ ] Login dérivé du numéro pour Employé
- [ ] Mot de passe par défaut au format Moov@AAAAMMJJ
- [ ] Bouton "Voir/Cacher" fonctionne
- [ ] Bouton "Générer" crée un mot de passe fort
- [ ] Barre de force se met à jour en temps réel
- [ ] Exigences se cochent dynamiquement
- [ ] Checkboxes fonctionnent
- [ ] Création ajoute le compte à la liste
- [ ] Badge correct (Payeur orange / Employé bleu)
- [ ] Message console si email activé
- [ ] Annuler ferme le modal sans créer

---

**Version** : 30 juillet 2026  
**Statut** : ✅ Prêt pour tests utilisateurs  
**Corrections appliquées** : Scroll modal + ImageWithFallback
