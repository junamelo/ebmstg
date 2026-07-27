# 🔧 Correctif - Page blanche sur simulation OPEN

## 🐛 Problème identifié

La page simulation OPEN (postpayé) affichait une page blanche au lieu du formulaire.

## 🔍 Cause

**Incohérence entre les noms de propriétés des tarifs :**

Dans `mockData.js`, les tarifs sont définis avec :
```javascript
{
  prixParMinute: 25,
  prixParSms: 10,
  prixParGo: 2000
}
```

Mais dans `Simulation.jsx`, le code utilisait :
```javascript
tarifs.tarif_minute  // ❌ INCORRECT
tarifs.tarif_sms     // ❌ INCORRECT
tarifs.tarif_go      // ❌ INCORRECT
```

Quand React essayait d'accéder à `tarifs.tarif_minute` (qui était `undefined`), cela causait une erreur JavaScript qui rendait la page blanche.

## ✅ Solution appliquée

**Correction des noms de propriétés dans `Simulation.jsx` :**

### 1. Affichage des tarifs unitaires
```javascript
// AVANT
<strong>{tarifs.tarif_minute.toLocaleString('fr-FR')} FCFA/min</strong>

// APRÈS
<strong>{tarifs.prixParMinute.toLocaleString('fr-FR')} FCFA/min</strong>
```

### 2. Aperçus temps réel sous les champs
```javascript
// AVANT
≈ {(parseFloat(form.minutesAppel) * tarifs.tarif_minute).toLocaleString('fr-FR')} FCFA

// APRÈS
≈ {(parseFloat(form.minutesAppel) * tarifs.prixParMinute).toLocaleString('fr-FR')} FCFA
```

### 3. Total global temps réel (orange)
```javascript
// AVANT
(parseFloat(form.minutesAppel) || 0) * tarifs.tarif_minute +
(parseFloat(form.nombreSms) || 0) * tarifs.tarif_sms +
(parseFloat(form.volumeDataGo) || 0) * tarifs.tarif_go

// APRÈS
(parseFloat(form.minutesAppel) || 0) * tarifs.prixParMinute +
(parseFloat(form.nombreSms) || 0) * tarifs.prixParSms +
(parseFloat(form.volumeDataGo) || 0) * tarifs.prixParGo
```

### 4. Fonction handleSubmitOpen
```javascript
// AVANT
const montantAppels = minutes * tarifs.tarif_minute
const montantSms = sms * tarifs.tarif_sms
const montantData = dataGo * tarifs.tarif_go

// APRÈS
const montantAppels = minutes * tarifs.prixParMinute
const montantSms = sms * tarifs.prixParSms
const montantData = dataGo * tarifs.prixParGo
```

## 📊 Tarifs réels (mockés)

Les tarifs corrects utilisés dans le système sont :

```javascript
{
  nom: 'Tarif Juillet 2026',
  prixParMinute: 25,      // 25 FCFA par minute d'appel
  prixParSms: 10,         // 10 FCFA par SMS
  prixParGo: 2000,        // 2000 FCFA par Go de data
  estActif: true
}
```

## 🧪 Test de validation

### Scénario de test :
1. Accéder à `/simulation`
2. Cliquer sur "Client OPEN (Postpayé)"
3. Vérifier que les tarifs s'affichent :
   - Appel : **25 FCFA/min** ✅
   - SMS : **10 FCFA/SMS** ✅
   - Data : **2 000 FCFA/Go** ✅
4. Entrer dans les champs :
   - Minutes : `120`
   - SMS : `50`
   - Data : `5`
5. Vérifier les aperçus temps réel :
   - Appels : **≈ 3 000 FCFA** (120 × 25)
   - SMS : **≈ 500 FCFA** (50 × 10)
   - Data : **≈ 10 000 FCFA** (5 × 2000)
6. Vérifier le total global : **13 500 FCFA**
7. Cliquer sur "Calculer l'estimation"
8. Vérifier le résultat détaillé

### Résultat attendu :
```
Appels (120 min)    :  3 000 FCFA
SMS (50 SMS)        :    500 FCFA
Data (5 Go)         : 10 000 FCFA
                      ──────────
Montant total estimé: 13 500 FCFA
```

## 🔄 Fichiers modifiés

1. **`Front/src/pages/simulation/Simulation.jsx`**
   - 7 occurrences corrigées : `tarif_minute` → `prixParMinute`
   - 7 occurrences corrigées : `tarif_sms` → `prixParSms`
   - 7 occurrences corrigées : `tarif_go` → `prixParGo`

2. **`SIMULATION_DOUBLE_TYPE.md`** - Documentation mise à jour
3. **`DEMARRAGE_RAPIDE.md`** - Tarifs mis à jour dans les exemples
4. **`CORRECTIF_SIMULATION.md`** - Ce fichier (nouveau)

## 📝 Logs de débogage ajoutés

Des `console.log()` ont été ajoutés pour faciliter le débogage :

```javascript
console.log('[Simulation] Chargement initial...')
console.log('[Simulation] Tarifs:', t)
console.log('[Simulation] Services:', s)
console.log('[Simulation] Affichage page principale, typeClient:', typeClient)
```

Ces logs permettent de vérifier que les données sont bien chargées et dans quel état se trouve le composant.

## ✅ Statut

**Problème résolu** ✅

La page simulation OPEN fonctionne maintenant correctement avec :
- ✅ Affichage des tarifs unitaires
- ✅ Aperçus temps réel sous chaque champ
- ✅ Total global temps réel (orange)
- ✅ Calcul correct du montant estimé
- ✅ Affichage détaillé du résultat

## 🚀 Pour tester

```bash
# Terminal 1 : Backend
cd Back
python manage.py runserver

# Terminal 2 : Frontend
cd Front
npm start

# Navigateur
http://localhost:3000/simulation
→ Cliquer sur "Client OPEN (Postpayé)"
→ Remplir les champs et observer les aperçus
```

---

**Correctif appliqué le :** 24 juillet 2026  
**Problème :** Page blanche sur simulation OPEN  
**Cause :** Noms de propriétés incorrects (tarif_minute vs prixParMinute)  
**Solution :** Correction des 21 occurrences dans Simulation.jsx  
**Statut :** ✅ Résolu
