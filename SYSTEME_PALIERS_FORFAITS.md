# 📊 Système de Paliers pour les Forfaits

## 🎯 Vue d'ensemble

La page **Gestion des Forfaits** (`/agent/forfaits`) a été entièrement refondue pour implémenter un **système de paliers** pour la facturation des appels et de la data.

---

## 🔧 Nouveau système de tarification

### 1. 📞 **Appels : Paliers par durée**

**Principe :**  
La facturation des appels se fait par paliers de **durée en secondes**.

**Exemple de configuration :**
```
Palier 1 : 30s  → 75 FCFA
Palier 2 : 60s  → 100 FCFA
Palier 3 : 120s → 150 FCFA
```

**Logique de facturation :**
- Un appel de **0 à 30 secondes** → facturé **75 FCFA** (palier 1)
- Un appel de **31 à 60 secondes** → facturé **100 FCFA** (palier 2)
- Un appel de **61 à 120 secondes** → facturé **150 FCFA** (palier 3)
- Un appel de **121 secondes et plus** → facturé au dernier palier ou calcul proportionnel

**Interface :**
- ➕ Bouton "Ajouter un palier" pour créer un nouveau palier
- 🗑️ Bouton de suppression pour chaque palier (minimum 1 palier obligatoire)
- 📊 Champs : Durée (secondes) + Prix (FCFA)

---

### 2. 📶 **Data : Paliers par volume**

**Principe :**  
La facturation de la data se fait par paliers de **volume en Mo (Mégaoctets)**.

**Exemple de configuration :**
```
Palier 1 : 100 Mo   → 200 FCFA
Palier 2 : 500 Mo   → 800 FCFA
Palier 3 : 1024 Mo  → 1500 FCFA (1 Go)
```

**Logique de facturation :**
- Consommation de **0 à 100 Mo** → facturé **200 FCFA** (palier 1)
- Consommation de **101 à 500 Mo** → facturé **800 FCFA** (palier 2)
- Consommation de **501 à 1024 Mo** → facturé **1500 FCFA** (palier 3)
- Consommation de **1025 Mo et plus** → facturé au dernier palier ou calcul proportionnel

**Interface :**
- ➕ Bouton "Ajouter un palier" pour créer un nouveau palier
- 🗑️ Bouton de suppression pour chaque palier (minimum 1 palier obligatoire)
- 📊 Champs : Volume (Mo) + Prix (FCFA)

---

### 3. 💬 **SMS : Prix uniforme**

**Principe :**  
Les SMS ont un **prix fixe unique**, pas de système de paliers.

**Exemple :**
```
Prix SMS : 10 FCFA par SMS
```

**Logique de facturation :**
- Chaque SMS coûte **10 FCFA** (ou le prix configuré)
- Pas de paliers, tarification linéaire

**Interface :**
- 📝 Champ unique : Prix par SMS (FCFA)

---

## ✨ Fonctionnalités implémentées

### ✅ Création de forfait
1. Cliquer sur **"Nouveau forfait"**
2. Remplir le **nom du forfait** (Ex: "Forfait Août 2026")
3. Configurer les **paliers d'appels** :
   - Ajouter autant de paliers que nécessaire
   - Définir durée (secondes) et prix (FCFA)
4. Définir le **prix SMS** (fixe)
5. Configurer les **paliers de data** :
   - Ajouter autant de paliers que nécessaire
   - Définir volume (Mo) et prix (FCFA)
6. Cliquer sur **"Créer le forfait"**

### ✅ Modification de forfait
1. Dans la liste, cliquer sur **"Modifier"** à côté d'un forfait
2. Le formulaire se remplit avec les valeurs actuelles
3. Modifier les paliers :
   - Ajouter de nouveaux paliers
   - Modifier les paliers existants
   - Supprimer des paliers (min 1)
4. Cliquer sur **"Enregistrer les modifications"**

### ✅ Gestion des forfaits
- ✅ **Activer** un forfait → devient le forfait en vigueur
- ✅ **Désactiver** un forfait → il reste dans l'historique
- ✅ **Rechercher** un forfait par nom
- ✅ Visualiser tous les forfaits (actifs et inactifs)

