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

1. [Définition des limites du système](#1-définition-des-limites-du-système)
2. [Identification des acteurs](#2-identification-des-acteurs)
3. [Diagramme global](#3-diagramme-global)
4. [Diagrammes par acteur principal](#4-diagrammes-par-acteur-principal)
5. [Cas d'utilisation détaillés avec descriptions](#5-cas-dutilisation-détaillés-avec-descriptions)
6. [Règles UML appliquées](#6-règles-uml-appliquées)

---

## 1. Définition des limites du système

### Système : **Portail de Facturation Moov Africa Togo**

**Périmètre :**
- ✅ **Dans le système :** Gestion contrats, publication factures, consultation, notifications, gestion utilisateurs
- ❌ **Hors système :** Génération des factures par le système de billing Moov, paiement des factures, système téléphonique

**Frontières :**
```
┌─────────────────────────────────────────────┐
│   PORTAIL DE FACTURATION MOOV AFRICA        │
│                                             │
│  • Gestion des contrats entreprises        │
│  • Publication des factures PDF            │
│  • Consultation des factures               │
│  • Notifications clients                    │
│  • Administration utilisateurs              │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 2. Identification des acteurs

### Acteurs humains

| Acteur | Type | Description | Responsabilités |
|--------|------|-------------|-----------------|
| **Super Admin** | Principal | Administrateur système | Configuration complète, gestion tous utilisateurs |
| **Chef Facturation** | Principal | Responsable facturation | Supervision, gestion agents, validation publications |
| **Agent Facturation** | Principal | Opérateur facturation | Publication factures, gestion contrats quotidienne |
| **Payeur** | Principal | Client entreprise | Consultation ses factures |
| **Employé** | Principal | Salarié de l'entreprise cliente | Consultation sa facture personnelle |

### Acteurs systèmes (secondaires)

| Acteur | Type | Description |
|--------|------|-------------|
| **Système Email** | Secondaire | Service SMTP Gmail |
| **Système SMS** | Secondaire | Service Vonage API |

---

## 1. Diagramme Global

### Vue d'ensemble du système

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Super Admin" as SuperAdmin
actor "Chef Facturation" as Chef
actor "Agent Facturation" as Agent
actor "Payeur" as Payeur
actor "Employé" as Employe

rectangle "Portail de Facturation Moov Africa" {
  
  ' ========== GESTION UTILISATEURS ==========
  package "Gestion Utilisateurs" {
    usecase "Créer utilisateur" as UC1
    usecase "Modifier statut utilisateur" as UC2
    usecase "Réinitialiser mot de passe" as UC3
    usecase "Consulter logs audit" as UC4
  }

  
  ' ========== GESTION CONTRATS ==========
  package "Gestion Contrats" {
    usecase "Créer contrat" as UC5
    usecase "Modifier contrat" as UC6
    usecase "Résilier contrat" as UC7
    usecase "Ajouter ligne" as UC8
    usecase "Modifier services ligne" as UC9
    usecase "Affecter employé à ligne" as UC10
  }
  
  ' ========== GESTION FACTURATION ==========
  package "Gestion Facturation" {
    usecase "Publier factures PDF" as UC11
    usecase "Envoyer notifications" as UC12
    usecase "Consulter factures" as UC13
    usecase "Télécharger facture PDF" as UC14
    usecase "Exporter données" as UC15
    usecase "Annuler facture" as UC16
  }
  
  ' ========== GESTION TARIFS & SERVICES ==========
  package "Gestion Tarifs & Services" {
    usecase "Créer forfait" as UC17
    usecase "Modifier forfait" as UC18
    usecase "Créer service" as UC19
    usecase "Modifier service" as UC20
  }
  
  ' ========== TABLEAUX DE BORD ==========
  package "Tableaux de Bord" {
    usecase "Consulter statistiques" as UC21
    usecase "Voir rapports globaux" as UC22
    usecase "Voir mes factures" as UC23
  }
}

' ========== RELATIONS SUPER ADMIN ==========
SuperAdmin --> UC1
SuperAdmin --> UC2
SuperAdmin --> UC3
SuperAdmin --> UC4
SuperAdmin --> UC5
SuperAdmin --> UC6
SuperAdmin --> UC7
SuperAdmin --> UC11
SuperAdmin --> UC12
SuperAdmin --> UC15
SuperAdmin --> UC16
SuperAdmin --> UC17
SuperAdmin --> UC18
SuperAdmin --> UC19
SuperAdmin --> UC20
SuperAdmin --> UC21
SuperAdmin --> UC22


' ========== RELATIONS CHEF FACTURATION ==========
Chef --> UC1
Chef --> UC2
Chef --> UC3
Chef --> UC5
Chef --> UC6
Chef --> UC7
Chef --> UC8
Chef --> UC9
Chef --> UC11
Chef --> UC12
Chef --> UC15
Chef --> UC16
Chef --> UC17
Chef --> UC18
Chef --> UC19
Chef --> UC20
Chef --> UC21
Chef --> UC22
Chef --> UC4

' ========== RELATIONS AGENT FACTURATION ==========
Agent --> UC5
Agent --> UC6
Agent --> UC8
Agent --> UC9
Agent --> UC10
Agent --> UC11
Agent --> UC13
Agent --> UC14
Agent --> UC15
Agent --> UC17
Agent --> UC19
Agent --> UC21

' ========== RELATIONS PAYEUR ==========
Payeur --> UC13
Payeur --> UC14
Payeur --> UC15
Payeur --> UC23

' ========== RELATIONS EMPLOYÉ ==========
Employe --> UC13
Employe --> UC14
Employe --> UC23

@enduml
```

---


## 2. Cas d'utilisation par acteur

### 2.1 Super Admin

**Responsabilités :** Administration complète du système

```plantuml
@startuml
left to right direction

actor "Super Admin" as SuperAdmin

rectangle "Portail Facturation" {
  usecase "Gérer tous les utilisateurs" as UC1
  usecase "Configurer le système" as UC2
  usecase "Consulter logs de sécurité" as UC3
  usecase "Gérer tous les contrats" as UC4
  usecase "Gérer toutes les factures" as UC5
  usecase "Créer/Modifier tarifs" as UC6
  usecase "Créer/Modifier services" as UC7
  usecase "Exporter toutes données" as UC8
  usecase "Voir statistiques globales" as UC9
  usecase "Publier factures" as UC10
  usecase "Annuler factures" as UC11
}

SuperAdmin --> UC1
SuperAdmin --> UC2
SuperAdmin --> UC3
SuperAdmin --> UC4
SuperAdmin --> UC5
SuperAdmin --> UC6
SuperAdmin --> UC7
SuperAdmin --> UC8
SuperAdmin --> UC9
SuperAdmin --> UC10
SuperAdmin --> UC11

note right of SuperAdmin
  **Permissions :**
  - Toutes les permissions (*)
  - Accès complet au système
  - Gestion de tous les utilisateurs
  - Configuration système
end note

@enduml
```

---

### 2.2 Chef Facturation

**Responsabilités :** Gestion des agents et supervision facturation

```plantuml
@startuml
left to right direction

actor "Chef Facturation" as Chef

rectangle "Portail Facturation" {
  usecase "Créer agents facturation" as UC1
  usecase "Modifier statut agents" as UC2
  usecase "Réinitialiser mot de passe agents" as UC3
  usecase "Publier factures" as UC4
  usecase "Annuler factures" as UC5
  usecase "Gérer contrats" as UC6
  usecase "Résilier contrats" as UC7
  usecase "Créer/Modifier tarifs" as UC8
  usecase "Créer/Modifier services" as UC9
  usecase "Consulter rapports globaux" as UC10
  usecase "Exporter données" as UC11
  usecase "Consulter logs audit" as UC12
}

Chef --> UC1
Chef --> UC2
Chef --> UC3
Chef --> UC4
Chef --> UC5
Chef --> UC6
Chef --> UC7
Chef --> UC8
Chef --> UC9
Chef --> UC10
Chef --> UC11
Chef --> UC12

note right of Chef
  **Permissions :**
  - Gestion des agents uniquement
  - Publication et annulation factures
  - Gestion complète des contrats
  - Création tarifs et services
  - Accès aux rapports globaux
end note

@enduml
```

---


### 2.3 Agent Facturation

**Responsabilités :** Opérations de facturation quotidiennes

```plantuml
@startuml
left to right direction

actor "Agent Facturation" as Agent

rectangle "Portail Facturation" {
  usecase "Créer contrats" as UC1
  usecase "Modifier contrats" as UC2
  usecase "Ajouter lignes" as UC3
  usecase "Modifier services ligne" as UC4
  usecase "Affecter employés" as UC5
  usecase "Publier factures PDF" as UC6
  usecase "Consulter factures" as UC7
  usecase "Télécharger PDF" as UC8
  usecase "Exporter données" as UC9
  usecase "Créer forfaits" as UC10
  usecase "Créer services" as UC11
  usecase "Voir statistiques" as UC12
}

Agent --> UC1
Agent --> UC2
Agent --> UC3
Agent --> UC4
Agent --> UC5
Agent --> UC6
Agent --> UC7
Agent --> UC8
Agent --> UC9
Agent --> UC10
Agent --> UC11
Agent --> UC12

note right of Agent
  **Permissions :**
  - Gestion des contrats
  - Publication de factures
  - Affectation employés
  - Création tarifs et services
  - Consultation factures
end note

@enduml
```

---

### 2.4 Payeur

**Responsabilités :** Consultation et gestion de ses factures

```plantuml
@startuml
left to right direction

actor "Payeur" as Payeur

rectangle "Portail Facturation" {
  usecase "Consulter mes factures" as UC1
  usecase "Télécharger PDF" as UC2
  usecase "Voir détails facture" as UC3
  usecase "Exporter mes données" as UC4
  usecase "Voir mes statistiques" as UC5
  usecase "Consulter historique" as UC6
  usecase "Recevoir notifications" as UC7
}

Payeur --> UC1
Payeur --> UC2
Payeur --> UC3
Payeur --> UC4
Payeur --> UC5
Payeur --> UC6
Payeur --> UC7

note right of Payeur
  **Permissions :**
  - Voir uniquement SES factures
  - Exporter ses propres données
  - Recevoir notifications Email/SMS
  - Consulter son historique
end note

@enduml
```

---


### 2.5 Employé

**Responsabilités :** Consultation de sa propre facture

```plantuml
@startuml
left to right direction

actor "Employé" as Employe

rectangle "Portail Facturation" {
  usecase "Consulter ma facture" as UC1
  usecase "Télécharger mon PDF" as UC2
  usecase "Voir détails ligne" as UC3
  usecase "Voir mes services" as UC4
  usecase "Recevoir notifications" as UC5
}

Employe --> UC1
Employe --> UC2
Employe --> UC3
Employe --> UC4
Employe --> UC5

note right of Employe
  **Permissions :**
  - Voir uniquement SA facture
  - Télécharger son PDF
  - Consulter ses services
  - Recevoir notifications
end note

@enduml
```

---

## 3. Cas d'utilisation principaux détaillés

### 3.1 Publier des factures

**Description :** Publication de factures à partir de PDF téléchargés

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Agent\nFacturation" as Agent
actor "Système\nEmail" as Email
actor "Système\nSMS" as SMS

rectangle "Portail de Facturation Moov Africa" {
  
  usecase "Publier factures" as UC_Main
  
  usecase "Uploader PDF" as UC1
  usecase "Sélectionner type" as UC1a
  usecase "Valider format" as UC1b
  
  usecase "Extraire métadonnées" as UC2
  usecase "Lire numéro facture" as UC2a
  usecase "Lire montants" as UC2b
  usecase "Lire période" as UC2c
  
  usecase "Matcher avec contrats" as UC3
  usecase "Matcher par compte (GLO)" as UC3a
  usecase "Matcher par MSISDN (SOM)" as UC3b
  
  usecase "Créer factures en base" as UC4
  usecase "Stocker PDF" as UC4a
  usecase "Générer numéro unique" as UC4b
  
  usecase "Envoyer notifications" as UC5
  usecase "Notifier par Email" as UC5a
  usecase "Notifier par SMS" as UC5b
  
  usecase "Tracer historique" as UC6
  usecase "S'authentifier" as UC_Auth
  usecase "Gérer erreurs matching" as UC_Error
}

' Relations principales
Agent --> UC_Main
UC_Main ..> UC_Auth : <<include>>

' Étapes du processus principal (séquentielles obligatoires)
UC_Main ..> UC1 : <<include>>
UC_Main ..> UC2 : <<include>>
UC_Main ..> UC3 : <<include>>
UC_Main ..> UC4 : <<include>>
UC_Main ..> UC6 : <<include>>

' Extension optionnelle : notifications
UC5 ..> UC_Main : <<extend>>\n[notification activée]

' Sous-étapes Upload (toutes obligatoires)
UC1 ..> UC1a : <<include>>
UC1 ..> UC1b : <<include>>

' Sous-étapes Extraction (toutes obligatoires)
UC2 ..> UC2a : <<include>>
UC2 ..> UC2b : <<include>>
UC2 ..> UC2c : <<include>>

' Sous-étapes Matching (variantes selon type)
UC3a ..> UC3 : <<extend>>\n[facture globale]
UC3b ..> UC3 : <<extend>>\n[facture individuelle]
UC_Error ..> UC3 : <<extend>>\n[aucun match]

' Sous-étapes Création (toutes obligatoires)
UC4 ..> UC4a : <<include>>
UC4 ..> UC4b : <<include>>

' Sous-étapes Notifications (conditionnelles)
UC5a ..> UC5 : <<extend>>\n[email configuré]
UC5b ..> UC5 : <<extend>>\n[SMS configuré]

UC5a --> Email
UC5b --> SMS

note right of UC_Main
  **Acteur principal :**
  Agent de Facturation
  
  **Préconditions :**
  - Authentifié (<<include>>)
  - Rôle AGENT_FACTURATION
  - Contrats existants en base
  
  **Flux principal :**
  1. Upload (<<include>>)
  2. Extraction (<<include>>)
  3. Matching (<<include>>)
  4. Création (<<include>>)
  5. Trace (<<include>>)
  6. Notification (<<extend>>)
end note

note bottom of UC3
  **Variantes de matching :**
  - GLO : Par compte (<<extend>>)
  - SOM : Par MSISDN (<<extend>>)
  - Une seule variante exécutée
end note

note bottom of UC5
  **Notifications optionnelles :**
  - Email si configuré
  - SMS si configuré
  - Peut fonctionner sans
end note

@enduml
```

---


### 3.2 Gérer les contrats

**Description :** Gestion complète du cycle de vie d'un contrat

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Agent\nFacturation" as Agent
actor "Chef\nFacturation" as Chef

rectangle "Portail de Facturation Moov Africa" {
  
  usecase "Gérer contrats" as UC_Main
  
  usecase "Créer contrat" as UC1
  usecase "Saisir informations" as UC1a
  usecase "Définir services défaut" as UC1b
  usecase "Assigner commercial" as UC1c
  
  usecase "Modifier contrat" as UC2
  usecase "Modifier informations" as UC2a
  usecase "Changer services défaut" as UC2b
  usecase "Changer commercial" as UC2c
  
  usecase "Ajouter ligne" as UC3
  usecase "Saisir MSISDN" as UC3a
  usecase "Définir forfait" as UC3b
  usecase "Hériter services contrat" as UC3c
  
  usecase "Modifier services ligne" as UC4
  
  usecase "Résilier contrat" as UC5
  usecase "Saisir date résiliation" as UC5a
  usecase "Saisir motif" as UC5b
  usecase "Clôturer facturation" as UC5c
  
  usecase "Changer statut facturation" as UC6
  
  usecase "Consulter audit" as UC7
  
  usecase "S'authentifier" as UC_Auth
  usecase "Valider données" as UC_Valid
  usecase "Tracer modifications" as UC_Trace
  usecase "Vérifier permissions" as UC_Perm
}

' Relations principales
Agent --> UC_Main
Chef --> UC_Main

UC_Main ..> UC_Auth : <<include>>

' Cas d'utilisation du menu principal
Agent --> UC1
Agent --> UC2
Agent --> UC3
Agent --> UC4
Agent --> UC7

' Réservé au Chef
Chef --> UC5
Chef --> UC6

' Sous-étapes Création (obligatoires sauf commercial)
UC1 ..> UC1a : <<include>>
UC1 ..> UC1b : <<include>>
UC1c ..> UC1 : <<extend>>\n[commercial disponible]
UC1 ..> UC_Valid : <<include>>
UC1 ..> UC_Trace : <<include>>

' Sous-étapes Modification (variantes optionnelles)
UC2a ..> UC2 : <<extend>>\n[modification infos]
UC2b ..> UC2 : <<extend>>\n[modification services]
UC2c ..> UC2 : <<extend>>\n[modification commercial]
UC2 ..> UC_Valid : <<include>>
UC2 ..> UC_Trace : <<include>>

' Sous-étapes Ajout ligne (toutes obligatoires)
UC3 ..> UC3a : <<include>>
UC3 ..> UC3b : <<include>>
UC3 ..> UC3c : <<include>>
UC3 ..> UC_Valid : <<include>>
UC3 ..> UC_Trace : <<include>>

' Sous-étapes Résiliation (toutes obligatoires)
UC5 ..> UC5a : <<include>>
UC5 ..> UC5b : <<include>>
UC5 ..> UC5c : <<include>>
UC5 ..> UC_Valid : <<include>>
UC5 ..> UC_Trace : <<include>>
UC5 ..> UC_Perm : <<include>>

' Vérifications (toujours obligatoires)
UC6 ..> UC_Trace : <<include>>
UC6 ..> UC_Perm : <<include>>

note right of UC_Main
  **Acteurs :**
  - Agent : CRUD contrats/lignes
  - Chef : + Résiliation + Statut
  
  **Préconditions :**
  - Authentifié (<<include>>)
  - Permissions adéquates
  
  **Flux :**
  - Création/Modif : <<include>>
  - Validation : <<include>>
  - Trace : <<include>>
end note

note bottom of UC2
  **Modification = variantes :**
  Chaque type de modification
  est une extension optionnelle.
  On peut modifier :
  - OU les infos
  - OU les services
  - OU le commercial
end note

note bottom of UC5
  **Résiliation irréversible :**
  Toutes les étapes sont
  obligatoires (<<include>>)
  - Date >= date effet
  - Motif obligatoire
  - Statut → CLOS
  - Plus de facturation
end note

@enduml
```

---


### 3.3 Consulter les factures

**Description :** Consultation et téléchargement de factures selon le rôle

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Agent\nFacturation" as Agent
actor "Payeur" as Payeur
actor "Employé" as Employe

rectangle "Portail de Facturation Moov Africa" {
  
  usecase "Consulter factures" as UC_Main
  
  usecase "Lister factures" as UC1
  usecase "Filtrer par période" as UC1a
  usecase "Filtrer par statut" as UC1b
  usecase "Filtrer par contrat" as UC1c
  
  usecase "Voir détails facture" as UC2
  usecase "Afficher montants" as UC2a
  usecase "Afficher période" as UC2b
  usecase "Voir historique" as UC2c
  
  usecase "Télécharger PDF" as UC3
  
  usecase "Exporter données" as UC4
  usecase "Exporter CSV" as UC4a
  usecase "Exporter Excel" as UC4b
  
  usecase "Voir statistiques" as UC5
  
  usecase "S'authentifier" as UC_Auth
  usecase "Vérifier permissions" as UC_Perm
}

' Relations principales
Agent --> UC_Main
Payeur --> UC_Main
Employe --> UC_Main

UC_Main ..> UC_Auth : <<include>>
UC_Main ..> UC_Perm : <<include>>

' Flux principal
UC_Main ..> UC1 : <<include>>

' Sous-étapes Liste (extensions optionnelles)
UC1a ..> UC1 : <<extend>>\n[filtrage période]
UC1b ..> UC1 : <<extend>>\n[filtrage statut]
UC1c ..> UC1 : <<extend>>\n[filtrage contrat]

' Actions depuis la liste
UC1 --> UC2
UC2 --> UC3

' Sous-étapes Détails (toutes obligatoires)
UC2 ..> UC2a : <<include>>
UC2 ..> UC2b : <<include>>
UC2c ..> UC2 : <<extend>>\n[historique disponible]

' Export (réservé Agent et Payeur)
Agent --> UC4
Payeur --> UC4

UC4a ..> UC4 : <<extend>>\n[format CSV]
UC4b ..> UC4 : <<extend>>\n[format Excel]

' Statistiques
Agent --> UC5
Payeur --> UC5

note right of UC_Main
  **Contrôle d'accès :**
  - Agent : Toutes factures
  - Payeur : Ses contrats
  - Employé : Sa ligne
  
  **Préconditions :**
  - Authentifié (<<include>>)
  - Permissions vérifiées (<<include>>)
  
  **Flux :**
  1. Liste (<<include>>)
  2. Filtres (<<extend>>)
  3. Détails → PDF
end note

note bottom of UC1
  **Filtres optionnels :**
  Les filtres sont des extensions
  car la liste peut s'afficher
  sans aucun filtre appliqué.
end note

note bottom of UC4
  **Formats d'export :**
  Variantes selon besoin :
  - CSV (<<extend>>)
  - Excel (<<extend>>)
  Un seul format à la fois
end note

@enduml
```

---

### 3.4 Gérer les utilisateurs

**Description :** Création et gestion des utilisateurs du système

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Super\nAdmin" as SuperAdmin
actor "Chef\nFacturation" as Chef
actor "Système\nEmail" as Email

rectangle "Portail de Facturation Moov Africa" {
  
  usecase "Gérer utilisateurs" as UC_Main
  
  usecase "Créer utilisateur" as UC1
  usecase "Saisir informations" as UC1a
  usecase "Définir rôle" as UC1b
  usecase "Générer mot de passe" as UC1c
  usecase "Envoyer credentials" as UC1d
  
  usecase "Modifier statut" as UC2
  usecase "Activer" as UC2a
  usecase "Désactiver" as UC2b
  usecase "Suspendre temporairement" as UC2c
  usecase "Bloquer définitivement" as UC2d
  usecase "Définir date fin suspension" as UC2c1
  usecase "Saisir raison" as UC2c2
  
  usecase "Réinitialiser mot de passe" as UC3
  usecase "Générer nouveau MDP" as UC3a
  usecase "Envoyer par email" as UC3b
  
  usecase "Consulter historique" as UC4
  usecase "Voir changements statut" as UC4a
  usecase "Voir actions utilisateur" as UC4b
  
  usecase "S'authentifier" as UC_Auth
  usecase "Vérifier permissions" as UC_Perm
  usecase "Tracer action" as UC_Trace
}

' Relations principales
SuperAdmin --> UC_Main
Chef --> UC_Main

UC_Main ..> UC_Auth : <<include>>
UC_Main --> UC1
UC_Main --> UC2
UC_Main --> UC3
SuperAdmin --> UC4

' Sous-étapes Création (toutes obligatoires)
UC1 ..> UC1a : <<include>>
UC1 ..> UC1b : <<include>>
UC1 ..> UC1c : <<include>>
UC1 ..> UC1d : <<include>>
UC1 ..> UC_Perm : <<include>>
UC1 ..> UC_Trace : <<include>>

UC1d --> Email

' Sous-étapes Modification statut (variantes)
UC2a ..> UC2 : <<extend>>\n[réactivation]
UC2b ..> UC2 : <<extend>>\n[désactivation]
UC2c ..> UC2 : <<extend>>\n[suspension temp]
UC2d ..> UC2 : <<extend>>\n[blocage définitif]
UC2 ..> UC_Perm : <<include>>
UC2 ..> UC_Trace : <<include>>

' Suspension temporaire (obligatoires si suspension)
UC2c ..> UC2c1 : <<include>>
UC2c ..> UC2c2 : <<include>>

' Sous-étapes Réinitialisation MDP (toutes obligatoires)
UC3 ..> UC3a : <<include>>
UC3 ..> UC3b : <<include>>
UC3 ..> UC_Perm : <<include>>
UC3 ..> UC_Trace : <<include>>

UC3b --> Email

' Sous-étapes Historique (variantes)
UC4a ..> UC4 : <<extend>>\n[vue statuts]
UC4b ..> UC4 : <<extend>>\n[vue actions]

note right of UC_Main
  **Hiérarchie permissions :**
  - Super Admin : Tous utilisateurs
  - Chef : Agents créés par lui
  
  **Préconditions :**
  - Authentifié (<<include>>)
  - Permissions OK (<<include>>)
  
  **Traçabilité :**
  - Toutes actions tracées
end note

note bottom of UC2
  **Variantes de statut :**
  Modifier statut peut prendre
  4 formes différentes (<<extend>>)
  Une seule exécutée à la fois :
  - Activer
  - Désactiver  
  - Suspendre (temporaire)
  - Bloquer (définitif)
end note

note bottom of UC2c
  **Si suspension temporaire :**
  Date fin et raison deviennent
  obligatoires (<<include>>)
end note

@enduml
```

---


### 3.5 Affecter employés aux lignes

**Description :** Affectation et gestion des employés sur les lignes téléphoniques

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Agent\nFacturation" as Agent
actor "Système\nEmail" as Email
actor "Système\nSMS" as SMS

rectangle "Portail de Facturation Moov Africa" {
  
  usecase "Gérer affectations\nemployés" as UC_Main
  
  usecase "Affecter employé" as UC1
  usecase "Sélectionner ligne" as UC1a
  usecase "Choisir employé" as UC1b
  usecase "Vérifier disponibilité" as UC1c
  usecase "Créer affectation" as UC1d
  
  usecase "Retirer employé" as UC2
  usecase "Confirmer retrait" as UC2a
  usecase "Supprimer affectation" as UC2b
  
  usecase "Consulter affectations" as UC3
  usecase "Lister par contrat" as UC3a
  usecase "Lister par employé" as UC3b
  
  usecase "Notifier employé" as UC4
  usecase "Envoyer email" as UC4a
  usecase "Envoyer SMS" as UC4b
  
  usecase "S'authentifier" as UC_Auth
  usecase "Valider données" as UC_Valid
  usecase "Tracer modification" as UC_Trace
  usecase "Gérer erreur affectation" as UC_Error
}

' Relations principales
Agent --> UC_Main

UC_Main ..> UC_Auth : <<include>>
UC_Main --> UC1
UC_Main --> UC2
UC_Main --> UC3

' Sous-étapes Affectation (toutes obligatoires)
UC1 ..> UC1a : <<include>>
UC1 ..> UC1b : <<include>>
UC1 ..> UC1c : <<include>>
UC1 ..> UC1d : <<include>>
UC1 ..> UC_Valid : <<include>>
UC1 ..> UC_Trace : <<include>>

' Extensions optionnelles/conditionnelles
UC4 ..> UC1 : <<extend>>\n[notification activée]
UC_Error ..> UC1 : <<extend>>\n[employé déjà affecté]

' Sous-étapes Retrait (toutes obligatoires)
UC2 ..> UC2a : <<include>>
UC2 ..> UC2b : <<include>>
UC2 ..> UC_Trace : <<include>>

' Sous-étapes Consultation (variantes)
UC3a ..> UC3 : <<extend>>\n[vue contrat]
UC3b ..> UC3 : <<extend>>\n[vue employé]

' Sous-étapes Notification (variantes)
UC4a ..> UC4 : <<extend>>\n[email configuré]
UC4b ..> UC4 : <<extend>>\n[SMS configuré]

UC4a --> Email
UC4b --> SMS

note right of UC_Main
  **Acteur :** Agent de Facturation
  
  **Préconditions :**
  - Authentifié (<<include>>)
  - Contrat et ligne existent
  - Employé existe et actif
  
  **Flux principal :**
  1. Sélectionner (<<include>>)
  2. Vérifier (<<include>>)
  3. Créer (<<include>>)
  4. Tracer (<<include>>)
  5. Notifier (<<extend>>)
end note

note bottom of UC1c
  **Validations obligatoires :**
  - Employé existe
  - Statut = ACTIF
  - Rôle = EMPLOYE
  - Pas déjà affecté
  - Ligne disponible
  
  Ces vérifications font partie
  du flux principal (<<include>>)
end note

note bottom of UC4
  **Notification optionnelle :**
  Envoi Email/SMS uniquement
  si service configuré.
  L'affectation fonctionne
  sans notification (<<extend>>)
end note

note bottom of UC3
  **Consultation = variantes :**
  Vue par contrat OU par employé
  Une seule vue à la fois
end note

@enduml
```

---

## 📝 Notes techniques

### Rôles et permissions

| Rôle | Permissions principales |
|------|------------------------|
| **SUPER_ADMIN** | Toutes les permissions (*) |
| **CHEF_FACTURATION** | Gestion agents, publication, annulation, tarifs, rapports |
| **AGENT_FACTURATION** | Gestion contrats, publication, consultation, création tarifs |
| **PAYEUR** | Consultation ses factures uniquement |
| **EMPLOYE** | Consultation sa facture uniquement |

### Statuts des factures

- **BROUILLON** : En cours de création
- **EN_COURS** : Validée mais non publiée
- **VALIDEE** : Prête pour publication
- **PUBLIEE** : Disponible pour le client
- **PAYEE** : Réglée par le client
- **ANNULEE** : Annulée par un chef/admin

### Statuts des contrats

- **ACTIF** : Contrat actif, facturation normale
- **SUSPENDU** : Facturation suspendue temporairement
- **CLOS** : Contrat résilié, plus de facturation
- **EN_ATTENTE** : En attente d'activation

---

## 🎯 Légende PlantUML

### Relations entre acteurs et cas d'utilisation
- `-->` : Association (acteur utilise cas d'utilisation)

### Relations entre cas d'utilisation

#### ✅ **<<include>>** (INCLUSION - OBLIGATOIRE)
```
[Cas de base] ..> [Cas inclus] : <<include>>
```
- **Définition :** Le cas de base a **TOUJOURS BESOIN** du cas inclus
- **Direction :** Du cas de base → vers le cas inclus
- **Exécution :** OBLIGATOIRE, systématique
- **Exemple :** "Publier facture" ..> "S'authentifier" : <<include>>
  - On ne peut pas publier sans s'authentifier

#### 🔀 **<<extend>>** (EXTENSION - OPTIONNELLE)
```
[Cas d'extension] ..> [Cas de base] : <<extend>>\n[condition]
```
- **Définition :** Le cas de base peut fonctionner **SEUL**, enrichi optionnellement
- **Direction :** Du cas d'extension → vers le cas de base
- **Exécution :** CONDITIONNELLE, optionnelle
- **Exemple :** "Envoyer SMS" ..> "Publier facture" : <<extend>>\n[SMS activé]
  - On peut publier sans envoyer de SMS

### 📋 Tableau récapitulatif

| Critère | <<include>> | <<extend>> |
|---------|-------------|------------|
| **Obligatoire** | ✅ OUI - Toujours exécuté | ❌ NON - Conditionnel |
| **Direction flèche** | Base → Inclus | Extension → Base |
| **Dépendance** | Forte (nécessaire) | Faible (optionnel) |
| **Condition** | Aucune | Oui (entre crochets) |
| **Cas de base sans** | ❌ Ne fonctionne pas | ✅ Fonctionne |
| **Usage** | Factorisation comportement commun | Variantes, options, exceptions |

### 💡 Exemples du projet

#### <<include>> (Obligatoire)
- Publier facture ..> S'authentifier : <<include>>
- Créer contrat ..> Valider données : <<include>>
- Toute action ..> Tracer modifications : <<include>>
- Créer utilisateur ..> Générer mot de passe : <<include>>

#### <<extend>> (Optionnel)
- Envoyer Email ..> Publier facture : <<extend>>\n[email configuré]
- Gérer erreur ..> Matcher contrats : <<extend>>\n[aucun match]
- Filtrer par période ..> Lister factures : <<extend>>\n[filtrage actif]
- Suspendre ..> Modifier statut : <<extend>>\n[suspension demandée]

---

**Document généré le :** 06 août 2026  
**Projet :** Portail de Facturation Moov Africa Togo  
**Version :** 2.0 (Corrections <<include>> et <<extend>>)
