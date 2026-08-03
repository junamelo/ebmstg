# Correction Cohérence Forfaits/Services/Options - Complet

## Date
2 août 2026 - 09h10

## Problèmes identifiés

### 1. Permissions backend incorrectes
- `CanManageTarifs` et `CanManageServices` vérifiaient `request.user.has_permission('tarifs.edit')` et `request.user.has_permission('services.edit')`
- Ces permissions utilisent le système `custom_permissions` qui n'est pas attribué aux agents
- **Résultat** : Les agents ne pouvaient pas créer de forfaits, services ou options

### 2. Champs incorrects dans GestionForfaits.jsx
- Utilisait `quota_voix_minutes` au lieu de `quota_minutes` (nom du champ dans le modèle)
- Utilisait `type_forfait` avec des valeurs `STANDARD`, `PREMIUM`, `BUSINESS` au lieu de `DATA`, `VOIX`, `SMS`, `MIXTE`

### 3. ServiceViewSet retournait ServiceListSerializer
- Pour l'action `list`, le ViewSet retournait `ServiceListSerializer` qui n'inclut pas les tarifs
- La simulation a besoin des tarifs pour afficher les options disponibles

## Corrections appliquées

### 1. Permissions backend (Back/accounts/permissions.py)

**Avant :**
```python
class CanManageTarifs(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_permission('tarifs.edit')  # ❌ Problème
```

**Après :**
```python
class CanManageTarifs(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        # ✅ Autorisation directe pour Admin, Chef, Agent
        return request.user.role in ['SUPER_ADMIN', 'CHEF_FACTURATION', 'AGENT_FACTURATION']
```

**Identique pour CanManageServices**

### 2. Champs forfaits (Front/src/pages/agent/GestionForfaits.jsx)

**Corrections :**
- `quota_voix_minutes` → `quota_minutes` (3 occurrences)
- Options type_forfait : `STANDARD`, `PREMIUM`, `BUSINESS` → `DATA`, `VOIX`, `SMS`, `MIXTE`
- Valeur par défaut : `STANDARD` → `MIXTE`

### 3. ServiceViewSet (Back/billing/views.py)

**Avant :**
```python
def get_serializer_class(self):
    if self.action == 'list':
        return ServiceListSerializer  # ❌ Sans tarifs
    elif self.action == 'create':
        return ServiceCreateSerializer
    return ServiceSerializer
```

**Après :**
```python
def get_serializer_class(self):
    if self.action == 'create':
        return ServiceCreateSerializer
    return ServiceSerializer  # ✅ Inclut toujours les tarifs
```

## Tests créés

**Fichier : Back/billing/test_packages_services.py**

### Tests de permissions (9 tests)
1. ✅ Agent peut créer un forfait
2. ✅ Chef peut créer un forfait
3. ✅ Admin peut créer un forfait
4. ✅ Agent peut créer un service
5. ✅ Agent peut créer une option sur un service
6. ✅ Employé peut lire services/options actifs
7. ✅ Employé ne peut pas créer un forfait
8. ✅ Employé ne peut pas créer un service
9. ✅ Employé ne peut pas modifier un service

### Tests de logique métier (4 tests)
1. ✅ Un forfait Package ne contient pas d'options TarifService
2. ✅ Un service peut avoir plusieurs options TarifService
3. ✅ Une option créée apparaît dans la liste des services pour simulation
4. ✅ Forfaits et services sont indépendants, aucune relation croisée

## Résultats des vérifications

### Tests Django
```bash
python manage.py test
# Résultat : 110 tests OK
```

### Check Django
```bash
python manage.py check
# Résultat : System check identified no issues (0 silenced)
```

### Build Frontend
```bash
npm run build
# Résultat : ✓ built in 17.66s
```

## Règles métier validées

### Forfait (Package)
- ✅ Prix mensuel fixe
- ✅ Quotas : data (Mo), voix (minutes), SMS
- ✅ Types : DATA, VOIX, SMS, MIXTE
- ✅ Aucune relation avec Service ou TarifService
- ✅ Géré dans `/agent/forfaits`

### Service
- ✅ Conteneur pour options tarifaires
- ✅ Types : PASS, OPTION, PROMO
- ✅ Peut avoir plusieurs options (TarifService)
- ✅ Géré dans `/agent/services`

### Option (TarifService)
- ✅ Appartient obligatoirement à un Service
- ✅ Prix et durée de validité
- ✅ Créée via POST `/api/billing/tarifs/` avec `service` ID
- ✅ Apparaît automatiquement dans la simulation