---

## 🎨 Interface utilisateur

### Header
```
┌───────────────────────────────────────────────────────┐
│  Gestion des Forfaits                 [+ Nouveau]     │
│  Configuration des grilles tarifaires avec paliers    │
└───────────────────────────────────────────────────────┘
```

### Formulaire de création/modification
```
┌───────────────────────────────────────────────────────┐
│  Créer un nouveau forfait                             │
├───────────────────────────────────────────────────────┤
│  Nom du forfait: [________________]                   │
│                                                        │
│  📞 Paliers Appels              [+ Ajouter palier]    │
│  ├─ 30s  → 75 FCFA   [🗑️]                            │
│  ├─ 60s  → 100 FCFA  [🗑️]                            │
│  └─ 120s → 150 FCFA  [🗑️]                            │
│                                                        │
│  💬 Prix SMS: [10] FCFA                               │
│                                                        │
│  📶 Paliers Data                [+ Ajouter palier]    │
│  ├─ 100 Mo  → 200 FCFA   [🗑️]                        │
│  ├─ 500 Mo  → 800 FCFA   [🗑️]                        │
│  └─ 1024 Mo → 1500 FCFA  [🗑️]                        │
│                                                        │
│  [Créer le forfait]  [Annuler]                        │
└───────────────────────────────────────────────────────┘
```

### Liste des forfaits
```
┌────────────────────────────────────────────────────────────┐
│  Liste des forfaits          🔍 [Rechercher...]           │
├──────┬─────┬──────────┬──────────┬────────┬────────┬──────┤
│ Nom  │ SMS │ Appels   │ Data     │ Date   │ Statut │ Acts │
├──────┼─────┼──────────┼──────────┼────────┼────────┼──────┤
│ Août │ 10  │ 3 paliers│ 3 paliers│ 01/08  │ Actif  │ Mod  │
│ Juil │ 10  │ 2 paliers│ 2 paliers│ 01/07  │ Inactif│ Act  │
└──────┴─────┴──────────┴──────────┴────────┴────────┴──────┘
```

---

## 🔄 Changements par rapport à l'ancienne version

### ❌ **Supprimé**
1. Templates prédéfinis (Standard, Entreprise, Promotionnel)
2. Système de tarification au prix par minute/Go
3. Prévisualisation de l'impact en %
4. Filtre par statut dans le tableau

### ✅ **Ajouté**
1. **Système de paliers** pour appels et data
2. **Gestion dynamique** des paliers (ajouter/supprimer)
3. **Bouton Modifier** sur chaque forfait
4. **Mode édition** complet avec pré-remplissage
5. **Interface plus claire** avec icônes explicites
6. **Explications** sous chaque section de paliers

---

## 📊 Structure des données

### Ancien format (backend actuel)
```javascript
{
  nom: "Forfait Juillet",
  prixParMinute: 25,      // Prix uniforme par minute
  prixParSms: 10,         // Prix uniforme par SMS
  prixParGo: 2000,        // Prix uniforme par Go
  estActif: true
}
```

### Nouveau format (avec paliers)
```javascript
{
  nom: "Forfait Août",
  prixParSms: 10,         // Prix uniforme SMS (inchangé)
  paliersAppels: [        // ✨ NOUVEAU
    { duree: 30, prix: 75 },
    { duree: 60, prix: 100 },
    { duree: 120, prix: 150 }
  ],
  paliersData: [          // ✨ NOUVEAU
    { volume: 100, prix: 200 },
    { volume: 500, prix: 800 },
    { volume: 1024, prix: 1500 }
  ],
  // Pour compatibilité backend
  prixParMinute: 25,      // Calculé depuis le premier palier
  prixParGo: 2000,        // Calculé depuis le premier palier
  estActif: true
}
```

---

## 🔧 Backend à adapter

Le backend actuel ne gère pas encore les paliers. Modifications nécessaires :

