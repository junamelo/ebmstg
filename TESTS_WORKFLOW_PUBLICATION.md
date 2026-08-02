# Tests du Workflow de Publication - Guide Complet

**Date** : 1er août 2026  
**Statut** : Prêt pour tests

---

## 📋 Checklist des Tests

### ✅ 1. Test GET factures_a_publier (Agent)

**Objectif** : Vérifier que l'endpoint retourne les factures VALIDEE

**Étapes** :
```bash
# 1. Lancer le serveur
cd Back
python manage.py runserver

# 2. Dans un autre terminal, lancer le script de test
python test_publication_workflow.py
```

**Ce que le script teste** :
- ✅ Utilisateurs (agent, payeur, employé)
- ✅ Factures VALIDEE en base
- ✅ Création facture test si nécessaire
- ✅ Liste des factures disponibles pour publication

**Résultat attendu** :
```
============================================================
  1. VÉRIFICATION DES UTILISATEURS
============================================================
✅ Agent trouvé: agent1 (...)
✅ Payeur trouvé: ...
✅ Employé trouvé: ...

============================================================
  2. FACTURES VALIDEE DISPONIBLES
============================================================
Nombre de factures VALIDEE: X

Liste des factures VALIDEE:
1. ID=123 | A20260699475555 | ENTREPRISE ABC | Ligne 99475555 | 25000.00 FCFA
```

---

### ✅ 2. Test publier_masse sur facture VALIDEE

**Objectif** : Vérifier la publication en masse via script Python

**Étapes** :
```bash
# Le script test_publication_workflow.py effectue automatiquement :
python test_publication_workflow.py
```

**Ce que le script fait** :
1. Sélectionne la première facture VALIDEE
2. Change son statut à PUBLIEE
3. Crée l'historique
4. Crée/met à jour la publication globale

**Résultat attendu** :
```
============================================================
  3. TEST PUBLICATION D'UNE FACTURE
============================================================
Facture à publier:
  - ID: 123
  - Numéro: A20260699475555
  - Statut AVANT: VALIDEE
  - Statut APRÈS: PUBLIEE ✅
```

---

### ✅ 3. Vérifier historique facture créé

**Résultat attendu** :
```
============================================================
  4. VÉRIFICATION HISTORIQUE FACTURE
============================================================
✅ Historique créé pour facture A20260699475555
   - Ancien statut: VALIDEE
   - Nouveau statut: PUBLIEE
   - Modifié par: Agent Name
   - Date: 2026-08-01 18:30:00
```

---

### ✅ 4. Vérifier publication globale créée/mise à jour

**Résultat attendu** :
```
============================================================
  5. VÉRIFICATION PUBLICATION GLOBALE
============================================================
✅ Publication créée (ou mise à jour)
   - Cycle: HYB
   - Période: 2026-07-01 → 2026-07-31
   - Agent: Agent Name
   - Factures traitées: 1/1
```

---

### ✅ 5. Vérifier visibilité Payeur

**Résultat attendu** :
```
============================================================
  6. TEST VISIBILITÉ PAYEUR
============================================================
Payeur username voit X facture(s) PUBLIEE
✅ Payeur voit bien la facture A20260699475555
```

---

### ✅ 6. Vérifier visibilité Employé

**Résultat attendu** :
```
============================================================
  7. TEST VISIBILITÉ EMPLOYÉ
============================================================
Employé username voit X facture(s) PUBLIEE
✅ Employé voit bien la facture A20260699475555
```

---

### ✅ 7. Vérifier non-visibilité employé non concerné

**Résultat attendu** :
```
============================================================
  8. TEST NON-VISIBILITÉ EMPLOYÉ NON CONCERNÉ
============================================================
✅ Employé autre_username ne voit PAS la facture A20260699475555 (normal)
```

---

### ✅ 8. Statistiques finales

**Résultat attendu** :
```
============================================================
  9. STATISTIQUES FINALES
============================================================
Distribution des factures par statut:
  - BROUILLON: 0
  - EN_COURS: 5
  - VALIDEE: 28
  - PUBLIEE: 1
  - PAYEE: 0
  - ANNULEE: 0

Total factures: 34
Total historique: 1
Total publications: 1
```

---

## 🧪 Tests Frontend

### Test 1 : Écran Factures à publier

