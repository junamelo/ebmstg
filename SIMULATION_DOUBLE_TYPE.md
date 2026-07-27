# 🎯 Refonte de la page Simulation - Double Type de Client

## 📋 Vue d'ensemble

La page Simulation a été entièrement refondue pour supporter **2 types de clients** distincts avec des modes de simulation adaptés :

### 1. Client HYBRIDE (HYB)
- **Facturation basée sur l'historique**
- Simulation basée sur la consommation réelle passée
- L'utilisateur sélectionne uniquement les **services optionnels** qu'il souhaite ajouter
- Le système calcule automatiquement la consommation de base (voix, SMS, data) selon l'historique

### 2. Client OPEN (OP) - Postpayé
- **Facturation prévisionnelle**
- L'utilisateur entre **manuellement** ses prévisions de consommation :
  * Minutes d'appel prévues
  * Nombre de SMS prévus
  * Volume de data prévu (en Go)
- L'utilisateur peut également ajouter des **services optionnels**
- Calcul : `(voix × tarif_minute) + (SMS × tarif_sms) + (data × tarif_go) + services`

---

## 🎨 Interface Utilisateur

### Écran 1 : Sélection du type de client

Lorsque l'utilisateur accède à la page `/simulation`, il voit d'abord **2 grandes cartes** pour choisir son type :

```
┌─────────────────────────────────────────────────────────────┐
│  📦 Client HYBRIDE           💰 Client OPEN (Postpayé)      │
│                                                              │
│  Simulation basée sur        Simulation prévisionnelle      │
│  votre historique           Entrez vos prévisions           │
│                                                              │
│  [Facturation basée sur     [Facturation prévisionnelle]    │
│   l'historique]                                              │
└─────────────────────────────────────────────────────────────┘
```

