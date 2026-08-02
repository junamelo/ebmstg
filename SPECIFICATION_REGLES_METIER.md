# SPÉCIFICATION DES RÈGLES MÉTIER
## Portail Web de Publication de Factures Clients Postpayés – Moov Africa

**Version** : 1.0  
**Date** : 30 juillet 2026  
**Statut** : Règles figées - Priorité 0

---

## 1. OBJECTIF DU PORTAIL

Permettre aux agents de facturation Moov Africa de :
- Uploader et découper des fichiers PDF de factures massifs
- Associer automatiquement chaque facture à l'entreprise et la ligne concernées
- Publier les factures validées pour consultation par les clients (payeurs et employés)
- Suivre l'historique des publications et le cycle de vie des factures

Permettre aux clients (payeurs et employés) de :
- Consulter leurs factures publiées
- Télécharger les PDF de leurs factures
- Suivre leur historique de facturation

---

## 2. GLOSSAIRE

| Terme | Définition |
|-------|------------|
| **Payeur** | Utilisateur responsable du règlement des factures d'une ou plusieurs entreprises |
| **Employé** | Utilisateur titulaire d'une ligne téléphonique dans une entreprise |
| **Ligne** | Numéro de téléphone mobile (MSISDN) associé à une entreprise |
| **MSISDN** | Mobile Station International Subscriber Directory Number - Identifiant unique d'une ligne |
| **Facture globale** | Facture consolidée pour l'ensemble d'une entreprise |
| **Facture SOM / individuelle** | Facture détaillée pour une ligne téléphonique spécifique |
| **Publication** | Action de rendre les factures accessibles aux clients après validation |
| **Cycle** | Cycle de facturation : HYB (Hybride) ou OP (Opérationnel/Postpayé) |
| **Matching** | Processus d'association automatique PDF ↔ Facture en base de données |

---

## 3. RÔLES ET MATRICE DES PERMISSIONS

### 3.1 Rôles autorisés

Les cinq rôles du système sont :

1. **SUPER_ADMIN** : Administration complète du système
2. **CHEF_FACTURATION** : Supervision de l'équipe et des opérations de facturation
3. **AGENT_FACTURATION** : Traitement quotidien des factures et publications
4. **PAYEUR** : Consultation des factures de son/ses entreprise(s)
5. **EMPLOYE** : Consultation de ses factures individuelles

### 3.2 Permissions par rôle

| Permission | SUPER_ADMIN | CHEF | AGENT | PAYEUR | EMPLOYE |
|------------|-------------|------|-------|--------|---------|
| Gérer utilisateurs | ✅ | Agents seulement | Payeurs/Employés | ❌ | ❌ |
| Créer entreprise | ✅ | ✅ | ✅ | ❌ | ❌ |
| Créer ligne | ✅ | ✅ | ✅ | ❌ | ❌ |
| Affecter employé → ligne | ✅ | ✅ | ✅ | ❌ | ❌ |
| Créer facture | ✅ | ✅ | ✅ | ❌ | ❌ |
| Upload PDF | ✅ | ✅ | ✅ | ❌ | ❌ |
| Valider facture | ✅ | ✅ | ✅ | ❌ | ❌ |
| Publier facture | ✅ | ✅ | ✅ | ❌ | ❌ |
| Annuler facture | ✅ | ✅ | ❌ | ❌ | ❌ |
| Consulter toutes factures | ✅ | ✅ | ✅ | ❌ | ❌ |
| Consulter ses factures | ✅ | ✅ | ✅ | ✅ Entreprises | ✅ Lignes |
| Télécharger PDF | ✅ | ✅ | ✅ | ✅ | ✅ |
| Voir logs système | ✅ | ✅ | ❌ | ❌ | ❌ |

### 3.3 Permissions définies dans le code

```python
ROLE_PERMISSIONS = {
    'SUPER_ADMIN': ['*'],
    
    'CHEF_FACTURATION': [
        'accounts.create_agent',
        'accounts.view_all',
        'accounts.edit_agents',
        'billing.publish',
        'billing.cancel',
        'billing.view_all',
        'tarifs.create',
        'services.create',
        'reports.view_all',
        'system.view_logs',
    ],
    
    'AGENT_FACTURATION': [
        'billing.publish',
        'billing.view_all',
        'tarifs.create',
        'services.create',
        'reports.view_all',
    ],
    
    'PAYEUR': [
        'billing.view_own',
        'billing.export_own',
    ],
    
    'EMPLOYE': [
        'billing.view_own',
    ],
}
```

