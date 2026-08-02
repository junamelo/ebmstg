# ✅ PRIORITÉ 0 COMPLÉTÉE
## Définition et Figeage des Règles Métier

**Date** : 30 juillet 2026  
**Statut** : Terminé

---

## 📦 LIVRABLES CRÉÉS

### 1. SPECIFICATION_REGLES_METIER.md (152 KB)

Document de référence fonctionnelle complet contenant :
- Objectif du portail
- Glossaire métier
- 5 rôles et matrice des permissions
- Modèle de données et règles d'affectation
- 2 types de factures (globale, SOM)
- Cycle de vie des factures (6 statuts)
- Workflow de publication PDF (7 étapes)
- Règles de visibilité par rôle
- 9 erreurs métier attendues
- 4 règles "À VALIDER" avec Moov
- 23 critères d'acceptation fonctionnels

### 2. MATRICE_ACCES_ET_TRANSITIONS.md (78 KB)

Tableaux de référence technique contenant :
- Matrice 40 actions × 5 rôles
- Matrice 6 statuts × 6 transitions
- Détail de chaque transition autorisée
- Détail de chaque transition interdite
- Conditions techniques de validation
- Règles d'audit obligatoires
- 4 classes de permissions codées
- Tests de validation suggérés

---

## 🔍 AUDIT RÉALISÉ

### Fichiers analysés (15)

**Backend** :
- `Back/accounts/models.py`
- `Back/accounts/permissions.py`
- `Back/accounts/views.py`
- `Back/billing/models.py`
- `Back/billing/serializers.py`
- `Back/billing/views.py`
- `Back/billing/services/pdf_processor.py`
- `Back/billing/urls.py`
- `Back/billing/migrations/`

**Frontend** :
- `Front/src/App.jsx`
- `Front/src/services/api.js`
- `Front/src/services/authService.js`
- `Front/src/services/factureService.js`
- `Front/src/pages/agent/PublicationPdf.jsx`

### Règles métier identifiées dans le code

✅ **Conforme** :
- 5 rôles correctement définis
- 6 statuts de facture complets
- Liaison Company → Payeur
- Liaison Line → Employe
- Liaison Invoice → Line
- Filtrage par rôle dans `InvoiceViewSet.get_queryset()`
- 19 permissions granulaires
- Historique des actions tracé

⚠️ **Écarts détectés** (non corrigés volontairement) :
1. Transition ANNULEE → statut actif : pas de validation explicite
2. Visibilité statut < PUBLIEE : pas de filtre systématique pour clients
3. Plusieurs factures candidates : pas de gestion d'erreur explicite
4. Notifications : non implémentées

---

## 📋 RÈGLES MÉTIER FIGÉES

### 3.1 Rôles

```
SUPER_ADMIN          → Administration complète
CHEF_FACTURATION     → Supervision facturation + agents
AGENT_FACTURATION    → Traitement factures + PDF
PAYEUR               → Consultation factures entreprises
EMPLOYE              → Consultation factures lignes
```

### 3.2 Modèle d'affectation

```
Entreprise → Payeur → Voit toutes factures (globales + SOM)
    │
    └── Lignes → Employé → Voit ses factures SOM uniquement
           │
           └── Factures
                ├── Globale (line=NULL)
                └── SOM (line=Line)
```

### 3.3 Cycle de vie

```
BROUILLON → EN_COURS → VALIDEE → PUBLIEE → PAYEE
                 ↓
             ANNULEE
```

**Transitions interdites** :
- ANNULEE → tout statut actif
- PAYEE → BROUILLON/EN_COURS/VALIDEE
- PUBLIEE → BROUILLON/EN_COURS

### 3.4 Workflow publication

```
1. Upload PDF + cycle + période
2. Découpage automatique
3. Extraction identifiants (facture/MSISDN/compte)
4. Matching avec factures EN_COURS
5. Attachement PDF → statut VALIDEE
6. Publication par agent → statut PUBLIEE
7. Visible clients (payeur/employé)
```

### 3.5 Ordre de matching

```
Priorité 1 : Numéro de facture exact
Priorité 2 : MSISDN exact
Priorité 3 : Compte entreprise (si MSISDN absent)
```

### 3.6 Visibilité

```
Admin/Chef/Agent : Toutes factures
Payeur           : Factures PUBLIEE de ses entreprises
Employé          : Factures PUBLIEE de ses lignes
```

---

## ✅ CONFORMITÉ DU CODE ACTUEL

### Points conformes

1. ✅ Les 5 rôles existent dans `User.ROLE_CHOICES`
2. ✅ Les 6 statuts existent dans `StatutFacture`
3. ✅ `Company.payeur` → `User` (FK)
4. ✅ `Line.employe` → `User` (FK, nullable)
5. ✅ `Invoice.company` → `Company` (FK, required)
6. ✅ `Invoice.line` → `Line` (FK, nullable)
7. ✅ Filtrage `InvoiceViewSet.get_queryset()` selon rôle
8. ✅ 19 classes de permissions dans `accounts/permissions.py`
9. ✅ `HistoriqueFacturation` trace les actions
10. ✅ PDF matching par `numero_facture`, `MSISDN`, `compte`

### Écarts identifiés (hors périmètre P0)

Ces écarts relèvent des **Priorités 1-3** et ne sont **PAS corrigés** dans cette phase :

#### 1. Validation transitions interdites
**État actuel** : Pas de `clean()` ou validation Django pour bloquer ANNULEE → BROUILLON  
**Impact** : Transition techniquement possible mais métier interdit  
**Priorité** : P1 (Cohérence fonctionnelle)  
**Action suggérée** : Ajouter validation dans `Invoice.clean()` ou serializer