**Étapes** :
1. Se connecter comme agent : `agent1` / mot de passe
2. Aller sur `/agent/factures-a-publier`
3. Vérifier :
   - ✅ Liste des factures VALIDEE s'affiche
   - ✅ Statistiques correctes (nombre, montant)
   - ✅ Filtres cycle et période fonctionnent
   - ✅ Sélection individuelle fonctionne
   - ✅ Sélection en masse fonctionne

### Test 2 : Publication en masse (Frontend)

**Étapes** :
1. Sur `/agent/factures-a-publier`
2. Sélectionner 2-3 factures
3. Cliquer "Publier la sélection"
4. Confirmer
5. Vérifier :
   - ✅ Message de succès
   - ✅ Liste rechargée automatiquement
   - ✅ Factures disparues de la liste

### Test 3 : Visibilité Payeur

**Étapes** :
1. Se déconnecter
2. Se connecter comme payeur
3. Aller sur `/factures`
4. Vérifier :
   - ✅ Voir uniquement factures PUBLIEE
   - ✅ Ne PAS voir factures VALIDEE
   - ✅ Ne PAS voir factures d'autres entreprises

### Test 4 : Visibilité Employé

**Étapes** :
1. Se connecter comme employé : `99475555` / mot de passe
2. Aller sur `/factures`
3. Vérifier :
   - ✅ Voir uniquement ses factures PUBLIEE
   - ✅ Ne PAS voir factures d'autres lignes

### Test 5 : Historique Publications

**Étapes** :
1. Se connecter comme agent/chef
2. Aller sur `/agent/publication/historique`
3. Vérifier :
   - ✅ Liste des publications s'affiche (API réelle)
   - ✅ Statistiques correctes
   - ✅ Filtres fonctionnent
   - ✅ Plus de données mock

---

## 🔧 Scripts de Test Disponibles

### test_publication_workflow.py

**Commande** :
```bash
cd Back
python test_publication_workflow.py
```

**Ce qu'il fait** :
- Vérifie les utilisateurs
- Liste les factures VALIDEE
- Crée une facture test si nécessaire
- Simule la publication
- Vérifie l'historique
- Vérifie la visibilité par rôle
- Affiche les statistiques

**Durée** : ~5 secondes

---

## 📊 Résultats Attendus Globaux

### Backend
- ✅ Endpoint `/api/billing/invoices/factures_a_publier/` fonctionne
- ✅ Endpoint `/api/billing/invoices/publier_masse/` fonctionne
- ✅ Filtre `statut='PUBLIEE'` appliqué pour PAYEUR/EMPLOYE
- ✅ Historique créé automatiquement
- ✅ Publication globale créée/mise à jour

### Frontend
- ✅ Écran "Factures à publier" fonctionnel
- ✅ Publication en masse fonctionne
- ✅ Menu navigation mis à jour
- ✅ Historique utilise API réelle (plus de mock)

### Sécurité
- ✅ Payeur voit uniquement ses factures PUBLIEE
- ✅ Employé voit uniquement ses factures PUBLIEE
- ✅ Impossible d'accéder factures non publiées via URL

---

## 🐛 Problèmes Connus

### Si le script échoue

**Erreur** : `User matching query does not exist`
- **Solution** : Créer l'agent avec `python create_test_data.py`

**Erreur** : `No module named 'billing'`
- **Solution** : Vérifier que vous êtes dans le dossier `Back/`

**Erreur** : `NameError: name 'CanPublishInvoices' is not defined`
- **Solution** : Déjà corrigé dans `billing/views.py`

### Si l'historique est vide

**Cause** : Aucune publication en base
- **Solution** : Le script crée automatiquement une publication test

---

## ✅ Checklist de Validation Finale

- [ ] Script `test_publication_workflow.py` exécuté sans erreur
- [ ] Écran `/agent/factures-a-publier` s'affiche correctement
- [ ] Publication en masse fonctionne
- [ ] Payeur voit uniquement factures PUBLIEE
- [ ] Employé voit uniquement ses factures PUBLIEE
- [ ] Historique affiche données réelles (API)
- [ ] Aucune donnée mock restante

---

## 📝 Notes

- Le script peut être exécuté plusieurs fois sans problème
- Les données de test créées sont réutilisables
- L'historique utilise maintenant l'API `/billing/publications/`
- Les statistiques sont calculées en temps réel

**Prêt pour la démonstration !** 🎉