---

## 4. MODÈLE DE DONNÉES MÉTIER

### 4.1 Hiérarchie fonctionnelle

```
Entreprise / Contrat (Company)
    ├── Payeur (User.role=PAYEUR)
    │   └── Voit : toutes factures (globales + individuelles)
    │
    └── Lignes téléphoniques (Line)
        ├── MSISDN (identifiant unique)
        ├── Employé (User.role=EMPLOYE) [optionnel]
        │   └── Voit : uniquement ses factures individuelles
        │
        └── Factures (Invoice)
            ├── Facture globale (line=NULL)
            └── Facture individuelle/SOM (line=Line)
```

### 4.2 Règles d'affectation

#### Entreprise → Payeur
- **Cardinalité** : Une entreprise a UN payeur
- **Clé** : `Company.payeur` → `User` (FK)
- **Règle** : Le payeur doit avoir `role='PAYEUR'`
- **Implication** : Le payeur voit TOUTES les factures de cette entreprise

#### Ligne → Entreprise
- **Cardinalité** : Une ligne appartient à UNE entreprise
- **Clé** : `Line.company` → `Company` (FK, required)
- **Unicité** : Le MSISDN est unique dans tout le système

#### Ligne → Employé
- **Cardinalité** : Une ligne peut être affectée à UN employé (optionnel)
- **Clé** : `Line.employe` → `User` (FK, nullable)
- **Règle** : L'employé doit avoir `role='EMPLOYE'`
- **Implication** : Si affecté, l'employé voit les factures individuelles de cette ligne

#### Facture → Entreprise
- **Cardinalité** : Une facture est liée à UNE entreprise
- **Clé** : `Invoice.company` → `Company` (FK, required)
- **Règle** : Toujours obligatoire

#### Facture → Ligne (pour SOM uniquement)
- **Cardinalité** : Une facture individuelle est liée à UNE ligne
- **Clé** : `Invoice.line` → `Line` (FK, nullable)
- **Règle** :
  - `line=NULL` → Facture **GLOBALE**
  - `line=Line(...)` → Facture **INDIVIDUELLE/SOM**

### 4.3 Règle fondamentale de liaison

**INTERDIT** : Lier par nom de personne ou texte libre

**OBLIGATOIRE** : Lier par identifiants de base de données (UUID, FK) et MSISDN

---

## 5. TYPES DE FACTURES

### 5.1 Facture GLOBALE

**Caractéristiques** :
- Une facture par entreprise par période et cycle
- Champ `line` = NULL
- Contient les consommations consolidées de toute l'entreprise

**Rapprochement PDF** :
- Priorité 1 : Numéro de facture exact
- Priorité 2 : Numéro de compte entreprise