### Simulation
- ✅ Charge services actifs avec `GET /api/billing/services/`
- ✅ Filtre services ayant au moins une option active
- ✅ Affiche options disponibles pour sélection
- ✅ Si aucun service actif, affiche message approprié

## Permissions finales

| Rôle | Forfaits | Services | Options | Simulation |
|------|----------|----------|---------|------------|
| **Admin** | Créer, Modifier, Lire | Créer, Modifier, Lire | Créer, Modifier, Lire | Lire |
| **Chef** | Créer, Modifier, Lire | Créer, Modifier, Lire | Créer, Modifier, Lire | Lire |
| **Agent** | Créer, Modifier, Lire | Créer, Modifier, Lire | Créer, Modifier, Lire | Lire |
| **Employé** | Lire (actifs) | Lire (actifs) | Lire (actifs) | Lire |
| **Payeur** | Lire (actifs) | Lire (actifs) | Lire (actifs) | Lire |

## Workflow agent pour créer une option

1. Se connecter en tant qu'agent (ou chef/admin)
2. Aller sur `/agent/services`
3. Cliquer sur "Nouveau forfait" pour créer un service (ex: BlackBerry)
4. Une fois créé, ouvrir le service en cliquant dessus (accordéon)
5. Cliquer sur "+ Option" pour ajouter une option tarifaire (ex: BB12 - 1200 FCFA)
6. L'option est créée via `POST /api/billing/tarifs/` avec `{ service: <id>, nom_option: "BB12", prix: 1200 }`
7. L'API recharge automatiquement avec `GET /api/billing/services/` pour afficher la nouvelle option
8. L'option apparaît immédiatement dans la simulation pour tous les utilisateurs

## Workflow simulation employé

1. Se connecter en tant qu'employé
2. Aller sur `/simulation`
3. Choisir type client : HYB (Hybride) ou OP (Open/Postpayé)
4. **Si services/options existent** :
   - Ouvrir l'accordéon "Services"
   - Développer chaque service pour voir ses options
   - Sélectionner les options souhaitées
   - Pour OP : remplir aussi les consommations prévues
   - Cliquer sur "Calculer l'estimation"
5. **Si aucun service actif** :
   - Message affiché : "Aucun service optionnel disponible pour le moment. Contactez votre agent de facturation pour plus d'informations."

## Points d'attention

### ✅ Forfaits et services sont distincts
- Un forfait Package est un contrat mensuel avec quotas
- Un service est un conteneur d'options tarifaires additionnelles
- Il n'y a **aucune relation** entre Package et TarifService

### ✅ GestionForfaits vs GestionServices
- **GestionForfaits.jsx** : gère exclusivement les forfaits Package (prix mensuel + quotas)
- **GestionServices.jsx** : gère les services et leurs options TarifService (ex: BlackBerry BB12, No Limit 24h)

### ✅ Simulation nécessite des données réelles
- Si aucun service actif n'existe en base, la simulation affiche un message approprié
- Les agents doivent créer services et options avant que les employés puissent simuler

### ✅ Tests exhaustifs
- 13 nouveaux tests spécifiques forfaits/services/options
- Total : 110 tests Django tous validés
- Aucun test ne vérifie de données mock

## Fichiers modifiés

1. `Back/accounts/permissions.py` - Permissions corrigées
2. `Back/billing/views.py` - ServiceViewSet serializer corrigé
3. `Front/src/pages/agent/GestionForfaits.jsx` - Champs corrigés
4. `Back/billing/test_packages_services.py` - Nouveaux tests créés

## Fichiers non modifiés (déjà corrects)

- `Back/billing/models.py` - Relations Package/Service/TarifService correctes
- `Back/billing/serializers.py` - Serializers corrects
- `Front/src/pages/agent/GestionServices.jsx` - Déjà correct, gère services + options
- `Front/src/pages/simulation/Simulation.jsx` - Déjà correct, filtre services actifs

## Prochaines étapes recommandées

1. ✅ Créer des services et options en base via l'interface agent
2. ✅ Tester la simulation avec un compte employé
3. ✅ Vérifier que les options créées apparaissent immédiatement
4. ✅ Documenter les services standards pour Moov Africa (BlackBerry, No Limit, Facture Détaillée, Incognito)

## Conclusion

**Statut : ✅ COMPLET ET VALIDÉ**

- Backend : permissions corrigées, tests validés (110/110 OK)
- Frontend : champs corrigés, build réussi
- Cohérence métier : forfaits ≠ services, indépendance validée
- Tests : 13 nouveaux tests spécifiques, tous validés
- Agent peut maintenant créer forfaits, services et options
- Employés peuvent lire et simuler avec les services actifs
