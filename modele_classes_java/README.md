# 📦 Modèle de Classes Java pour PowerDesigner

## 📋 Contenu du package

Ce dossier contient **26 fichiers Java** représentant le modèle de classes UML du Portail de Facturation Moov Africa Togo.

### Structure

```
modele_classes_java/
├── README.md (ce fichier)
│
├── 📂 Package: com.moov.facturation.utilisateurs
│   ├── User.java (15 classes)
│   ├── StatusHistory.java
│   ├── RoleChoices.java (enum)
│   └── StatusChoices.java (enum)
│
├── 📂 Package: com.moov.facturation.contrats
│   ├── Commercial.java
│   ├── Company.java
│   ├── Line.java
│   ├── AuditContrat.java
│   ├── CategorieClient.java (enum)
│   ├── StatutFacturation.java (enum)
│   ├── ModeReglement.java (enum)
│   ├── CycleFacturation.java (enum)
│   └── TypeAction.java (enum)
│
├── 📂 Package: com.moov.facturation.facturation
│   ├── Invoice.java
│   ├── NotificationFacture.java
│   ├── HistoriqueFacturation.java
│   ├── Publication.java
│   ├── StatutFacture.java (enum)
│   ├── TypeActionFacturation.java (enum)
│   ├── Canal.java (enum)
│   └── Statut.java (enum)
│
└── 📂 Package: com.moov.facturation.catalogue
    ├── Package.java
    ├── Service.java
    ├── TarifService.java
    ├── Cycle.java
    ├── TypeForfait.java (enum)
    └── TypeService.java (enum)
```

---

## 🔧 Import dans PowerDesigner

### Méthode 1 : Reverse Engineering Java (Recommandée)

1. **Ouvrir PowerDesigner**
   - Lancer PowerDesigner
   - Créer un nouveau "Object-Oriented Model" (OOM)

2. **Lancer le Reverse Engineering**
   - Menu : `File` → `Reverse Engineer` → `Java...`
   - Ou raccourci : `Ctrl + R`

3. **Configurer le Reverse Engineering**
   - **Step 1 - Source Selection** :
     - Cliquer sur le bouton `...` (Browse)
     - Sélectionner **TOUS** les fichiers `.java` de ce dossier
     - Ou sélectionner le dossier entier `modele_classes_java/`
   
   - **Step 2 - Options** :
     - ☑ Generate associations from attributes
     - ☑ Create packages from file structure
     - ☑ Import comments as notes
     - Cliquer sur `Next`

4. **Lancer l'import**
   - Cliquer sur `Finish`
   - PowerDesigner va analyser les fichiers et générer le diagramme

5. **Résultat**
   - Les 15 classes et 9 enumerations seront importées
   - Les packages seront créés automatiquement
   - Les relations (List<>, associations) seront transformées en liens UML

---

### Méthode 2 : Import par Eclipse/IntelliJ (Alternative)

Si la méthode directe ne fonctionne pas :

1. **Créer un projet Java temporaire**
   - Créer un projet Java dans Eclipse ou IntelliJ IDEA
   - Copier tous les fichiers `.java` dans le projet

2. **Compiler le projet**
   - S'assurer que le projet compile sans erreur
   - PowerDesigner préfère les fichiers `.class` pour un reverse engineering plus précis

3. **Reverse Engineering depuis les .class**
   - Dans PowerDesigner : `File` → `Reverse Engineer` → `Java...`
   - Sélectionner les fichiers `.class` du répertoire `bin/` ou `out/`

---

### Méthode 3 : Import XMI (Si disponible)

Si vous avez l'option XMI dans PowerDesigner :

1. Utiliser un outil comme IntelliJ IDEA pour générer un fichier XMI
2. Importer le XMI dans PowerDesigner : `File` → `Import` → `XMI...`

---

## ⚙️ Configuration PowerDesigner recommandée

Après l'import, pour optimiser le diagramme :

### 1. Organiser les classes par package

- Activer l'affichage par package : `Tools` → `Display Preferences` → `Package`
- Les 4 packages seront visibles :
  - `utilisateurs`
  - `contrats`
  - `facturation`
  - `catalogue`

### 2. Configurer l'affichage des attributs