**Visibilité** :
- ✅ Payeur de l'entreprise (après publication)
- ❌ Employés (n'ont pas accès)

### 5.2 Facture INDIVIDUELLE / SOM

**Caractéristiques** :
- Une facture par ligne/MSISDN par période et cycle
- Champ `line` = Line(id=X)
- Contient les consommations détaillées de la ligne

**Rapprochement PDF** :
- Priorité 1 : Numéro de facture exact
- Priorité 2 : MSISDN exact
- Priorité 3 : Compte entreprise (si MSISDN absent)

**Visibilité** :
- ✅ Payeur de l'entreprise (après publication)
- ✅ Employé affecté à cette ligne (après publication)
- ❌ Autres employés

---

## 6. CYCLE DE VIE DES FACTURES

### 6.1 Statuts obligatoires

```
StatutFacture(models.TextChoices):
    BROUILLON = 'BROUILLON'   # Créée, non prête
    EN_COURS = 'EN_COURS'     # Prête pour matching PDF
    VALIDEE = 'VALIDEE'       # PDF attaché, contrôlée
    PUBLIEE = 'PUBLIEE'       # Visible clients
    PAYEE = 'PAYEE'           # Réglée
    ANNULEE = 'ANNULEE'       # Annulée
```

### 6.2 Transitions autorisées

```
BROUILLON → EN_COURS    [Agent valide la facture]
EN_COURS → VALIDEE      [PDF attaché automatiquement]
VALIDEE → PUBLIEE       [Agent/Chef publie]
PUBLIEE → PAYEE         [Paiement enregistré]

EN_COURS → ANNULEE      [Chef annule]
VALIDEE → ANNULEE       [Chef annule avant publication]
```

### 6.3 Transitions INTERDITES

| Depuis | Vers | Raison |
|--------|------|--------|
| ANNULEE | BROUILLON | Une facture annulée ne peut pas être réactivée sans procédure dédiée |
| ANNULEE | EN_COURS | Une facture annulée ne peut pas être réactivée sans procédure dédiée |
| ANNULEE | VALIDEE | Une facture annulée ne peut pas être réactivée sans procédure dédiée |
| PAYEE | EN_COURS | Une facture payée ne peut pas revenir en cours |
| PAYEE | BROUILLON | Une facture payée ne peut pas revenir en brouillon |
| PUBLIEE | EN_COURS | Une facture publiée ne peut être remplacée silencieusement |
| PUBLIEE | BROUILLON | Une facture publiée ne peut être remplacée silencieusement |

### 6.4 Règle de statut pour matching PDF

**RÈGLE STRICTE** : Un PDF ne peut être automatiquement associé qu'à une facture en statut `EN_COURS`.

**Exceptions** :
- Consultation/téléchargement d'un PDF déjà attaché : tous statuts
- Notification "facture déjà traitée" : si statut ≥ VALIDEE

---

## 7. WORKFLOW DE PUBLICATION PDF

### 7.1 Processus officiel

```
1. UPLOAD
   Agent choisit :
   - Fichier PDF
   - Cycle (HYB ou OP)
   - Période (début et fin)

2. DÉCOUPAGE
   Système analyse le PDF :
   - Détecte la structure (blocs de pages)
   - Découpe en fichiers individuels
   - Extraction texte par bloc

3. IDENTIFICATION
   Pour chaque bloc, extraction :
   - Numéro de facture
   - MSISDN (si présent)
   - Compte entreprise (fallback)

4. MATCHING
   Recherche facture EN_COURS correspondante :
   a) Par numéro de facture exact (priorité 1)
   b) Par MSISDN exact (priorité 2)
   c) Par compte entreprise (priorité 3, seulement si MSISDN absent)

5. VALIDATION
   Si facture trouvée :
   - Attachement du PDF
   - Changement statut → VALIDEE
   - Création entrée historique

6. RAPPORT
   Résultat du traitement :
   - Fichiers créés
   - Factures mises à jour
   - Erreurs de matching

7. PUBLICATION FINALE
   Agent/Chef sélectionne factures VALIDEE :
   - Action "Publier"
   - Changement statut → PUBLIEE
   - Factures deviennent visibles clients
```

### 7.2 Ordre de matching obligatoire

**Priorité 1** : Numéro de facture exact
- Recherche : `numero_facture` contient l'identifiant extrait
- Le plus fiable car unique

**Priorité 2** : MSISDN exact
- Recherche : `company__lines__msisdn` = MSISDN extrait
- Pour factures SOM uniquement

**Priorité 3** : Compte entreprise
- Recherche : `company__compte` = Compte extrait
- **UNIQUEMENT** si aucun MSISDN exploitable
- Pour factures globales principalement

### 7.3 Règles d'erreurs et exceptions

#### Erreur : Aucun identifiant
- **Cause** : Extraction texte impossible ou PDF vide
- **Action** : Signaler l'erreur, ne pas créer de matching

#### Erreur : Aucune facture candidate
- **Cause** : Aucune facture EN_COURS pour ce cycle/période/identifiant
- **Action** : Signaler l'erreur, PDF créé mais non attaché

#### Information : Facture déjà traitée
- **Cause** : Facture trouvée mais statut ≥ VALIDEE
- **Action** : Ne pas réécraser, informer "déjà traitée"
- **Note** : Ce n'est PAS une erreur technique

#### Erreur : Mauvais cycle ou période
- **Cause** : Cycle du PDF ≠ cycle de la ligne/facture
- **Action** : Aucune association automatique

#### Erreur : Plusieurs factures candidates
- **Cause** : Plusieurs factures EN_COURS matchent les critères
- **Action** : Erreur explicite, **JAMAIS** choisir arbitrairement
- **Solution** : Agent doit clarifier manuellement

#### Erreur : Type incompatible
- **Règle** : Un PDF global ne peut pas écraser une facture individuelle
- **Règle** : Un PDF individuel ne peut pas être attaché à une facture globale
- **Action** : Erreur explicite

---

## 8. RÈGLES DE VISIBILITÉ

### 8.1 Principe général

**RÈGLE FONDAMENTALE** : Le filtrage des données DOIT être effectué côté **backend**, jamais uniquement côté frontend.

### 8.2 Visibilité par rôle

#### SUPER_ADMIN / CHEF_FACTURATION / AGENT_FACTURATION

```python
# Accès complet selon permissions
queryset = Invoice.objects.all()
```

#### PAYEUR

```python
# Uniquement factures PUBLIEE de ses entreprises
queryset = Invoice.objects.filter(
    company__payeur=request.user,
    statut='PUBLIEE'
)
```

**Contenu visible** :
- Toutes factures globales de ses entreprises
- Toutes factures individuelles/SOM de ses entreprises
- Peut télécharger tous les PDF associés

#### EMPLOYE

```python
# Uniquement factures PUBLIEE de ses lignes affectées
queryset = Invoice.objects.filter(
    line__employe=request.user,
    statut='PUBLIEE'
)
```

**Contenu visible** :
- Uniquement ses factures individuelles/SOM
- Ne voit PAS les factures globales
- Ne voit PAS les factures des autres lignes
- Peut télécharger uniquement ses PDF

### 8.3 Règles de sécurité

**INTERDIT** :
- Accéder au PDF ou détail d'une facture en modifiant l'URL
- Voir des factures non publiées (statut < PUBLIEE) pour payeur/employé
- Voir des factures d'une autre entreprise (payeur)
- Voir des factures d'une autre ligne (employé)

**OBLIGATOIRE** :
- Vérification backend de `request.user` pour chaque requête
- Vérification de `statut='PUBLIEE'` pour clients
- Vérification de la relation entreprise/ligne avant affichage PDF

---

## 9. ERREURS MÉTIER ATTENDUES

### 9.1 Erreurs de matching PDF

| Code | Description | Cause | Action |
|------|-------------|-------|--------|
| ERR_NO_ID | Aucun identifiant trouvé | PDF illisible, scanné sans OCR | Signaler à l'agent |
| ERR_NO_INVOICE | Aucune facture candidate | Pas de facture EN_COURS pour cette période/cycle | Créer facture d'abord |
| INFO_ALREADY | Facture déjà traitée | Statut ≥ VALIDEE | Informer (pas erreur) |
| ERR_BAD_CYCLE | Cycle incompatible | PDF HYB vs ligne OP | Vérifier cycle |
| ERR_MULTIPLE | Plusieurs candidats | Doublons en base | Clarification manuelle |
| ERR_TYPE_MISMATCH | Type incompatible | PDF global vs facture SOM | Vérifier type |

### 9.2 Erreurs de permissions

| Code | Description | Cause | Action |
|------|-------------|-------|--------|
| ERR_PERM_DENIED | Permission refusée | Utilisateur sans droit | Vérifier rôle |
| ERR_NOT_PUBLISHED | Facture non publiée | Employé/Payeur accède à VALIDEE | Attendre publication |
| ERR_WRONG_COMPANY | Mauvaise entreprise | Payeur accède à autre entreprise | Bloquer accès |
| ERR_WRONG_LINE | Mauvaise ligne | Employé accède à autre ligne | Bloquer accès |

### 9.3 Erreurs de transition de statut

| Code | Description | Cause | Action |
|------|-------------|-------|--------|
| ERR_INVALID_TRANSITION | Transition interdite | Ex: ANNULEE → BROUILLON | Rejeter |
| ERR_ALREADY_PAID | Facture déjà payée | Tentative modification | Bloquer |
| ERR_ALREADY_PUBLISHED | Facture déjà publiée | Tentative remplacement PDF | Informer |

---

## 10. RÈGLES À VALIDER

Ces règles nécessitent validation métier Moov Africa :

### 10.1 Délais et notifications

- **À VALIDER** : Délai entre VALIDEE et obligation de publication
- **À VALIDER** : Notification email automatique aux clients après publication
- **À VALIDER** : Rappel automatique avant échéance

### 10.2 Modifications post-publication

- **À VALIDER** : Procédure de correction d'une facture publiée
- **À VALIDER** : Possibilité d'annuler une facture PUBLIEE
- **À VALIDER** : Archivage des factures PAYEE

### 10.3 Gestion des doublons

- **À VALIDER** : Action si même MSISDN dans plusieurs entreprises
- **À VALIDER** : Action si même numéro de facture réutilisé

### 10.4 Données historiques

- **À VALIDER** : Durée de conservation des factures
- **À VALIDER** : Archivage automatique après X mois

---

## 11. CRITÈRES D'ACCEPTATION FONCTIONNELS

### 11.1 Publication PDF

✅ **AC1** : L'agent peut uploader un PDF de factures multiples  
✅ **AC2** : Le système découpe le PDF en fichiers individuels  
✅ **AC3** : Chaque fichier est automatiquement associé à la facture EN_COURS correspondante  
✅ **AC4** : Les factures associées passent au statut VALIDEE  
✅ **AC5** : Un rapport de traitement est généré (succès/erreurs)  
✅ **AC6** : Les fichiers non associés sont signalés avec la raison  

### 11.2 Consultation Payeur

✅ **AC7** : Un payeur voit toutes les factures PUBLIEE de ses entreprises  
✅ **AC8** : Un payeur voit les factures globales et individuelles  
✅ **AC9** : Un payeur peut télécharger tous les PDF de ses factures  
❌ **AC10** : Un payeur ne peut pas voir les factures d'autres entreprises  
❌ **AC11** : Un payeur ne peut pas voir les factures non publiées  

### 11.3 Consultation Employé

✅ **AC12** : Un employé voit uniquement les factures PUBLIEE de ses lignes affectées  
❌ **AC13** : Un employé ne voit pas les factures globales  
❌ **AC14** : Un employé ne voit pas les factures d'autres lignes  
✅ **AC15** : Un employé peut télécharger le PDF de ses factures  

### 11.4 Sécurité

❌ **AC16** : Modifier l'URL ne permet pas d'accéder aux factures d'autrui  
❌ **AC17** : Les PDF non publiés ne sont pas accessibles directement  
✅ **AC18** : Chaque action sensible génère une entrée d'historique  

### 11.5 Workflow

✅ **AC19** : Une facture BROUILLON peut passer à EN_COURS  
✅ **AC20** : Une facture EN_COURS peut passer à VALIDEE (après PDF)  
✅ **AC21** : Une facture VALIDEE peut passer à PUBLIEE (action agent)  
❌ **AC22** : Une facture ANNULEE ne peut pas revenir à un statut actif  
❌ **AC23** : Une facture PAYEE ne peut pas revenir à EN_COURS  

---

## 12. CONFORMITÉ DU CODE ACTUEL

### 12.1 Conforme aux règles

✅ Les 5 rôles sont correctement définis  
✅ Les statuts de facture sont complets  
✅ La liaison Company → Payeur existe  
✅ La liaison Line → Employe existe  
✅ La liaison Invoice → Line existe  
✅ Le filtrage par rôle est implémenté dans `InvoiceViewSet.get_queryset()`  
✅ Les permissions granulaires existent  
✅ L'historique des actions est tracé  

### 12.2 Écarts identifiés (non corrigés)

⚠️ **Transition ANNULEE → actif** : Pas de validation explicite dans le code  
⚠️ **Visibilité statut < PUBLIEE** : Pas de filtre `statut='PUBLIEE'` pour payeur/employé  
⚠️ **Plusieurs factures candidates** : Pas de gestion explicite de l'erreur  
⚠️ **Notifications** : Non implémentées  

**Note** : Ces écarts relèvent des Priorités 1-3 et ne sont pas corrigés dans cette phase.

---

**Fin de la spécification des règles métier**