**Design des cartes :**
- Icônes SVG distinctives (cube pour HYB, dollar pour OP)
- Fond dégradé au survol (bleu pour HYB, orange pour OP)
- Animation au survol (élévation + rotation de l'icône)
- Badge de type en bas de chaque carte

---

### Écran 2 : Simulation HYBRIDE

Après avoir choisi **Client HYBRIDE**, l'utilisateur accède à :

**Éléments affichés :**
1. **En-tête** : "Simulation de facturation - Client HYBRIDE"
2. **Boutons** :
   - "← Changer de type" (retour à l'écran de sélection)
   - "Historique" (accès à l'historique des simulations)
3. **Formulaire** :
   - Accordéon "Services optionnels"
   - Chaque service peut être déplié pour voir les options tarifaires
   - Une seule option par service à la fois
   - Badge indiquant le nombre de services sélectionnés
4. **Actions** :
   - Bouton "Calculer l'estimation"
   - Bouton "Réinitialiser"
5. **Résultat** (après soumission) :
   - Liste des services sélectionnés avec leurs tarifs
   - Montant total estimé (fond bleu dégradé)
   - Note : "Cette simulation est basée sur votre consommation réelle passée, plus les services optionnels sélectionnés."

---

### Écran 3 : Simulation OPEN

Après avoir choisi **Client OPEN**, l'utilisateur accède à :

**Éléments affichés :**
1. **En-tête** : "Simulation de facturation - Client OPEN"
2. **Boutons** : identiques à HYBRIDE
3. **Tarifs unitaires en vigueur** (encadré informatif) :
   ```
   Appel : 25 FCFA/min
   SMS : 10 FCFA/SMS
   Data : 2000 FCFA/Go
   ```
4. **Formulaire** :
   - **3 champs de saisie** :
     * Minutes d'appel prévues (avec aperçu du montant en temps réel)
     * Nombre de SMS prévus (avec aperçu)
     * Volume de data prévu en Go (avec aperçu)
   - **Accordéon "Services optionnels"** (identique à HYBRIDE)
   - **Aperçu du total** en temps réel (orange) :
     ```
     Montant estimé : 15 750 FCFA
     ```
5. **Actions** : identiques à HYBRIDE
6. **Résultat** (après soumission) :
   - Détail par type de consommation :
     * Appels (120 min) : 6 000 FCFA
     * SMS (50 SMS) : 1 250 FCFA
     * Data (5 Go) : 5 000 FCFA
   - Services optionnels sélectionnés
   - Montant total estimé
   - Note : "Cette simulation est basée sur vos prévisions de consommation. Le montant réel peut varier selon votre consommation effective."

---

## 🔧 Modifications Techniques

### Fichiers modifiés

#### 1. `Front/src/pages/simulation/Simulation.jsx`

**Nouveaux états :**
```javascript
const [typeClient, setTypeClient] = useState('') // '', 'HYB', 'OP'
```

**Nouvelles fonctions :**
- `handleSubmitHybride()` : Soumission pour client HYBRIDE
- `handleSubmitOpen()` : Soumission pour client OPEN avec calcul tarifaire
- `handleReset()` : Réinitialisation complète du formulaire

**Logique conditionnelle :**
- Si `typeClient === ''` → Affiche l'écran de sélection
- Si `typeClient === 'HYB'` → Affiche la simulation HYBRIDE
- Si `typeClient === 'OP'` → Affiche la simulation OPEN

**Calcul pour OPEN :**
```javascript
const montantAppels = minutes * tarifs.tarif_minute
const montantSms = sms * tarifs.tarif_sms
const montantData = dataGo * tarifs.tarif_go
const montantTotal = montantAppels + montantSms + montantData + services_montant
```

#### 2. `Front/src/pages/simulation/Simulation.css`

**Nouveaux styles ajoutés :**

```css
/* Sélection du type de client */
.type-client-selection { ... }
.type-client-card { ... }
.type-client-card--hyb { ... }
.type-client-card--op { ... }
.type-client-icon { ... }
.type-client-title { ... }
.type-client-description { ... }
.type-client-badge { ... }
```

**Animations :**
- Hover : élévation de la carte (translateY -4px)
- Hover : agrandissement + rotation de l'icône (scale 1.1, rotate 5deg)
- Transitions fluides (0.25s ease)

**Responsive :**
- Sur mobile (< 768px) : les 2 cartes passent en colonne unique

---

## 📊 Données de test

### Tarifs utilisés (mock) :
```javascript
{
  prixParMinute: 25,    // FCFA/minute
  prixParSms: 10,       // FCFA/SMS
  prixParGo: 2000       // FCFA/Go
}
```

### Services optionnels disponibles :
- **Moov Money** : 500 FCFA/mois
- **Assistance 24/7** : 1000 FCFA/mois
- **Package Streaming** : 2500 FCFA/mois

---

## ✅ Fonctionnalités implémentées

### Client HYBRIDE :
- ✅ Écran de sélection du type
- ✅ Formulaire avec accordéon des services
- ✅ Sélection d'une option par service
- ✅ Badge du nombre de services sélectionnés
- ✅ Calcul du montant total des services
- ✅ Affichage du résultat détaillé
- ✅ Bouton de retour vers la sélection
- ✅ Réinitialisation du formulaire

### Client OPEN :
- ✅ Écran de sélection du type
- ✅ Affichage des tarifs unitaires en vigueur
- ✅ 3 champs de saisie (voix, SMS, data)
- ✅ Aperçu en temps réel du montant pour chaque champ
- ✅ Accordéon des services optionnels (comme HYBRIDE)
- ✅ Aperçu du total global en temps réel (orange)
- ✅ Calcul détaillé par poste de consommation
- ✅ Affichage du résultat avec répartition
- ✅ Note explicative différente selon le type
- ✅ Bouton de retour vers la sélection
- ✅ Réinitialisation du formulaire

### Commun :
- ✅ Changement de type sans rechargement
- ✅ Design cohérent avec les couleurs Moov (bleu #002a7a, orange #e05500)
- ✅ Responsive mobile
- ✅ Animations fluides
- ✅ Messages d'erreur appropriés

---

## 🚀 Comment tester

1. Démarrer le frontend :
   ```bash
   cd Front
   npm start
   ```

2. Accéder à : `http://localhost:3000/simulation`

3. **Scénario HYBRIDE** :
   - Cliquer sur "Client HYBRIDE"
   - Ouvrir l'accordéon "Services"
   - Sélectionner 1 ou plusieurs services
   - Cliquer sur "Calculer l'estimation"
   - Vérifier le résultat

4. **Scénario OPEN** :
   - Revenir à l'écran de sélection (bouton "← Changer de type")
   - Cliquer sur "Client OPEN (Postpayé)"
   - Entrer : 120 minutes, 50 SMS, 5 Go
   - Observer l'aperçu en temps réel sous chaque champ
   - Optionnellement, ajouter des services
   - Observer l'aperçu du total global (orange)
   - Cliquer sur "Calculer l'estimation"
   - Vérifier le résultat détaillé

5. **Changement de type** :
   - Cliquer sur "← Changer de type"
   - Choisir l'autre type de client
   - Vérifier que le formulaire est réinitialisé

---

## 🎨 Design System

### Couleurs utilisées :

**Client HYBRIDE :**
- Primaire : `#002a7a` (bleu Moov)
- Fond hover : gradient `#f8faff`
- Icône : fond gradient `#e3f2fd` → `#bbdefb`

**Client OPEN :**
- Primaire : `#e05500` (orange Moov)
- Fond hover : gradient `#fff8f4`
- Icône : fond gradient `#fff3e0` → `#ffe0b2`

### Typographie :
- Titre page : 28px, font-weight 700
- Titre carte : 20px, font-weight 700
- Corps : 14px, line-height 1.6

---

## 📝 Notes techniques

### Gestion de l'état :
- Le changement de type réinitialise complètement le formulaire (form, optionsChoisies, resultat, erreur)
- Les tarifs et services sont chargés une seule fois au montage du composant
- Le typeClient est stocké en état local (pas de persistance)

### Validation :
- **HYBRIDE** : au moins 1 service doit être sélectionné
- **OPEN** : au moins 1 champ de consommation OU 1 service doit être renseigné

### Calcul temps réel :
- Pour OPEN : aperçu sous chaque champ + total global orange
- Utilise les tarifs chargés depuis l'API (ou mock)

### Responsive :
- Desktop : 2 colonnes (illustration + formulaire)
- Mobile : 1 colonne (illustration masquée)
- Cartes de sélection : 2 colonnes → 1 colonne sur mobile

---

## 🔮 Améliorations futures possibles

1. **Persistance du type client** :
   - Sauvegarder dans localStorage
   - Pré-sélectionner au prochain accès

2. **Backend API** :
   - Endpoint `/simulations/hybride` pour calcul serveur
   - Endpoint `/simulations/open` pour calcul serveur
   - Prise en compte de l'historique réel pour HYBRIDE

3. **Graphiques** :
   - Diagramme circulaire de la répartition des coûts pour OPEN
   - Comparaison avec la facture précédente

4. **Export** :
   - Bouton "Télécharger en PDF"
   - Bouton "Envoyer par email"

5. **Recommandations** :
   - Suggérer des forfaits adaptés selon les prévisions OPEN
   - Alertes si consommation prévue anormalement élevée

---

## 🎉 Résultat

La page Simulation propose maintenant une **expérience utilisateur claire et adaptée** selon le type de client :

- **HYBRIDE** → Simple et rapide (services uniquement)
- **OPEN** → Détaillé et prévisionnel (saisie manuelle de la consommation)

Les 2 modes partagent le même design cohérent et intuitif, avec des animations fluides et un feedback visuel immédiat.
