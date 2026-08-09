# 📚 Documentation UML Complète
## Portail de Facturation Moov Africa Togo

**Projet de fin d'année GLSI-A**  
**Étudiant :** Benoit BANLEPO Mintre  
**Date :** Août 2026  
**Version :** 1.0

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Technologies utilisées](#technologies-utilisées)
3. [Documentation UML disponible](#documentation-uml-disponible)
4. [Guide d'utilisation rapide](#guide-dutilisation-rapide)
5. [Structure du projet](#structure-du-projet)

---

## Vue d'ensemble

Ce document centralise toute la documentation UML créée pour le Portail de Facturation Moov Africa Togo, incluant :

- ✅ Diagrammes de cas d'utilisation (Use Case Diagrams)
- ✅ Diagramme de classes (Class Diagram)
- ✅ Modèle Java exportable vers PowerDesigner

---

## Technologies utilisées

### Frontend
- **Runtime & Tools** : Node.js 18+, npm
- **Framework** : React 18
- **Build Tool** : Vite 5
- **Styling** : Tailwind CSS 3
- **HTTP Client** : Axios
- **Animations** : Framer Motion
- **Charts** : Recharts
- **PDF Viewer** : PDF.js

### Backend
- **Langage** : Python 3.10+
- **Framework** : Django 5.0+
- **API** : Django REST Framework 3.14+
- **Base de données** : SQLite 3
- **Authentification** : JWT (djangorestframework-simplejwt)

### Services externes
- **Email** : Gmail SMTP (notifications)
- **SMS** : Vonage API (notifications - mode DÉMO)

---

## Documentation UML disponible

### 1. 📊 Diagrammes de cas d'utilisation

**Fichier :** `DIAGRAMMES_CAS_UTILISATION_V3.md`

**Contenu :**
- Diagramme global avec 18 cas d'utilisation fonctionnels
- 5 diagrammes détaillés par acteur/domaine :
  - Gestion des utilisateurs (Admin)
  - Gestion des contrats (Chef Facturation)
  - Gestion de la facturation (Agent Facturation)
  - Consultation factures (Payeur)
  - Tableau de bord (Chef Facturation)
- Relations `<<include>>` et `<<extend>>` correctement appliquées
- Descriptions textuelles complètes pour chaque UC
- Packages par domaine métier

**Format :** Markdown + PlantUML

**Caractéristiques :**
- Conforme aux règles académiques UML
- Uniquement des cas d'utilisation **fonctionnels récurrents**
- Distinction acteurs primary/secondary
- Hiérarchie des acteurs (Admin > Chef > Agent)

---

### 2. 📐 Diagramme de classes

**Fichier principal :** `DIAGRAMME_CLASSES.md`

**Contenu :**
- 15 classes métier
- 11 enumerations
- 67 attributs (simplifiés, essentiels uniquement)
- 17 associations avec cardinalités
- 4 packages (domaines) :
  - Gestion Utilisateurs
  - Gestion Contrats
  - Gestion Facturation
  - Catalogue Produits

**Format :** Markdown + PlantUML (diagramme intégré)

**Fichier PlantUML autonome :** `DIAGRAMME_CLASSES_PLANTUML.puml`
- Diagramme complet en PlantUML
- 4 packages colorés
- Toutes les relations visualisées
- Notes et légende

---

### 3. ☕ Modèle Java pour PowerDesigner

**Dossier :** `modele_classes_java/`

**Contenu :**
- 26 fichiers Java (15 classes + 11 enums)
- Organisation en 4 packages Java :
  - `com.moov.facturation.utilisateurs`
  - `com.moov.facturation.contrats`
  - `com.moov.facturation.facturation`
  - `com.moov.facturation.catalogue`
- Types UML standard (String, Integer, Double, Boolean, Date)
- Relations via `List<>` pour cardinalités multiples
- Méthodes métier principales
- Getters/Setters complets
- Commentaires JavaDoc

**Documentation incluse :**
- `README.md` : Guide complet d'import dans PowerDesigner (3 méthodes)
- `VERIFICATION.md` : Checklist de vérification et points de contrôle

---

## Guide d'utilisation rapide

### Pour consulter les diagrammes

#### Option 1 : Lecture directe (Markdown)
Les fichiers `.md` contiennent les diagrammes en format texte PlantUML et sont lisibles directement.

#### Option 2 : Visualisation PlantUML
1. Installer l'extension PlantUML dans VS Code
2. Ouvrir les fichiers `.md` ou `.puml`
3. Utiliser la prévisualisation PlantUML

#### Option 3 : Export en image
```bash
# Installer PlantUML
npm install -g node-plantuml

# Générer une image PNG
plantuml DIAGRAMME_CLASSES_PLANTUML.puml
```

---

### Pour importer dans PowerDesigner

**Étapes rapides :**

1. Ouvrir PowerDesigner
2. Créer un nouveau "Object-Oriented Model" (OOM)
3. Menu : `File` → `Reverse Engineer` → `Java...`
4. Sélectionner tous les fichiers `.java` du dossier `modele_classes_java/`
5. Cocher les options :
   - ☑ Generate associations from attributes
   - ☑ Create packages from file structure
   - ☑ Import comments as notes
6. Cliquer sur `Finish`

**Documentation détaillée :** `modele_classes_java/README.md`

---

### Pour modifier les diagrammes

#### Cas d'utilisation
1. Ouvrir `DIAGRAMMES_CAS_UTILISATION_V3.md`
2. Modifier les blocs PlantUML entre ` ```plantuml` et ` ``` `
3. Prévisualiser avec l'extension PlantUML

#### Diagramme de classes
1. **Option A :** Modifier `DIAGRAMME_CLASSES.md` (documentation + diagramme)
2. **Option B :** Modifier `DIAGRAMME_CLASSES_PLANTUML.puml` (diagramme uniquement)
3. **Option C :** Modifier les fichiers Java dans `modele_classes_java/` puis re-générer

---

## Structure du projet

```
Projet de fin d'année GLSI-A BANLEPO Mintre Benoit 2026/
│
├── 📄 DOCUMENTATION_UML_COMPLETE.md (ce fichier)
│
├── 📊 DIAGRAMMES UML
│   ├── DIAGRAMMES_CAS_UTILISATION_V3.md (diagrammes UC + descriptions)
│   ├── DIAGRAMME_CLASSES.md (diagramme de classes + doc)
│   └── DIAGRAMME_CLASSES_PLANTUML.puml (diagramme de classes autonome)
│
├── ☕ MODELE JAVA POUR POWERDESIGNER
│   └── modele_classes_java/
│       ├── README.md (guide d'import PowerDesigner)
│       ├── VERIFICATION.md (checklist de vérification)
│       │
│       ├── 📦 com.moov.facturation.utilisateurs (4 fichiers)
│       │   ├── User.java
│       │   ├── StatusHistory.java
│       │   ├── RoleChoices.java
│       │   └── StatusChoices.java
│       │
│       ├── 📦 com.moov.facturation.contrats (9 fichiers)
│       │   ├── Commercial.java
│       │   ├── Company.java
│       │   ├── Line.java
│       │   ├── AuditContrat.java
│       │   ├── CategorieClient.java
│       │   ├── StatutFacturation.java
│       │   ├── ModeReglement.java
│       │   ├── CycleFacturation.java
│       │   └── TypeAction.java
│       │
│       ├── 📦 com.moov.facturation.facturation (8 fichiers)
│       │   ├── Invoice.java
│       │   ├── NotificationFacture.java
│       │   ├── HistoriqueFacturation.java
│       │   ├── Publication.java
│       │   ├── StatutFacture.java
│       │   ├── TypeActionFacturation.java
│       │   ├── Canal.java
│       │   └── Statut.java
│       │
│       └── 📦 com.moov.facturation.catalogue (6 fichiers)
│           ├── Package.java
│           ├── Service.java
│           ├── TarifService.java
│           ├── Cycle.java
│           ├── TypeForfait.java
│           └── TypeService.java
│
├── 🔧 CODE SOURCE
│   ├── Back/ (Django backend)
│   │   ├── accounts/ (gestion utilisateurs)
│   │   ├── billing/ (gestion contrats et facturation)
│   │   └── moov_backend/ (configuration Django)
│   │
│   └── Front/ (React frontend)
│       └── src/
│           ├── pages/ (pages de l'application)
│           ├── components/ (composants réutilisables)
│           └── services/ (services API)
│
└── 📝 DOCUMENTATION TECHNIQUE
    ├── BACKEND_COMPLET.md
    ├── BACKEND_FINAL_COMPLET.md
    ├── BACKEND_PHASE4_COMPLET.md
    └── BACKEND_PHASE5_COMPLET.md
```

---

## 📊 Statistiques du projet

### Documentation UML

| Type | Fichiers | Détails |
|------|----------|---------|
| **Diagrammes UC** | 1 | 1 global + 5 détaillés, 18 UC fonctionnels |
| **Diagramme de classes** | 2 | Markdown + PlantUML autonome |
| **Modèle Java** | 28 | 26 fichiers Java + 2 docs |
| **Total** | **31 fichiers** | Documentation UML complète |

### Modèle de données

| Élément | Nombre |
|---------|--------|
| Classes | 15 |
| Enumerations | 11 |
| Packages | 4 |
| Attributs | 67 |
| Méthodes | 8 |
| Associations | 17 |

---

## 🎯 Points clés du modèle

### Architecture en couches

Le système suit une architecture en 4 domaines :

1. **Utilisateurs** : Authentification, autorisations, rôles
2. **Contrats** : Gestion des clients et lignes téléphoniques
3. **Facturation** : Génération, publication, notifications
4. **Catalogue** : Forfaits, services, tarification

### Acteurs du système

- **Super Admin** : Administration système complète
- **Chef Facturation** : Gestion contrats, validation factures
- **Agent Facturation** : Publication factures, gestion quotidienne
- **Payeur** : Consultation et téléchargement factures
- **Employé** : Consultation factures individuelles

### Fonctionnalités principales

1. Gestion des utilisateurs avec hiérarchie de rôles
2. Gestion des contrats entreprises multi-lignes
3. Publication automatisée de factures PDF (GLO et SOM)
4. Notifications multi-canal (Email + SMS)
5. Tableau de bord avec statistiques et KPIs
6. Traçabilité complète (audit trails)

---

## 📚 Références

### Normes UML appliquées

- **UML 2.5** : Diagrammes de cas d'utilisation et de classes
- **Règles académiques** : Cas d'utilisation fonctionnels uniquement
- **Relations UML** :
  - `<<include>>` : Obligatoire, systématique, direction Base → Inclus
  - `<<extend>>` : Optionnel, conditionnel, direction Extension → Base
- **Types UML standard** : String, Integer, Real, Boolean, Date

### Documentation technique source

- Modèles Django : `Back/accounts/models.py` et `Back/billing/models.py`
- Documentation backend : `BACKEND_*.md`
- Code source complet disponible dans les dossiers `Back/` et `Front/`

---

## ✅ Checklist de livraison

### Documentation UML

- [x] Diagrammes de cas d'utilisation (global + détaillés)
- [x] Descriptions textuelles des UC principaux
- [x] Diagramme de classes complet
- [x] Modèle Java exportable vers PowerDesigner
- [x] Documentation d'import PowerDesigner
- [x] Fichiers de vérification et validation

### Conformité académique

- [x] Respect des règles UML 2.5
- [x] Cas d'utilisation fonctionnels uniquement
- [x] Relations `<<include>>` et `<<extend>>` correctes
- [x] Types UML standard
- [x] Packages et organisation logique
- [x] Cardinalités précises
- [x] Commentaires et documentation

### Formats livrés

- [x] Markdown (lecture universelle)
- [x] PlantUML (éditable, versionnable)
- [x] Java (importable PowerDesigner)

---

## 🎓 Utilisation pour le rapport de projet

### Sections recommandées

1. **Analyse des besoins**
   - Insérer : Diagrammes de cas d'utilisation
   - Source : `DIAGRAMMES_CAS_UTILISATION_V3.md`

2. **Conception**
   - Insérer : Diagramme de classes
   - Source : `DIAGRAMME_CLASSES.md` ou images générées

3. **Architecture technique**
   - Insérer : Description des packages et couches
   - Source : Ce document, section "Points clés du modèle"

4. **Technologies**
   - Insérer : Stack technique
   - Source : Ce document, section "Technologies utilisées"

### Export des diagrammes en images

Pour intégrer dans un rapport Word/PDF :

```bash
# Générer toutes les images
plantuml DIAGRAMME_CLASSES_PLANTUML.puml
plantuml DIAGRAMMES_CAS_UTILISATION_V3.md
```

Résultat : fichiers PNG dans le même dossier

---

## 🔧 Maintenance et évolution

### Pour ajouter une nouvelle classe

1. Ajouter dans le modèle Django (`Back/billing/models.py` ou `Back/accounts/models.py`)
2. Mettre à jour `DIAGRAMME_CLASSES.md`
3. Mettre à jour `DIAGRAMME_CLASSES_PLANTUML.puml`
4. Créer le fichier Java correspondant dans `modele_classes_java/`

### Pour ajouter un nouveau cas d'utilisation

1. Identifier le domaine métier (utilisateurs, contrats, facturation)
2. Vérifier qu'il s'agit d'une fonctionnalité récurrente
3. Ajouter dans `DIAGRAMMES_CAS_UTILISATION_V3.md`
4. Ajouter la description textuelle complète

---

## 📞 Support et questions

Pour toute question sur la documentation UML :

1. Consulter les README dans chaque dossier
2. Vérifier les fichiers `VERIFICATION.md`
3. Comparer avec les modèles Django sources

---

## 🏆 Résumé

Ce projet dispose d'une **documentation UML complète et professionnelle**, incluant :

✅ Diagrammes de cas d'utilisation conformes aux standards académiques  
✅ Diagramme de classes détaillé et simplifié  
✅ Modèle Java exportable vers PowerDesigner  
✅ Documentation technique complète  
✅ Guides d'utilisation et de vérification  

**Tous les livrables UML sont prêts pour le projet de fin d'année ! 🎉**

---

**Auteur :** Benoit BANLEPO Mintre  
**Formation :** GLSI-A (Génie Logiciel et Systèmes d'Information)  
**Établissement :** [Nom de l'établissement]  
**Date :** Août 2026  
**Version :** 1.0

---

**FIN DU DOCUMENT**
