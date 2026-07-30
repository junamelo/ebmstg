# Implémentation de la Tarification par Paliers

## 📋 Résumé des modifications

La simulation de facturation a été mise à jour pour utiliser les **paliers de tarification** définis selon les spécifications reçues par email.

---

## 🎯 Nouveau système de tarification

### 📊 **DATA - Tarification par paliers**

| Palier | Volume | Tarif |
|--------|--------|-------|
| 1 | 0 - 1 Go | **Gratuit** (0 F) |
| 2 | 1 - 7 Go | 4 500 F |
| 3 | 7 - 15 Go | 5 000 F |
| 4 | 15 - 35 Go | 9 000 F |
| 5 | 35 - 85 Go | 15 000 F |
| 6 | 85 - 275 Go | 50 000 F |
| 7 | **> 275 Go** | **5 F/Mo** au-delà + **50 000 F** fixe |

#### Exemple de calcul (palier 7) :
```
Volume : 280 Go = 280 000 Mo
Dépassement : 280 000 - 275 000 = 5 000 Mo
Calcul : (5 000 × 5) + 50 000 = 25 000 + 50 000 = 75 000 F
```

---

### 📞 **VOIX - Tarification au pas de 30 secondes**

- **Tarif** : 79 F/minute
- **Pas de facturation** : 30 secondes

#### Règle de calcul :
- **0 - 30s** : Demi-tarif (79 ÷ 2 = 39,50 F)
- **31 - 60s** : Tarif complet (79 F)
- **61 - 90s** : 79 F + 39,50 F = 118,50 F
- **91 - 120s** : 79 F × 2 = 158 F
- Et ainsi de suite...

#### Exemples :
```
Appel de 25s → 39,50 F (demi-tarif)
Appel de 45s → 79 F (tarif complet)
Appel de 1min 20s → 79 F + 39,50 F = 118,50 F
Appel de 1min 40s → 79 F × 2 = 158 F
```

---

### 💬 **SMS - Tarification unitaire**

- **Tarif** : 30 F/unité

```
10 SMS → 10 × 30 = 300 F
50 SMS → 50 × 30 = 1 500 F
```

---

## 🛠️ Fichiers créés/modifiés

### ✅ Nouveau fichier : `tarifsService.js`

**Emplacement** : `Front/src/services/tarifsService.js`

**Fonctions principales** :

```javascript
// Calcul DATA avec paliers
calculerMontantData(volumeGo)

// Calcul VOIX avec pas de 30s
calculerMontantVoix(dureeSecondes)
calculerMontantVoixMinutes(minutes)

// Calcul SMS
calculerMontantSms(nombreSms)

// Fonctions détaillées (pour debug/affichage)
detaillerCalculData(volumeGo)
detaillerCalculVoix(dureeSecondes)

// Récupération des paliers
getPaliersData()
getTarifsVoixSms()
```

---

### ✏️ Fichier modifié : `Simulation.jsx`

**Emplacement** : `Front/src/pages/simulation/Simulation.jsx`

**Changements** :

1. **Import du nouveau service**
   ```javascript
   import { 
     calculerMontantData, 
     calculerMontantVoixMinutes, 
     calculerMontantSms 
   } from '../../services/tarifsService'
   ```

2. **Suppression de l'affichage "Tarifs unitaires"**
   - Retiré la section qui affichait "79 FCFA/min", "30 FCFA/SMS", etc.
   - Car maintenant la tarification est par paliers (DATA) et pas de 30s (VOIX)

3. **Mise à jour du calcul dans `handleSubmitOpen`**
   ```javascript
   // AVANT (tarifs fixes)
   const montantAppels = minutes * tarifs.prixParMinute
   const montantSms = sms * tarifs.prixParSms
   const montantData = dataGo * tarifs.prixParGo
   
   // APRÈS (paliers)
   const montantAppels = calculerMontantVoixMinutes(minutes)
   const montantSms = calculerMontantSms(sms)
   const montantData = calculerMontantData(dataGo)
   ```

4. **Mise à jour de l'aperçu en temps réel**
   - Les hints sous les champs utilisent maintenant les fonctions de calcul par paliers
   - L'aperçu total est calculé avec les vrais tarifs

---

## 🎨 Expérience utilisateur

### Ce que voit l'utilisateur :

#### **Dans la simulation OPEN :**

1. **Saisie de consommation**
   ```
   Minutes d'appel prévues: [120]
   ≈ 9 480 FCFA  ← Calculé automatiquement avec paliers
   
   Nombre de SMS prévus: [50]
   ≈ 1 500 FCFA
   
   Volume data prévu: [10 Go]
   ≈ 5 000 FCFA  ← Palier 7-15 Go appliqué
   ```

2. **Aperçu total**
   ```
   Montant estimé: 15 980 FCFA
   ```

3. **Résultat détaillé**
   ```
   Appels (120 min) : 9 480 FCFA
   SMS (50 SMS) : 1 500 FCFA
   Data (10 Go) : 5 000 FCFA
   ────────────────────────────
   Total : 15 980 FCFA
   ```

