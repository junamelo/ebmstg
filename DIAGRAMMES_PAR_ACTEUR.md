# 📊 Diagrammes de Cas d'Utilisation par Acteur
## Portail de Facturation Moov Africa Togo

**Version :** 1.0  
**Date :** 9 août 2026  
**Auteur :** Benoit BANLEPO Mintre

---

## Table des matières

1. [Chef & Agent Facturation (avec héritage)](#1-chef--agent-facturation)
2. [Super Admin](#2-super-admin)
3. [Payeur](#3-payeur)
4. [Employé](#4-employé)
5. [Commercial](#5-commercial)

---

## 1. Chef & Agent Facturation

### Principe de l'héritage

**Agent Facturation** hérite de tous les cas d'utilisation du **Chef Facturation**.
Le Chef a des UC supplémentaires (administration, supervision).

```plantuml
@startuml
left to right direction

' === ACTEURS AVEC HÉRITAGE ===
actor "Chef\nFacturation" as Chef
actor "Agent\nFacturation" as Agent

' Héritage : Agent hérite de Chef
Chef <|-- Agent

rectangle "Portail de Facturation" {
  
  ' === UC COMMUNS (hérités par Agent) ===
  usecase "Gérer contrats" as UC1
  usecase "Publier factures" as UC2
  usecase "Consulter factures" as UC3
  usecase "Gérer tarifs" as UC4
  
  ' === UC SPÉCIFIQUES CHEF ===
  usecase "Annuler facture" as UC_CHEF1
  usecase "Résilier contrat" as UC_CHEF2
  usecase "Gérer agents" as UC_CHEF3
}

' === RELATIONS AGENT ===
Agent --> UC1
Agent --> UC2
Agent --> UC3
Agent --> UC4

' === RELATIONS CHEF ===
Chef --> UC_CHEF1
Chef --> UC_CHEF2
Chef --> UC_CHEF3

note right of Agent
  **Agent hérite de Chef**
  
  Peut faire :
  ✅ Gérer contrats (créer, modifier)
  ✅ Publier factures
  ✅ Consulter factures
  ✅ Créer tarifs
  
  Ne peut pas :
  ❌ Annuler factures
  ❌ Résilier contrats
  ❌ Gérer agents
end note

note bottom of Chef
  **Chef = Agent + Supervision**
  
  UC supplémentaires :
  ✅ Annuler facture
  ✅ Résilier contrat
  ✅ Gérer agents
end note

@enduml
```

---

### Récapitulatif Chef vs Agent

| Cas d'utilisation | Agent | Chef |
|-------------------|-------|------|
| **Gestion Contrats** |
| Créer contrat | ✅ | ✅ (hérité) |
| Modifier contrat | ✅ | ✅ (hérité) |
| Résilier contrat | ❌ | ✅ **Chef uniquement** |
| Ajouter ligne | ✅ | ✅ (hérité) |
| Modifier services ligne | ✅ | ✅ (hérité) |
| Affecter employé | ✅ | ✅ (hérité) |
| **Gestion Facturation** |
| Publier factures | ✅ | ✅ (hérité) |
| Consulter factures | ✅ | ✅ (hérité) |
| Annuler facture | ❌ | ✅ **Chef uniquement** |
| Télécharger PDF | ✅ | ✅ (hérité) |
| Exporter données | ✅ | ✅ (hérité) |
| **Gestion Tarifs** |
| Créer forfait | ✅ | ✅ (hérité) |
| Créer service | ✅ | ✅ (hérité) |
| Modifier forfait | ❌ | ✅ **Chef uniquement** |
| Modifier service | ❌ | ✅ **Chef uniquement** |
| Activer/Désactiver tarif | ❌ | ✅ **Chef uniquement** |
| **Gestion Utilisateurs** |
| Créer agent | ❌ | ✅ **Chef uniquement** |
| Modifier statut agent | ❌ | ✅ **Chef uniquement** |
| Réinitialiser mot de passe | ❌ | ✅ **Chef uniquement** |
| **Rapports** |
| Consulter statistiques | ✅ | ✅ (hérité) |
| Consulter audit | ❌ | ✅ **Chef uniquement** |

---

## 2. Super Admin

### Diagramme complet

```plantuml
@startuml
left to right direction

' === ACTEUR ===
actor "Super Admin" as Admin
actor "Chef\nFacturation" as Chef

' Héritage : Admin hérite de Chef
Chef <|-- Admin

rectangle "Portail de Facturation" {
  
  ' === UC ADMIN ===
  usecase "Gérer tous\nutilisateurs" as UC1
  usecase "Configurer\nsystème" as UC2
  usecase "Consulter logs" as UC3
  usecase "Gérer permissions" as UC4
}

' === RELATIONS ===
Admin --> UC1
Admin --> UC2
Admin --> UC3
Admin --> UC4

note right of Admin
  **Admin = Chef + Administration**
  
  Hérite de Chef :
  ✅ Gérer contrats
  ✅ Publier factures
  ✅ Annuler factures
  ✅ Résilier contrats
  ✅ Gérer agents
  
  UC supplémentaires :
  ✅ Gérer TOUS utilisateurs
  ✅ Configurer système
  ✅ Consulter logs
  ✅ Gérer permissions
end note

@enduml
```

---

## 3. Payeur & Employé (avec héritage)

### Principe de l'héritage

**Employé** hérite des cas d'utilisation du **Payeur** (consultation factures, téléchargement PDF).
Le Payeur a des UC supplémentaires (contrats, statistiques, export).

```plantuml
@startuml
left to right direction

' === ACTEURS AVEC HÉRITAGE ===
actor "Payeur" as Payeur
actor "Employé" as Employe

' Héritage : Employé hérite de Payeur
Payeur <|-- Employe

rectangle "Portail de Facturation" {
  
  ' === UC COMMUNS (hérités par Employé) ===
  usecase "Consulter factures" as UC1
  usecase "Télécharger PDF" as UC2
  usecase "Modifier son\nmot de passe" as UC3
  
  ' === UC SPÉCIFIQUES PAYEUR ===
  usecase "Consulter ses\ncontrats" as UC_PAY1
  usecase "Consulter ses\nstatistiques" as UC_PAY2
  usecase "Exporter ses\ndonnées" as UC_PAY3
}

' === RELATIONS EMPLOYÉ ===
Employe --> UC1
Employe --> UC2
Employe --> UC3

' === RELATIONS PAYEUR ===
Payeur --> UC_PAY1
Payeur --> UC_PAY2
Payeur --> UC_PAY3

note right of Employe
  **Employé hérite de Payeur**
  
  Peut faire :
  ✅ Voir SA facture uniquement
  ✅ Télécharger SON PDF
  ✅ Modifier son mot de passe
  
  Ne peut pas :
  ❌ Voir les contrats
  ❌ Voir les statistiques
  ❌ Exporter des données
  ❌ Voir d'autres factures
  
  **Portée limitée :**
  L'Employé voit uniquement
  la facture de SA ligne
end note

note bottom of Payeur
  **Payeur = Employé + Gestion**
  
  UC supplémentaires :
  ✅ Voir tous ses contrats
  ✅ Voir toutes ses factures
  ✅ Voir ses statistiques
  ✅ Exporter ses données
  
  **Portée étendue :**
  Le Payeur voit TOUS
  les contrats de son entreprise
end note

@enduml
```

### Récapitulatif Payeur vs Employé

| Cas d'utilisation | Employé | Payeur |
|-------------------|---------|--------|
| **Consultation** |
| Consulter factures | ✅ (SA ligne) | ✅ (hérité + TOUTES ses factures) |
| Télécharger PDF | ✅ | ✅ (hérité) |
| Modifier mot de passe | ✅ | ✅ (hérité) |
| **Gestion (Payeur uniquement)** |
| Consulter contrats | ❌ | ✅ **Payeur uniquement** |
| Consulter statistiques | ❌ | ✅ **Payeur uniquement** |
| Exporter données | ❌ | ✅ **Payeur uniquement** |

**Différence clé :**
- **Employé** : Voit uniquement **SA facture individuelle** (1 ligne)
- **Payeur** : Voit **TOUTES les factures de son entreprise** (tous contrats)

---

## 4. Commercial

### Diagramme complet

```plantuml
@startuml
left to right direction

' === ACTEUR ===
actor "Commercial" as Commercial

rectangle "Portail de Facturation" {
  
  ' === UC COMMERCIAL ===
  usecase "Consulter ses\ncontrats prospectés" as UC1
  usecase "Consulter factures\nde ses contrats" as UC2
  usecase "Consulter ses\nstatistiques" as UC3
  usecase "Télécharger PDF" as UC4
  usecase "Exporter ses\ndonnées" as UC5
}

' === RELATIONS ===
Commercial --> UC1
Commercial --> UC2
Commercial --> UC3
Commercial --> UC4
Commercial --> UC5

note right of Commercial
  **Suivi portefeuille**
  
  Peut faire :
  ✅ Voir SES contrats prospectés
  ✅ Voir factures de SES contrats
  ✅ Voir SES stats (CA, etc.)
  ✅ Télécharger les PDF
  ✅ Exporter SES données
  
  Ne peut pas :
  ❌ Créer/Modifier contrats
  ❌ Publier factures
  ❌ Voir autres commerciaux
  ❌ Gérer tarifs
end note

@enduml
```

---

## 📊 Tableau Récapitulatif Global

| Cas d'utilisation | Admin | Chef | Agent | Commercial | Payeur | Employé |
|-------------------|-------|------|-------|------------|--------|---------|
| **Gestion Utilisateurs** |
| Créer utilisateur (tous rôles) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Créer agent | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Modifier utilisateur | ✅ | ✅* | ❌ | ❌ | ❌ | ❌ |
| Modifier son mot de passe | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Gérer permissions | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Gestion Contrats** |
| Créer contrat | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Modifier contrat | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Résilier contrat | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Consulter ses contrats | - | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Gestion Facturation** |
| Publier factures | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Annuler facture | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Consulter toutes factures | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Consulter ses factures | - | ✅ | ✅ | ✅** | ✅ | ✅*** |
| Télécharger PDF | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Gestion Tarifs** |
| Créer tarif | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Modifier tarif | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Activer/Désactiver | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Rapports & Export** |
| Consulter toutes stats | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Consulter ses stats | - | ✅ | ✅ | ✅ | ✅ | ❌ |
| Exporter toutes données | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Exporter ses données | - | ✅ | ✅ | ✅ | ✅ | ❌ |
| Consulter audit | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Consulter logs système | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

**Légendes :**
- *Chef : uniquement ses agents
- **Commercial : factures de ses contrats prospectés
- ***Employé : uniquement SA facture individuelle

---

## 🔄 Hiérarchies d'Héritage

```
Super Admin
    ↑
    |
Chef Facturation
    ↑
    |
Agent Facturation

Payeur
    ↑
    |
Employé

Commercial (indépendant)
```

**Règle d'héritage :**
L'acteur spécialisé hérite de TOUS les UC de l'acteur général + ses UC spécifiques.

**Hiérarchies dans le système :**

1. **Hiérarchie Administration** : Admin > Chef > Agent
   - Héritage complet des permissions
   - Chaque niveau ajoute des UC de supervision

2. **Hiérarchie Consultation** : Payeur > Employé  
   - Héritage des UC de base (consulter, télécharger)
   - Payeur a UC supplémentaires (contrats, stats, export)
   - **Différence de portée** : Employé (1 ligne) vs Payeur (toute l'entreprise)

3. **Acteur indépendant** : Commercial
   - Aucun héritage
   - UC spécifiques au suivi commercial

---

**FIN DU DOCUMENT**