- Clic droit sur le diagramme → `Display Preferences`
- Onglet `Class` :
  - ☑ Attributes
  - ☑ Attribute types
  - ☑ Attribute visibility
  - ☐ Attribute default values (optionnel)

### 3. Configurer l'affichage des méthodes

- Onglet `Class` :
  - ☑ Operations
  - ☑ Operation parameters
  - ☑ Operation visibility

### 4. Générer les associations automatiques

- Menu : `Tools` → `Generate Associations from Attributes`
- PowerDesigner va transformer les attributs de type `List<>` en associations UML

---

## 📊 Statistiques du modèle importé

Après l'import, vous devriez avoir :

| Type | Nombre | Détails |
|------|--------|---------|
| **Classes** | 15 | User, Company, Line, Invoice, Package, etc. |
| **Enumerations** | 11 | RoleChoices, StatutFacture, CategorieClient, etc. |
| **Packages** | 4 | utilisateurs, contrats, facturation, catalogue |
| **Associations** | ~17 | Relations entre classes |
| **Attributs** | 67 | Total simplifié (uniquement essentiels) |
| **Méthodes** | 8 | Méthodes principales métier |

---

## 🔍 Vérification de l'import

### Checklist après import

- [ ] Les 15 classes sont présentes
- [ ] Les 11 enumerations sont présentes
- [ ] Les 4 packages sont créés
- [ ] Les attributs de type `List<>` sont transformés en associations
- [ ] Les cardinalités sont correctes (1, 0..1, 0..*, etc.)
- [ ] Les types des attributs sont corrects (String, Integer, Real, Boolean, Date)
- [ ] Les méthodes principales sont présentes
- [ ] Les commentaires JavaDoc sont importés comme notes

---

## 🛠️ Résolution de problèmes courants

### Problème 1 : Les associations ne sont pas créées

**Solution :**
- Après l'import, aller dans `Tools` → `Generate Associations from Attributes`
- Sélectionner toutes les classes
- Cocher `Generate associations from collection types`

### Problème 2 : Les types ne sont pas reconnus

**Solution :**
- Vérifier que Java est configuré dans PowerDesigner
- Menu : `Database` → `Configure Model Options` → `Java`

### Problème 3 : Les packages ne sont pas créés

**Solution :**
- Lors du reverse engineering, cocher `Create packages from file structure`
- Ou créer manuellement les 4 packages et déplacer les classes

### Problème 4 : Erreur "Invalid Java syntax"

**Solution :**
- Tous les fichiers Java fournis sont syntaxiquement corrects
- Vérifier que vous utilisez PowerDesigner 16.x ou supérieur
- Essayer la méthode 2 (via Eclipse/IntelliJ)

---

## 📝 Notes importantes

1. **Types Java → Types UML**
   - Les types Java (`String`, `Integer`, `Double`, `Boolean`, `Date`) correspondent aux types UML standard
   - PowerDesigner fait la conversion automatiquement

2. **Relations**
   - Les attributs de type `List<T>` deviennent des associations avec cardinalité `0..*`
   - Les attributs de type objet simple deviennent des associations avec cardinalité `0..1` ou `1`

3. **Enumerations**
   - Les enums Java sont importées comme des stéréotypes `<<enumeration>>`
   - Les valeurs sont importées comme des "literals"

4. **Commentaires**
   - Les commentaires JavaDoc (`/** ... */`) sont importés comme notes UML
   - Les commentaires simples (`//`) ne sont pas importés

---

## 📚 Documentation complémentaire

Pour plus de détails sur le modèle :

- **Diagramme de classes complet** : `../DIAGRAMME_CLASSES.md`
- **Diagramme PlantUML** : `../DIAGRAMME_CLASSES_PLANTUML.puml`
- **Diagrammes de cas d'utilisation** : `../DIAGRAMMES_CAS_UTILISATION_V3.md`
- **Code source Django** :
  - `../Back/accounts/models.py` (modèle User)
  - `../Back/billing/models.py` (modèles métier)

---

## ✅ Import réussi !

Si vous avez suivi ces étapes, vous devriez maintenant avoir un diagramme de classes UML complet et exploitable dans PowerDesigner.

**Bon courage pour votre projet de fin d'année ! 🎓**

---

**Auteur :** Benoit BANLEPO Mintre  
**Formation :** GLSI-A  
**Date :** Août 2026  
**Version :** 1.0
