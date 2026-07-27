# Changelog - Projet Moov Africa e-Billings

## [24/07/2026] - Refonte complète de la page Simulation avec double type de client

### ✨ Nouvelle fonctionnalité : Simulation adaptée selon le type de client

La page Simulation a été entièrement refondue pour proposer **2 modes de simulation distincts** :

#### 🎯 Mode 1 : Client HYBRIDE (HYB)
- **Facturation basée sur l'historique de consommation**
- L'utilisateur sélectionne uniquement les **services optionnels** qu'il souhaite ajouter
- La consommation de base (voix, SMS, data) est calculée automatiquement selon l'historique
- Interface simplifiée : accordéon des services avec sélection d'options

#### 💰 Mode 2 : Client OPEN (OP) - Postpayé
- **Facturation prévisionnelle** où l'utilisateur entre ses prévisions
- 3 champs de saisie :
  * Minutes d'appel prévues
  * Nombre de SMS prévus
  * Volume de data prévu (en Go)
- Affichage des **tarifs unitaires** en vigueur (FCFA/min, FCFA/SMS, FCFA/Go)
- **Aperçu en temps réel** du montant sous chaque champ
- **Total global** affiché en orange avec mise à jour instantanée
- Services optionnels également disponibles
- Calcul : `(voix × tarif_minute) + (SMS × tarif_sms) + (data × tarif_go) + services`

---

### 🎨 Nouvelle Interface

#### Écran de sélection du type de client
- 2 grandes cartes interactives :
  * **Client HYBRIDE** (icône cube, couleur bleue)
  * **Client OPEN** (icône dollar, couleur orange)
- Animations au survol :
  * Élévation de la carte (translateY -4px)
  * Rotation et agrandissement de l'icône
  * Fond dégradé selon le type
- Design moderne et épuré
- Responsive : 2 colonnes desktop → 1 colonne mobile

#### Formulaire de simulation
- **En-tête dynamique** : affiche le type de client sélectionné
- **Bouton "Changer de type"** : retour à l'écran de sélection sans perte de contexte
- **Formulaire adapté** selon le type :
  * HYBRIDE : accordéon des services uniquement
  * OPEN : champs de saisie + tarifs + aperçu temps réel + services
- **Résultat détaillé** :
  * Pour OPEN : répartition par poste (Appels, SMS, Data, Services)
  * Pour HYBRIDE : liste des services sélectionnés
  * Note explicative différente selon le type

---

### 🔧 Modifications techniques

#### Fichiers modifiés

**1. `Front/src/pages/simulation/Simulation.jsx`**
- Ajout de l'état `typeClient` : `''`, `'HYB'`, ou `'OP'`
- Nouvelle fonction `handleSubmitHybride()` pour simulation HYBRIDE
- Nouvelle fonction `handleSubmitOpen()` pour simulation OPEN avec calcul tarifaire
- Nouvelle fonction `handleReset()` pour réinitialisation complète
- Logique conditionnelle :
  * Si `typeClient === ''` → Écran de sélection
  * Si `typeClient === 'HYB'` → Simulation HYBRIDE
  * Si `typeClient === 'OP'` → Simulation OPEN
- Calcul temps réel pour OPEN :
  ```javascript
  montantAppels = minutes × tarif_minute
  montantSms = sms × tarif_sms
  montantData = dataGo × tarif_go
  montantTotal = montantAppels + montantSms + montantData + services
  ```

**2. `Front/src/pages/simulation/Simulation.css`**
- Nouveaux styles pour l'écran de sélection :
  * `.type-client-selection` : grille 2 colonnes
  * `.type-client-card` : cartes interactives
  * `.type-client-card--hyb` : variante bleue
  * `.type-client-card--op` : variante orange
  * `.type-client-icon` : conteneur icône avec dégradé
  * `.type-client-title` : titre coloré selon type
  * `.type-client-badge` : badge de type
- Animations fluides (0.25s ease)
- Responsive mobile (< 768px)

---

### ✅ Fonctionnalités implémentées

#### Client HYBRIDE
- ✅ Écran de sélection avec design moderne
- ✅ Formulaire avec accordéon des services
- ✅ Sélection d'une option par service maximum
- ✅ Badge du nombre de services sélectionnés
- ✅ Calcul du montant total des services
- ✅ Affichage détaillé du résultat
- ✅ Bouton de retour vers la sélection
- ✅ Réinitialisation complète

#### Client OPEN
- ✅ Écran de sélection identique
- ✅ Affichage des tarifs unitaires en vigueur (encadré bleu)
- ✅ 3 champs de saisie numériques (voix, SMS, data)
- ✅ Aperçu orange en temps réel sous chaque champ
- ✅ Accordéon des services optionnels (comme HYBRIDE)
- ✅ Aperçu du total global en temps réel (encadré orange)
- ✅ Calcul détaillé par poste de consommation
- ✅ Affichage du résultat avec répartition complète
- ✅ Note explicative adaptée
- ✅ Bouton de retour vers la sélection
- ✅ Réinitialisation complète

