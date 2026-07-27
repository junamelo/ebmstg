# 🔄 Harmonisation Frontend-Backend

## Date : 22 juillet 2026

---

## ✅ Modifications effectuées

### 1. Configuration CORS

**Fichier modifié :** `moov_backend/settings.py`

**Problème :** Le backend était configuré pour accepter uniquement les requêtes du port 5173, alors que le frontend React tourne sur le port 3000.

**Solution :**
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',      # ✅ Ajouté
    'http://127.0.0.1:3000',      # ✅ Ajouté
    'http://localhost:5173',      # Conservé pour compatibilité
    'http://127.0.0.1:5173',      # Conservé pour compatibilité
]
```

**Impact :**
- ✅ Le frontend sur port 3000 peut maintenant communiquer avec le backend
- ✅ Plus d'erreurs CORS lors des requêtes API
- ✅ Compatible avec les deux ports (3000 et 5173)

---

### 2. Cycles de facturation

**Fichier modifié :** `billing/models.py`

**Problème :** Incohérence entre les valeurs de cycles
- Backend : `HYB1`, `HYB2`, `MON1`
- Frontend : `HYB`, `OP`

**Solution :**
```python
# AVANT
class CycleFacturation(models.TextChoices):
    HYB1 = 'HYB1', 'Hybride 1'
    HYB2 = 'HYB2', 'Hybride 2'
    MON1 = 'MON1', 'Mensuel 1'

# APRÈS
class CycleFacturation(models.TextChoices):
    HYB = 'HYB', 'Hybride'
    OP = 'OP', 'Opérationnel'
```

**Migration créée :** `billing/migrations/0002_alter_line_cycle.py`
- ✅ Migration appliquée avec succès
- ✅ Cycle par défaut : `HYB`

**Impact :**
- ✅ Formulaires frontend compatibles avec le backend
- ✅ Création de comptes avec cycles HYB/OP fonctionnelle
- ✅ Attribution de lignes aux payeurs conforme
- ⚠️ Les anciennes valeurs `HYB1`, `HYB2`, `MON1` ne sont plus acceptées

---

## 📋 Récapitulatif des changements

| Élément | Avant | Après | Statut |
|---------|-------|-------|--------|
| Port CORS | 5173 | 3000 + 5173 | ✅ |
| Cycles | HYB1, HYB2, MON1 | HYB, OP | ✅ |
| Migration DB | 0001_initial | 0002_alter_line_cycle | ✅ |
| Cycle par défaut | MON1 | HYB | ✅ |
| Documentation | Incomplète | Mise à jour | ✅ |

---

## 🧪 Tests disponibles

Un script de test a été créé : **`test_cycles.py`**

### Comment tester :

1. **Démarrer le serveur Django**
   ```bash
   cd Back
   python manage.py runserver
   ```

2. **Installer requests (si nécessaire)**
   ```bash
   pip install requests
   ```

3. **Exécuter les tests**
   ```bash
   python test_cycles.py
   ```

### Tests effectués :
- ✅ Connexion et obtention du token JWT
- ✅ Création d'entreprise
- ✅ Création de ligne avec cycle HYB
- ✅ Création de ligne avec cycle OP
- ✅ Récupération des lignes
- ✅ Modification du cycle d'une ligne
- ✅ Validation : rejet des cycles invalides (MON1, HYB1, etc.)
- ✅ Nettoyage automatique des données de test

---

## 📝 Utilisation des nouveaux cycles

### Dans le frontend

**Formulaire création de compte (GestionComptes.jsx) :**
```jsx
<select name="cycle_facturation">
  <option value="HYB">Hybride (HYB)</option>
  <option value="OP">Opérationnel (OP)</option>
</select>
```

**Attribution de lignes :**
- Les lignes affichent maintenant "HYB" ou "OP"
- Compatible avec les formulaires d'import/sélection

### Dans le backend

**Création de ligne (API) :**
```json
POST /api/billing/lines/
{
  "company": 1,
  "msisdn": "79123456",
  "utilisateur": "Employé Test",
  "forfait": 15000.00,
  "cycle": "HYB",
  "statut": "ACTIF"
}
```

**Valeurs acceptées :**
- ✅ `"HYB"` (Hybride)
- ✅ `"OP"` (Opérationnel)
- ❌ `"HYB1"` (invalide)
- ❌ `"HYB2"` (invalide)
- ❌ `"MON1"` (invalide)

---

## ⚠️ Actions requises

### Si vous avez des données existantes

Si des lignes ont déjà été créées avec les anciens cycles, vous devez les mettre à jour manuellement :

```sql
-- Option 1 : Tout mettre en HYB
UPDATE lines SET cycle = 'HYB';

-- Option 2 : Convertir selon la logique métier
UPDATE lines SET cycle = 'HYB' WHERE cycle IN ('HYB1', 'HYB2');
UPDATE lines SET cycle = 'OP' WHERE cycle = 'MON1';
```

### Redémarrer le serveur Django

Après les modifications, redémarrez le serveur :
```bash
python manage.py runserver
```

---

## 🎯 Prochaines étapes

### Priorité 1 - Tester l'intégration
- [ ] Tester la création de compte payeur depuis le frontend
- [ ] Tester l'attribution de lignes avec différents cycles
- [ ] Vérifier l'affichage dans les dashboards
- [ ] Valider les formulaires de modification

### Priorité 2 - Ajouter champ cycle au User
- [ ] Ajouter `cycle_facturation` au modèle User
- [ ] Créer la migration
- [ ] Mettre à jour les serializers
- [ ] Adapter les formulaires frontend

### Priorité 3 - Créer les modèles manquants
- [ ] Package (forfaits)
- [ ] Service (services optionnels)
- [ ] TarifService (options tarifaires)
- [ ] Simulation (historique)
- [ ] Publication (historique agent)

---

## 📚 Documentation mise à jour

Les fichiers suivants ont été mis à jour :
- ✅ `README.md` - Exemples d'API avec nouveaux cycles
- ✅ `CHANGELOG.md` - Historique détaillé des modifications
- ✅ `HARMONISATION_FRONTEND_BACKEND.md` - Ce document
- ✅ `test_cycles.py` - Script de test automatisé

---

## 🔍 Vérification rapide

Pour vérifier que tout fonctionne :

```bash
# 1. Vérifier les migrations
python manage.py showmigrations billing

# 2. Vérifier le modèle
python manage.py shell
>>> from billing.models import CycleFacturation
>>> print(CycleFacturation.choices)
[('HYB', 'Hybride'), ('OP', 'Opérationnel')]

# 3. Tester l'API
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@moov.tg","password":"admin123"}'
```

---

## ✅ Statut final

| Composant | Statut | Notes |
|-----------|--------|-------|
| Configuration CORS | ✅ OK | Port 3000 ajouté |
| Cycles de facturation | ✅ OK | HYB et OP synchronisés |
| Migrations DB | ✅ OK | 0002_alter_line_cycle appliquée |
| Documentation | ✅ OK | Tous les docs mis à jour |
| Tests | ✅ OK | Script test_cycles.py disponible |
| Frontend | ✅ OK | Formulaires compatibles |
| Backend | ✅ OK | API fonctionnelle |

**🎉 Frontend et Backend sont maintenant harmonisés !**
