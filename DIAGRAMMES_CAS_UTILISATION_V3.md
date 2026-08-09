# 📊 Diagrammes de Cas d'Utilisation UML
## Portail de Facturation Moov Africa Togo

**Version :** 3.0 (Conforme règles académiques UML)  
**Date :** 06 août 2026  
**Auteur :** Benoit BANLEPO Mintre

---

## ⚠️ Règles UML appliquées

Ce document respecte les règles académiques des diagrammes de cas d'utilisation :
- ✅ Vision utilisateur (pas technique)
- ✅ Fonctionnalités essentielles uniquement
- ✅ Limites du système clairement définies
- ✅ Acteurs principaux/secondaires distingués
- ✅ Relations `<<include>>` et `<<extend>>` correctes
- ✅ Descriptions textuelles pour cas importants
- ✅ Diagrammes lisibles et non surchargés

---

## Table des matières

1. [Limites du système](#1-limites-du-système)
2. [Identification des acteurs](#2-identification-des-acteurs)
3. [Diagramme global](#3-diagramme-global)
4. [Diagrammes détaillés](#4-diagrammes-détaillés)
5. [Descriptions textuelles](#5-descriptions-textuelles)
6. [Règles UML](#6-règles-uml)

---

## 1. Limites du système

### Système : **Portail de Facturation Moov Africa Togo**

**Objectif :** Permettre la gestion et la consultation des factures des clients entreprises.

**Périmètre :**

- ✅ **Dans le système :** Gestion contrats, publication factures, consultation, notifications
- ❌ **Hors système :** Génération factures (système billing Moov), paiement

**Frontières :**
```
┌──────────────────────────────────────────┐
│  PORTAIL DE FACTURATION MOOV AFRICA      │
│                                          │
│  • Gestion contrats entreprises         │
│  • Publication factures PDF             │
│  • Consultation factures                │
│  • Notifications clients                │
│  • Administration système               │
│                                          │
└──────────────────────────────────────────┘
```

---

## 2. Identification des acteurs

### 2.1 Acteurs humains (principaux)

| Acteur | Description | Responsabilités principales |
|--------|-------------|----------------------------|
| **Super Admin** | Administrateur système | Configuration, gestion tous utilisateurs |
| **Chef Facturation** | Responsable facturation | Supervision, validation, résiliation |
| **Agent Facturation** | Opérateur facturation | Publication factures quotidienne |
| **Payeur** | Client entreprise | Consultation ses contrats et factures |
| **Employé** | Salarié entreprise cliente | Consultation sa facture personnelle |

### 2.2 Acteurs systèmes (secondaires)

| Acteur | Type | Description |
|--------|------|-------------|
| **Système Email** | <<actor>> | Service SMTP (Gmail) |
| **Système SMS** | <<actor>> | Service SMS (Vonage) |

### 2.3 Hiérarchie des acteurs

```
Super Admin
    |
    ├─ Chef Facturation
    |      |
    |      └─ Agent Facturation
    |
Payeur
    |
    └─ Employé
```

---

## 3. Diagramme global

### Vue d'ensemble - Fonctionnalités essentielles



```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

' === ACTEURS ===
actor "Super Admin" as Admin <<primary>>
actor "Chef\nFacturation" as Chef <<primary>>
actor "Agent\nFacturation" as Agent <<primary>>
actor "Payeur" as Payeur <<primary>>
actor "Employé" as Employe <<primary>>
actor "Système\nEmail" as Email <<secondary>>
actor "Système\nSMS" as SMS <<secondary>>

' Hiérarchie des acteurs
Admin ---|> Chef
Chef ---|> Agent

rectangle "Portail de Facturation Moov Africa" {
  
  ' === CAS D'UTILISATION FONCTIONNELS ===
  
  ' GESTION UTILISATEURS
  usecase "Créer utilisateur" as UC1
  usecase "Modifier statut\nutilisateur" as UC2
  usecase "Réinitialiser\nmot de passe" as UC3
  
  ' GESTION CONTRATS
  usecase "Créer contrat" as UC4
  usecase "Modifier contrat" as UC5
  usecase "Résilier contrat" as UC6
  usecase "Ajouter ligne\ntéléphonique" as UC7
  usecase "Modifier services\nligne" as UC8
  usecase "Affecter employé\nà ligne" as UC9
  
  ' GESTION FACTURATION
  usecase "Publier factures\nPDF" as UC10
  usecase "Annuler facture" as UC11
  usecase "Consulter factures" as UC12
  usecase "Télécharger PDF" as UC13
  usecase "Exporter données" as UC14
  
  ' GESTION TARIFS
  usecase "Gérer forfaits" as UC15
  usecase "Gérer services" as UC16
  
  ' CONSULTATION & RAPPORTS
  usecase "Consulter\nstatistiques" as UC17
  usecase "Consulter audit" as UC18
}

' === RELATIONS ACTEURS → UC FONCTIONNELS ===

' Super Admin
Admin --> UC1
Admin --> UC2
Admin --> UC3
Admin --> UC18

' Chef Facturation
Chef --> UC6
Chef --> UC11

' Agent Facturation
Agent --> UC4
Agent --> UC5
Agent --> UC7
Agent --> UC8
Agent --> UC9
Agent --> UC10
Agent --> UC12
Agent --> UC14
Agent --> UC15
Agent --> UC16
Agent --> UC17

' Payeur
Payeur --> UC12
Payeur --> UC13
Payeur --> UC14
Payeur --> UC17

' Employé
Employe --> UC12
Employe --> UC13

' === RELATIONS ENTRE UC ===

' Relations fonctionnelles
UC12 --> UC13

note right of Admin
  **Hiérarchie :**
  Super Admin > Chef > Agent
  L'héritage donne accès
  aux UC des niveaux inférieurs
  
  **Note :** S'authentifier est obligatoire
  mais n'apparaît pas comme UC fonctionnel
end note

note bottom of UC12
  **UC fonctionnel récurrent**
  Utilisé quotidiennement
  par tous les acteurs
end note

@enduml
```

**Note :** Seuls les cas d'utilisation fonctionnels et récurrents sont représentés. Les actions techniques (authentification, validation, traçage) sont implicites.

---

## 4. Diagrammes détaillés

### 4.1 Publier des factures

**Acteur principal :** Agent Facturation  
**Acteurs secondaires :** Système Email, Système SMS  
**Objectif :** Publier les factures mensuelles des clients depuis des fichiers PDF

```plantuml
@startuml
left to right direction

actor "Agent\nFacturation" as Agent <<primary>>
actor "Système\nEmail" as Email <<secondary>>
actor "Système\nSMS" as SMS <<secondary>>

rectangle "Portail de Facturation" {
  usecase "Publier factures\nPDF" as Main
  usecase "S'authentifier" as Auth
  usecase "Uploader PDF" as UC1
  usecase "Extraire données" as UC2
  usecase "Matcher contrats" as UC3
  usecase "Enregistrer factures" as UC4
  usecase "Envoyer\nnotifications" as UC5
}

Agent --> Main
Main ..> Auth : <<include>>
Main ..> UC1 : <<include>>
Main ..> UC2 : <<include>>
Main ..> UC3 : <<include>>
Main ..> UC4 : <<include>>

UC5 ..> Main : <<extend>>\n{notification activée}

UC5 --> Email
UC5 --> SMS

note right of Main
  **Fonctionnalité complète**
  Toutes les étapes sont obligatoires
  sauf les notifications
end note

note bottom of UC5
  **Point d'extension :** Après enregistrement
  **Condition :** Service notification configuré
end note

@enduml
```

---

### 4.2 Gérer contrats

**Acteur principal :** Agent Facturation  
**Objectif :** Créer et gérer les contrats clients

```plantuml
@startuml
left to right direction

actor "Agent\nFacturation" as Agent <<primary>>

rectangle "Portail de Facturation" {
  usecase "Créer contrat" as UC1
  usecase "Modifier contrat" as UC2
  usecase "Ajouter ligne\ntéléphonique" as UC3
  usecase "Modifier services\nligne" as UC4
  usecase "Affecter employé\nà ligne" as UC5
  usecase "S'authentifier" as Auth
  usecase "Valider données" as Valid
  usecase "Tracer action" as Trace
}

Agent --> UC1
Agent --> UC2
Agent --> UC3
Agent --> UC4
Agent --> UC5

' Obligations communes
UC1 ..> Auth : <<include>>
UC2 ..> Auth : <<include>>
UC3 ..> Auth : <<include>>

UC1 ..> Valid : <<include>>
UC2 ..> Valid : <<include>>
UC3 ..> Valid : <<include>>

UC1 ..> Trace : <<include>>
UC2 ..> Trace : <<include>>
UC5 ..> Trace : <<include>>

note right of Agent
  **Opérations quotidiennes**
  L'agent gère le cycle de vie
  complet des contrats
end note

@enduml
```

---

### 4.3 Résilier contrat

**Acteur principal :** Chef Facturation  
**Objectif :** Résilier définitivement un contrat client

```plantuml
@startuml
left to right direction

actor "Chef\nFacturation" as Chef <<primary>>

rectangle "Portail de Facturation" {
  usecase "Résilier contrat" as Main
  usecase "S'authentifier" as Auth
  usecase "Saisir date\nrésiliation" as UC1
  usecase "Saisir motif" as UC2
  usecase "Clôturer\nfacturation" as UC3
  usecase "Vérifier\npermissions" as Perm
  usecase "Tracer action" as Trace
}

Chef --> Main

Main ..> Auth : <<include>>
Main ..> UC1 : <<include>>
Main ..> UC2 : <<include>>
Main ..> UC3 : <<include>>
Main ..> Perm : <<include>>
Main ..> Trace : <<include>>

note right of Main
  **Action irréversible**
  Réservée au Chef Facturation
  Toutes les étapes obligatoires
end note

@enduml
```

---

### 4.4 Consulter factures

**Acteurs principaux :** Agent, Payeur, Employé  
**Objectif :** Consulter et télécharger les factures selon les droits

```plantuml
@startuml
left to right direction

actor "Agent\nFacturation" as Agent <<primary>>
actor "Payeur" as Payeur <<primary>>
actor "Employé" as Employe <<primary>>

rectangle "Portail de Facturation" {
  usecase "Consulter factures" as Main
  usecase "S'authentifier" as Auth
  usecase "Lister factures" as UC1
  usecase "Filtrer" as UC2
  usecase "Voir détails" as UC3
  usecase "Télécharger PDF" as UC4
  usecase "Exporter données" as UC5
  usecase "Vérifier droits" as Perm
}

Agent --> Main
Payeur --> Main
Employe --> Main

Main ..> Auth : <<include>>
Main ..> UC1 : <<include>>
Main ..> Perm : <<include>>

UC2 ..> UC1 : <<extend>>\n{filtrage demandé}

UC1 --> UC3
UC3 --> UC4

Agent --> UC5
Payeur --> UC5

note right of Perm
  **Contrôle d'accès :**
  - Agent : toutes factures
  - Payeur : ses contrats
  - Employé : sa ligne
end note

@enduml
```

---

### 4.5 Gérer utilisateurs

**Acteur principal :** Super Admin, Chef Facturation  
**Objectif :** Créer et administrer les comptes utilisateurs

```plantuml
@startuml
left to right direction

actor "Super Admin" as Admin <<primary>>
actor "Chef\nFacturation" as Chef <<primary>>
actor "Système\nEmail" as Email <<secondary>>

' Hiérarchie
Admin ---|> Chef

rectangle "Portail de Facturation" {
  usecase "Créer utilisateur" as UC1
  usecase "Modifier statut\nutilisateur" as UC2
  usecase "Réinitialiser\nmot de passe" as UC3
  usecase "Consulter audit" as UC4
  usecase "S'authentifier" as Auth
  usecase "Vérifier\npermissions" as Perm
  usecase "Envoyer credentials" as Cred
}

Admin --> UC1
Chef --> UC1

Admin --> UC2
Chef --> UC2

Admin --> UC3
Chef --> UC3

Admin --> UC4

UC1 ..> Auth : <<include>>
UC2 ..> Auth : <<include>>
UC3 ..> Auth : <<include>>

UC1 ..> Perm : <<include>>
UC2 ..> Perm : <<include>>

UC1 ..> Cred : <<include>>
UC3 ..> Cred : <<include>>

Cred --> Email

note bottom of Perm
  **Hiérarchie :**
  - Admin : tous utilisateurs
  - Chef : agents créés par lui
end note

@enduml
```

---

## 5. Descriptions textuelles

### 5.1 UC04 - Publier factures

#### Partie 1 : Identification

| Élément | Valeur |
|---------|--------|
| **Titre** | Publier factures |
| **Résumé** | L'agent de facturation publie les factures mensuelles à partir de fichiers PDF fournis par le système de billing |
| **Acteur principal** | Agent Facturation |
| **Acteurs secondaires** | Système Email, Système SMS |
| **Date** | 06/08/2026 |
| **Version** | 1.0 |

#### Partie 2 : Scénarios

**Préconditions :**
- L'agent est authentifié
- Les fichiers PDF sont disponibles
- Les contrats existent en base

**Scénario nominal :**
1. L'agent sélectionne le fichier PDF à publier
2. Le système extrait les métadonnées des factures
3. Le système associe chaque facture à son contrat
4. Le système enregistre les factures en base
5. Le système stocke les fichiers PDF
6. Le système affiche un récapitulatif de la publication

**Scénarios alternatifs :**
- **A1. Notifications activées**
  - Point d'extension : Après étape 6
  - Le système envoie des notifications par email
  - Le système envoie des notifications par SMS
  - Retour au scénario nominal

**Scénarios d'exception :**
- **E1. Aucun contrat trouvé**
  - Le système affiche un message d'erreur
  - L'agent peut corriger et réessayer
- **E2. PDF déjà publié**
  - Le système refuse la publication (évite doublon)
  - Fin du cas d'utilisation

**Postconditions :**
- Les factures sont enregistrées en base
- Les PDF sont stockés
- Les clients peuvent consulter leurs factures
- Les notifications sont envoyées (si activées)

#### Partie 3 : Exigences non fonctionnelles

- **Performance :** Traiter un PDF de 500 factures en moins de 2 minutes
- **Sécurité :** Vérifier l'authenticité du PDF avant traitement
- **Fiabilité :** Aucune perte de données en cas d'échec partiel
- **Interface :** Progress bar durant le traitement

---

### 5.2 UC05 - Consulter factures

#### Partie 1 : Identification

| Élément | Valeur |
|---------|--------|
| **Titre** | Consulter factures |
| **Résumé** | Les utilisateurs consultent leurs factures selon leurs permissions |
| **Acteurs principaux** | Agent Facturation, Payeur, Employé |
| **Date** | 06/08/2026 |
| **Version** | 1.0 |

#### Partie 2 : Scénarios

**Préconditions :**
- L'utilisateur est authentifié
- Des factures existent pour cet utilisateur

**Scénario nominal :**
1. L'utilisateur accède à la liste des factures
2. Le système affiche les factures selon les permissions
   - Agent : toutes les factures
   - Payeur : factures de ses contrats
   - Employé : sa facture uniquement
3. L'utilisateur sélectionne une facture
4. Le système affiche les détails
5. L'utilisateur peut télécharger le PDF

**Scénarios alternatifs :**
- **A1. Export des données**
  - L'agent ou le payeur demande un export
  - Le système génère un fichier CSV ou Excel
  - Le système lance le téléchargement

**Scénarios d'exception :**
- **E1. Aucune facture disponible**
  - Le système affiche un message informatif
  - Fin du cas d'utilisation

**Postconditions :**
- L'utilisateur a consulté ses factures
- Le téléchargement PDF est effectué (si demandé)

---

## 6. Règles UML

### 6.1 Relations

| Relation | Notation | Signification | Direction |
|----------|----------|---------------|-----------|
| **Association** | `-->` | Communication simple | Acteur → UC |
| **Include** | `..> <<include>>` | Sous-fonction obligatoire | Base → Inclus |
| **Extend** | `..> <<extend>>` | Sous-fonction optionnelle | Extension → Base |
| **Généralisation** | `---|>` | Héritage/Spécialisation | Spécifique → Général |

### 6.2 Règles appliquées

✅ **DO (Bonnes pratiques) :**
- Nommer avec verbe à l'infinitif
- Définir clairement les limites du système
- Distinguer acteurs principal/secondaire
- Utiliser `<<include>>` pour fonctions communes obligatoires
- Utiliser `<<extend>>` pour comportements optionnels
- Ajouter descriptions textuelles pour UC importants

❌ **DON'T (Erreurs à éviter) :**
- Trop de détails techniques
- Décomposition hiérarchique excessive
- Confondre `<<include>>` et `<<extend>>`
- Surcharger le diagramme
- Oublier de définir les limites

---

**FIN DU DOCUMENT**