#### Commun aux 2 modes
- ✅ Changement de type sans rechargement de page
- ✅ Design cohérent avec les couleurs Moov (bleu #002a7a, orange #e05500)
- ✅ Responsive mobile optimisé
- ✅ Animations fluides et naturelles
- ✅ Messages d'erreur clairs et contextuels
- ✅ Validation des formulaires
- ✅ Accessibilité (labels, contraste, focus)

---

### 📊 Validation et messages

#### Client HYBRIDE
- ❌ Erreur : "Veuillez sélectionner au moins un service."
- ✅ Succès : Affichage du résultat avec liste des services

#### Client OPEN
- ❌ Erreur : "Veuillez entrer au moins une consommation prévue ou sélectionner un service."
- ✅ Succès : Affichage du résultat avec répartition détaillée

---

### 🚀 Comment tester

1. Démarrer le frontend : `cd Front && npm start`
2. Accéder à : `http://localhost:3000/simulation`
3. **Test HYBRIDE** :
   - Cliquer sur "Client HYBRIDE"
   - Ouvrir l'accordéon "Services"
   - Sélectionner 2-3 services
   - Cliquer sur "Calculer l'estimation"
   - Vérifier le résultat
4. **Test OPEN** :
   - Cliquer sur "← Changer de type"
   - Cliquer sur "Client OPEN (Postpayé)"
   - Entrer : 120 minutes, 50 SMS, 5 Go
   - Observer les aperçus en temps réel
   - Ajouter 1-2 services optionnels
   - Observer l'aperçu du total global
   - Cliquer sur "Calculer l'estimation"
   - Vérifier la répartition détaillée
5. **Test changement de type** :
   - Vérifier que le formulaire se réinitialise correctement
   - Vérifier que l'animation de transition est fluide

---

### 📝 Documentation créée

- **`SIMULATION_DOUBLE_TYPE.md`** : Documentation complète avec captures d'écran ASCII, diagrammes, et guide technique

---

### 🔮 Améliorations futures possibles

1. **Persistance** : Sauvegarder le type client dans localStorage
2. **Backend** : Endpoints `/simulations/hybride` et `/simulations/open` pour calcul serveur
3. **Historique** : Intégration de l'historique réel pour HYBRIDE
4. **Graphiques** : Diagramme circulaire de répartition des coûts
5. **Export** : Téléchargement PDF et envoi email
6. **Recommandations** : Suggestions de forfaits selon les prévisions

---

## [22/07/2026] - Harmonisation Frontend/Backend

### ✅ Modifications effectuées

#### 1. Configuration CORS (settings.py)
**Avant :**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
```

**Après :**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
```

**Raison :** Le frontend React tourne sur le port 3000, pas 5173. Les deux ports sont conservés pour compatibilité.

---

#### 2. Cycles de facturation (billing/models.py)
**Avant :**
```python
class CycleFacturation(models.TextChoices):
    HYB1 = 'HYB1', 'Hybride 1'
    HYB2 = 'HYB2', 'Hybride 2'
    MON1 = 'MON1', 'Mensuel 1'
```

**Après :**
```python
class CycleFacturation(models.TextChoices):
    HYB = 'HYB', 'Hybride'
    OP = 'OP', 'Opérationnel'
```

**Raison :** Harmonisation avec le frontend qui utilise HYB (Hybride) et OP (Opérationnel) dans les formulaires de gestion des comptes.

**Migration créée :** `billing/migrations/0002_alter_line_cycle.py`

**Valeur par défaut :** `HYB` (Hybride)

---

### 📝 Impacts

#### Sur la base de données
- Migration appliquée avec succès
- Les lignes existantes conservent leurs valeurs (ou doivent être mises à jour manuellement)
- Nouveau cycle par défaut : `HYB`

#### Sur l'API
- Endpoints `/api/billing/lines/` acceptent maintenant `cycle: "HYB"` ou `cycle: "OP"`
- Les anciennes valeurs `HYB1`, `HYB2`, `MON1` ne sont plus valides

#### Sur le frontend
- Formulaires de création/modification de lignes compatibles
- Formulaire de création de comptes (admin) compatible
- Champ "Cycle de facturation" affiche correctement HYB et OP

---

### ⚠️ Actions requises

1. **Si des données de test existent** : mettre à jour manuellement les cycles dans la base de données
   ```sql
   UPDATE lines SET cycle = 'HYB' WHERE cycle IN ('HYB1', 'HYB2');
   UPDATE lines SET cycle = 'OP' WHERE cycle = 'MON1';
   ```

2. **Tester les endpoints** :
   - Création de ligne avec cycle HYB
   - Création de ligne avec cycle OP
   - Modification du cycle d'une ligne existante

3. **Vérifier le frontend** :
   - Formulaire création compte (admin) : sélection HYB/OP
   - Formulaire attribution lignes : affichage correct des cycles
   - Dashboard : affichage des informations de cycle

---

### 🎯 Prochaines étapes recommandées

1. **Ajouter le champ cycle_facturation au modèle User**
   - Pour PAYEUR et EMPLOYE uniquement
   - Permet de stocker le cycle directement sur le compte

2. **Créer les modèles manquants**
   - Package (forfaits)
   - Service (services optionnels)
   - Simulation (historique)
   - Publication (historique agent)

3. **Implémenter les endpoints manquants**
   - CRUD forfaits et services
   - Simulation de facturation
   - Gestion des comptes utilisateurs
   - Attribution lignes aux payeurs

4. **Ajouter les permissions par rôle**
   - Actuellement : seulement IsAuthenticated
   - Nécessaire : permissions granulaires (admin, agent, payeur, employé)