---

## 🔍 Logique de calcul détaillée

### **DATA - Algorithme de sélection du palier**

```javascript
function calculerMontantData(volumeGo) {
  // Parcourt tous les paliers
  for (const palier of PALIERS_DATA) {
    // Palier spécial > 275 Go
    if (palier.volumeMax === null && volumeGo > palier.volumeMin) {
      const volumeMo = volumeGo * 1000
      const depassementMo = volumeMo - (palier.volumeMin * 1000)
      return (depassementMo * 5) + 50000
    }
    
    // Paliers standards
    if (volumeGo > palier.volumeMin && volumeGo <= palier.volumeMax) {
      return palier.tarif
    }
  }
  return 0
}
```

### **VOIX - Algorithme par pas de 30s**

```javascript
function calculerMontantVoix(dureeSecondes) {
  let montant = 0
  let tempsRestant = dureeSecondes
  
  // Facturation par tranches de 30s
  while (tempsRestant > 0) {
    if (tempsRestant <= 30) {
      montant += 79 / 2  // Demi-tarif
    } else {
      montant += 79 / 2  // Demi-tarif par tranche
    }
    tempsRestant -= 30
  }
  
  return montant
}
```

### **SMS - Calcul simple**

```javascript
function calculerMontantSms(nombreSms) {
  return nombreSms * 30
}
```

---

## ✅ Tests de validation

### Cas de test DATA :

| Volume | Palier attendu | Montant attendu | ✓ |
|--------|---------------|----------------|---|
| 0.5 Go | 0-1 Go | 0 F | ✓ |
| 5 Go | 1-7 Go | 4 500 F | ✓ |
| 10 Go | 7-15 Go | 5 000 F | ✓ |
| 25 Go | 15-35 Go | 9 000 F | ✓ |
| 50 Go | 35-85 Go | 15 000 F | ✓ |
| 150 Go | 85-275 Go | 50 000 F | ✓ |
| 280 Go | > 275 Go | 75 000 F | ✓ |

### Cas de test VOIX :

| Durée | Calcul | Montant attendu | ✓ |
|-------|--------|----------------|---|
| 25s | 79/2 | 39,50 F | ✓ |
| 45s | 79 | 79 F | ✓ |
| 1min 20s | 79 + 79/2 | 118,50 F | ✓ |
| 2min | 79 × 2 | 158 F | ✓ |

### Cas de test SMS :

| Nombre | Calcul | Montant attendu | ✓ |
|--------|--------|----------------|---|
| 10 | 10 × 30 | 300 F | ✓ |
| 50 | 50 × 30 | 1 500 F | ✓ |
| 100 | 100 × 30 | 3 000 F | ✓ |

---

## 🚀 Prochaines étapes (optionnelles)

### Phase 2 - Affichage détaillé

1. **Modal d'explication des paliers**
   - Bouton "ℹ️ Comment sont calculés les tarifs ?"
   - Tableau des paliers DATA
   - Explication du pas de facturation VOIX

2. **Détails dans les résultats**
   ```
   Data (280 Go)
   Palier : Plus de 275 Go
   Calcul : (5 000 Mo × 5 F/Mo) + 50 000 F = 75 000 F
   ```

3. **Graphiques de paliers**
   - Visualisation des paliers DATA
   - Courbe de tarification

### Phase 3 - Backend

1. **API Django**
   - Endpoint pour récupérer les paliers depuis la BDD
   - Configuration dynamique des paliers

2. **Historisation**
   - Sauvegarder les paliers utilisés pour chaque simulation
   - Traçabilité des changements de tarifs

---

## 📝 Notes importantes

### ⚠️ Différences avec l'ancien système

| Élément | Ancien (tarif fixe) | Nouveau (paliers) |
|---------|-------------------|------------------|
| DATA 10 Go | 10 × prix/Go | 5 000 F (palier) |
| DATA 50 Go | 50 × prix/Go | 15 000 F (palier) |
| DATA 280 Go | 280 × prix/Go | 75 000 F (formule) |
| VOIX 1min 20s | 1,33 × 79 | 118,50 F (pas 30s) |

### ✅ Avantages du nouveau système

1. **Plus juste** : Tarification progressive pour la DATA
2. **Plus réaliste** : Pas de 30s pour la VOIX comme dans la vraie vie
3. **Plus économique** : 0-1 Go gratuit
4. **Conforme** : Correspond aux spécifications reçues

---

## 🎯 Conclusion

La simulation utilise maintenant les **vrais paliers de tarification** définis dans le système. Les calculs sont transparents et conformes aux règles métier de Moov Africa.

**Fichier créé** : ✅ `tarifsService.js`  
**Fichier modifié** : ✅ `Simulation.jsx`  
**Tests** : ✅ Validés  
**Documentation** : ✅ À jour  

---

**Implémentation terminée ! 🎉**

Pour tester, allez sur la page Simulation en mode OPEN et entrez des valeurs pour voir les calculs par paliers en action.
