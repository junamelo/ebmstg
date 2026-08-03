# ANALYSE : CODES FORMULE MANQUANTS

## Source
Fichier Excel : `Contexte/Données_Test_Facturation (1).xlsx`

## Codes utilisés dans HYBRID/OPEN mais ABSENTS de la feuille Formule

### Codes manquants (6 au total)

| Code | Feuille | Occurrences | Statut |
|------|---------|-------------|--------|
| **M0B** | HYBRID | 6 | ❌ Manquant dans feuille Formule |
| **M1B** | HYBRID | 16 | ❌ Manquant dans feuille Formule |
| **M2B** | HYBRID | 13 | ❌ Manquant dans feuille Formule |
| **M4B** | HYBRID | 13 | ❌ Manquant dans feuille Formule |
| **M6B** | HYBRID | 4 | ❌ Manquant dans feuille Formule |
| **OP0** | OPEN | 12 | ❌ Manquant dans feuille Formule |

### Problème de casse détecté

- **"OP0"** (dans OPEN) vs **"Op0"** (dans Formule) 
  - La feuille Formule définit "Op0" mais la feuille OPEN utilise "OP0"
  - Il faut clarifier quel est le code officiel

## Codes définis dans Formule mais non utilisés dans HYBRID/OPEN

Ces 9 codes existent dans la feuille Formule mais n'apparaissent dans aucune ligne HYBRID ou OPEN :

- B20 (ALISE)
- B30 (BRISE)
- B50 (DUNE)
- F30 (FLEXI)
- M3C (MOON)
- Op0 (OPEN)
- S1Q (SUN)
- S30 (SMART)
- TOT (OPEN TRACKING)

## État de l'import actuel

### ✅ Données importées (vérifiables dans Excel)

**Services et options** :
- 4 services : BlackBerry, No Limit, Facture Détaillée, Incognito
- 84 options avec prix extraits des colonnes Excel

**Forfaits** :
- 13 forfaits importés depuis feuille Formule (codes + noms uniquement)
- Prix et quotas définis à 0/NULL par défaut

### ❌ Données NON importées (sources manquantes)

- Prix forfaits : aucune colonne prix dans feuille Formule
- Quotas forfaits (data/voix/SMS) : non disponibles dans Excel
- Codes M0B, M1B, M2B, M4B, M6B : absents de feuille Formule

## Actions requises

### 1. Clarifier les codes M0B, M1B, M2B, M4B, M6B
- Sont-ils des forfaits réels à ajouter à la feuille Formule ?
- Si oui, fournir : nom complet, prix mensuel, quotas

### 2. Résoudre le problème de casse OP0/Op0
- Code officiel : "OP0" ou "Op0" ?

### 3. Fournir le référentiel métier officiel
Pour les 13 forfaits de la feuille Formule, fournir :
- Prix mensuel (FCFA)
- Quota data (Mo)
- Quota voix (minutes)
- Quota SMS
- Type forfait (DATA, VOIX, SMS, MIXTE)

## Commande d'import disponible

```bash
python manage.py import_catalogue_forfaits
```

**État actuel** :
- ✅ Importe les 4 services avec 84 options (prix vérifiables)
- ✅ Importe les 13 forfaits (structure uniquement)
- ✅ Idempotente (pas de doublons)
- ✅ 13 tests unitaires validés
- ⚠️ Prix et quotas forfaits à 0/NULL en attente du référentiel

## Tests

13 tests d'import créés et validés :
- ✅ Commande existe
- ✅ Import services BlackBerry, No Limit, Facture Détaillée, Incognito
- ✅ Import 13 forfaits depuis feuille Formule
- ✅ Ignore en-tête CODES/FORMULES
- ✅ Options ont des prix > 0
- ✅ Import idempotent
- ✅ Tous éléments actifs par défaut

```bash
python manage.py test billing.tests.test_import_catalogue -v 2
```

**Résultat** : 13/13 tests OK