### 1. Modèle `Package` ou `Tarif`
```python
class Tarif(models.Model):
    nom = models.CharField(max_length=200)
    prix_sms = models.IntegerField(default=10)
    
    # Nouveaux champs JSON
    paliers_appels = models.JSONField(default=list)  # [{ duree: 30, prix: 75 }, ...]
    paliers_data = models.JSONField(default=list)    # [{ volume: 100, prix: 200 }, ...]
    
    # Anciens champs (pour compatibilité)
    prix_par_minute = models.DecimalField(max_digits=10, decimal_places=2)
    prix_par_go = models.DecimalField(max_digits=10, decimal_places=2)
    
    est_actif = models.BooleanField(default=False)
    date_application = models.DateField()
```

### 2. Logique de calcul
```python
def calculer_cout_appel(duree_secondes, paliers_appels):
    """
    Trouve le palier correspondant à la durée
    """
    paliers_tries = sorted(paliers_appels, key=lambda x: x['duree'])
    
    for palier in paliers_tries:
        if duree_secondes <= palier['duree']:
            return palier['prix']
    
    # Si dépassement du dernier palier
    return paliers_tries[-1]['prix']

def calculer_cout_data(volume_mo, paliers_data):
    """
    Trouve le palier correspondant au volume
    """
    paliers_tries = sorted(paliers_data, key=lambda x: x['volume'])
    
    for palier in paliers_tries:
        if volume_mo <= palier['volume']:
            return palier['prix']
    
    # Si dépassement du dernier palier
    return paliers_tries[-1]['prix']
```

---

## 🧪 Exemples de calcul

### Exemple 1 : Appels
**Configuration :**
- Palier 1 : 30s → 75 FCFA
- Palier 2 : 60s → 100 FCFA
- Palier 3 : 120s → 150 FCFA

**Facturations :**
- Appel de 20s → **75 FCFA** (palier 1)
- Appel de 30s → **75 FCFA** (palier 1)
- Appel de 31s → **100 FCFA** (palier 2) ✨
- Appel de 45s → **100 FCFA** (palier 2)
- Appel de 90s → **150 FCFA** (palier 3)
- Appel de 200s → **150 FCFA** (dernier palier)

### Exemple 2 : Data
**Configuration :**
- Palier 1 : 100 Mo → 200 FCFA
- Palier 2 : 500 Mo → 800 FCFA
- Palier 3 : 1024 Mo → 1500 FCFA

**Facturations :**
- 50 Mo → **200 FCFA** (palier 1)
- 100 Mo → **200 FCFA** (palier 1)
- 101 Mo → **800 FCFA** (palier 2) ✨
- 300 Mo → **800 FCFA** (palier 2)
- 1000 Mo → **1500 FCFA** (palier 3)
- 2000 Mo → **1500 FCFA** (dernier palier)

---

## ✅ Avantages du nouveau système

1. **✨ Plus flexible** : Tarification progressive selon consommation réelle
2. **💰 Mieux adapté** : Reflète la politique tarifaire de Moov Africa
3. **🎯 Plus précis** : Facturation au palier exact (pas de moyennes)
4. **📊 Plus transparent** : L'utilisateur voit clairement les paliers
5. **🔧 Facilement modifiable** : L'agent peut ajuster finement les paliers

---

## 🚀 Comment tester

```bash
# Frontend
cd Front
npm start

# Navigateur
http://localhost:3000/agent/forfaits
```

1. Se connecter en tant qu'**Agent de facturation**
2. Aller dans **"Gestion Forfaits"** (sidebar)
3. Cliquer sur **"Nouveau forfait"**
4. Configurer :
   - Nom : "Test Paliers Août"
   - Appels : 30s→75, 60s→100, 120s→150
   - SMS : 10
   - Data : 100Mo→200, 500Mo→800, 1024Mo→1500
5. Cliquer sur **"Créer le forfait"**
6. Vérifier dans la liste
7. Cliquer sur **"Modifier"** pour tester l'édition

---

**Date de création :** 24 juillet 2026  
**Fichiers modifiés :** `Front/src/pages/agent/GestionForfaits.jsx`  
**Status :** ✅ Implémenté (frontend uniquement, backend à adapter)