#### 2. Filtre statut PUBLIEE pour clients
**État actuel** : Filtrage par rôle OK, mais pas de filtre `statut='PUBLIEE'` systématique  
**Impact** : Payeur/employé peuvent techniquement voir VALIDEE  
**Priorité** : P0-P1 (Sécurité métier)  
**Action suggérée** : Ajouter `.filter(statut='PUBLIEE')` dans queryset payeur/employé

#### 3. Gestion erreur multiple factures
**État actuel** : Pas de gestion explicite si plusieurs factures matchent  
**Impact** : Risque d'association arbitraire ou erreur non claire  
**Priorité** : P1 (Qualité matching)  
**Action suggérée** : Lever exception explicite + rapport d'erreur

#### 4. Notifications
**État actuel** : Non implémentées  
**Impact** : Clients non notifiés après publication  
**Priorité** : P2 (Qualité service)  
**Action suggérée** : Implémenter email/SMS après publication

---

## 📊 MÉTRIQUES

### Documents créés
- **2 fichiers** de spécification (230 KB total)
- **12 sections** de règles métier
- **2 matrices** de référence (40 actions × 5 rôles, 6×6 transitions)
- **23 critères** d'acceptation
- **4 règles** à valider avec Moov

### Code analysé
- **15 fichiers** Python et JavaScript
- **~5000 lignes** de code audité
- **0 modification** de code (respecte consigne)
- **4 écarts** identifiés et documentés

---

## 🎯 OBJECTIF ATTEINT

✅ **Règles métier définies** : Chaque comportement attendu est documenté  
✅ **Règles figées** : Document de référence opposable  
✅ **Code audité** : Conformité vérifiée, écarts listés  
✅ **Matrices créées** : Référence rapide pour implémentation  
✅ **Aucune régression** : Aucun code modifié, aucune donnée touchée  

---

## 📖 PROCHAINES ÉTAPES RECOMMANDÉES

### Priorité 1 : Cohérence fonctionnelle

1. **Ajouter filtre statut PUBLIEE** pour payeur/employé
   ```python
   # Dans InvoiceViewSet.get_queryset()
   if user.role == 'PAYEUR':
       return Invoice.objects.filter(
           company__payeur=user,
           statut='PUBLIEE'  # ← AJOUTER
       )
   ```

2. **Valider transitions interdites**
   ```python
   # Dans Invoice.clean()
   FORBIDDEN_TRANSITIONS = {
       'ANNULEE': ['BROUILLON', 'EN_COURS', 'VALIDEE', 'PUBLIEE'],
       'PAYEE': ['BROUILLON', 'EN_COURS', 'VALIDEE'],
   }
   
   if self.pk:  # Modification
       old = Invoice.objects.get(pk=self.pk)
       if self.statut in FORBIDDEN_TRANSITIONS.get(old.statut, []):
           raise ValidationError(f'Transition {old.statut} → {self.statut} interdite')
   ```

3. **Gérer erreur factures multiples**
   ```python
   # Dans pdf_processor.py
   candidates = Invoice.objects.filter(...)
   if candidates.count() > 1:
       raise MultipleInvoicesError(
           f'{candidates.count()} factures trouvées. Clarification manuelle requise.'
       )
   ```

### Priorité 2 : Supprimer mocks frontend

4. Brancher tous les écrans à Django (voir plan Codex)
5. Retirer données localStorage fictives
6. Tester scénario complet de bout en bout

### Priorité 3 : Tests automatisés

7. Implémenter tests suggérés dans MATRICE_ACCES_ET_TRANSITIONS.md
8. Valider critères d'acceptation SPECIFICATION_REGLES_METIER.md

---

## 🚫 CE QUI N'A PAS ÉTÉ FAIT (VOLONTAIREMENT)

Conformément à la consigne de **Priorité 0 uniquement** :

❌ Pas de nouveaux écrans  
❌ Pas de refactoring  
❌ Pas de modification de données  
❌ Pas de création de comptes  
❌ Pas de suppression de mocks  
❌ Pas de changement de routes API  
❌ Pas de migrations  
❌ Pas de correction du mécanisme PDF  
❌ Pas d'invention de règles non présentes  

**Tout le travail a consisté à DOCUMENTER les règles existantes et auditer la conformité.**

---

## 📞 UTILISATION DES DOCUMENTS

### SPECIFICATION_REGLES_METIER.md
- **Pour qui** : Product Owner, développeurs, testeurs
- **Usage** : Référence fonctionnelle, cahier des charges
- **Quand** : Avant chaque développement de feature

### MATRICE_ACCES_ET_TRANSITIONS.md
- **Pour qui** : Développeurs backend, testeurs
- **Usage** : Implémentation permissions, validation transitions
- **Quand** : Lors du codage des vues et tests

---

## ✅ VALIDATION FINALE

☑️ Audit complet sans modification de code  
☑️ 2 documents de référence créés  
☑️ Règles métier figées et vérifiables  
☑️ Écarts identifiés mais non corrigés  
☑️ Conformité à la consigne de Priorité 0  
☑️ Aucune régression introduite  
☑️ Prêt pour Priorité 1  

---

**Développé pour** : Moov Africa Togo  
**Projet** : Portail e-Billings  
**Phase** : Priorité 0 - Règles métier  
**Statut** : ✅ **TERMINÉ**  
**Date** : 30 juillet 2026

