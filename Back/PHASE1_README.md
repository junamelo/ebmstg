# Phase 1 : Authentification & Gestion Utilisateurs ✅

## 📋 Ce qui a été implémenté

### 1. API Authentification Complète

#### Endpoints disponibles :

**POST `/api/accounts/login/`**
```json
{
  "email": "agent@moov.tg",
  "password": "agent123"
}
```
Retourne : `{ user, access, refresh }`

**POST `/api/accounts/logout/`**
```json
{
  "refresh": "your_refresh_token"
}
```
Blacklist le token pour empêcher réutilisation

**POST `/api/accounts/refresh/`**
```json
{
  "refresh": "your_refresh_token"
}
```
Retourne : `{ access }` (nouveau token)

**POST `/api/accounts/change-password/`**
```json
{
  "old_password": "ancien_mdp",
  "new_password": "nouveau_mdp",
  "new_password_confirm": "nouveau_mdp"
}
```

**GET `/api/accounts/profile/`**
Retourne les infos de l'utilisateur connecté

---

### 2. API Gestion Utilisateurs (CRUD complet)

#### Endpoints ViewSet `/api/accounts/users/` :

**GET `/api/accounts/users/`** - Liste des utilisateurs
- Super Admin : voit tout
- Chef : voit ses agents
- Autres : voient seulement eux-mêmes

**POST `/api/accounts/users/`** - Créer utilisateur
```json
{
  "email": "nouveau@moov.tg",
  "username": "nouveau_user",
  "password": "Moov@20260730",
  "first_name": "Prénom",
  "last_name": "Nom",
  "role": "AGENT_FACTURATION",
  "status": "ACTIF",
  "telephone": "90123456",
  "force_password_change": true,
  "send_email": true
}
```

**GET `/api/accounts/users/{id}/`** - Détail utilisateur

**PUT/PATCH `/api/accounts/users/{id}/`** - Modifier utilisateur

**DELETE `/api/accounts/users/{id}/`** - Supprimer utilisateur

---

### 3. Actions Spéciales

**POST `/api/accounts/users/{id}/change_status/`**
```json
{
  "new_status": "SUSPENDU",
  "reason": "Non-paiement",
  "end_date": "2026-08-30T00:00:00Z",
  "send_notification": true
}
```

**POST `/api/accounts/users/{id}/reset_password/`**
```json
{
  "new_password": "Moov@20260730",
  "force_change": true,
  "send_email": true
}
```

**GET `/api/accounts/users/{id}/status_history/`**
Historique des changements de statut

**GET `/api/accounts/users/{id}/permissions/`**
Toutes les permissions de l'utilisateur

**POST `/api/accounts/users/{id}/assign_permission/`**
```json
{
  "permission": "billing.publish",
  "action": "add"
}
```

---

### 4. Permissions Personnalisées

Créé dans `accounts/permissions.py` :

- `IsSuperAdmin` - Super admin seulement
- `IsChefFacturation` - Chef et admin
- `IsAgentFacturation` - Agent, chef et admin
- `IsPayeur` - Payeur seulement
- `IsEmploye` - Employé seulement
- `HasCustomPermission` - Basé sur permissions user
- `CanManageUser` - Peut gérer un autre user
- `IsOwnerOrAdmin` - Propriétaire ou admin
- `IsActiveUser` - Utilisateur actif seulement
- `CanCreateUser` - Peut créer des users
- `CanPublishInvoices` - Peut publier factures
- `CanCancelInvoices` - Peut annuler factures
- `CanManageTarifs` - Peut gérer tarifs
- `CanManageServices` - Peut gérer services

**Usage dans une vue** :
```python
from accounts.permissions import IsAgentFacturation, CanManageUser

class MonView(APIView):
    permission_classes = [IsAgentFacturation, CanManageUser]
```

---

### 5. Middlewares de Sécurité

Créé dans `accounts/middleware.py` :

#### `AuditLogMiddleware`
- Logger automatiquement toutes les actions sensibles
- Capture : user, méthode, path, IP, durée, status
- Logs dans `logs/security.log`

#### `CheckUserStatusMiddleware`
- Vérifie automatiquement si suspension expirée
- Réactive l'utilisateur si `status_end_date` dépassée
- Crée un historique automatiquement

---

### 6. JWT avec Token Blacklist

Configuration dans `settings.py` :
- **Access token** : 2 heures
- **Refresh token** : 7 jours
- **Rotation** : Activée (nouveau refresh à chaque refresh)
- **Blacklist** : Activée (empêche réutilisation après logout)

---

## 🔧 Configuration Required

### 1. Créer les dossiers de logs

```bash
cd Back
mkdir logs
```

### 2. Appliquer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Créer un superuser si besoin

```bash
python manage.py createsuperuser
```

Ou utiliser le script existant :
```bash
python create_superuser.py
```

---

## 🧪 Tests des Endpoints

### Test 1 : Login
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@moov.tg",
    "password": "admin123"
  }'
```

### Test 2 : Profil
```bash
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test 3 : Créer un agent
```bash
curl -X POST http://localhost:8000/api/accounts/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nouvel.agent@moov.tg",
    "username": "nouvel_agent",
    "password": "Moov@20260730",
    "first_name": "Jean",
    "last_name": "DUPONT",
    "role": "AGENT_FACTURATION",
    "telephone": "90123456"
  }'
```

### Test 4 : Changer statut
```bash
curl -X POST http://localhost:8000/api/accounts/users/USER_ID/change_status/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "new_status": "SUSPENDU",
    "reason": "Test suspension",
    "end_date": "2026-08-30T00:00:00Z"
  }'
```

### Test 5 : Logout
```bash
curl -X POST http://localhost:8000/api/accounts/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

---

## 📊 Matrice des Permissions

| Rôle | Créer User | Gérer Status | Reset MDP | Voir Tous | Gérer Permissions |
|------|------------|--------------|-----------|-----------|-------------------|
| **SUPER_ADMIN** | ✅ Tous | ✅ Tous | ✅ Tous | ✅ | ✅ |
| **CHEF_FACTURATION** | ✅ Agents | ✅ Ses agents | ✅ Ses agents | ✅ Ses agents | ❌ |
| **AGENT_FACTURATION** | ✅ Payeur/Employé | ❌ | ❌ | ❌ | ❌ |
| **PAYEUR** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **EMPLOYE** | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🔐 Sécurité Implémentée

✅ Validation mot de passe (8 chars, maj, min, chiffre, spécial)
✅ Hash des mots de passe (Django PBKDF2)
✅ JWT avec rotation et blacklist
✅ Logs de sécurité (actions sensibles)
✅ Vérification automatique statut user
✅ IP tracking lors des connexions
✅ Protection CSRF
✅ CORS configuré
✅ Permissions granulaires par rôle
✅ Audit trail des changements de statut

---

## 📝 TODO (à implémenter plus tard)

- [ ] Envoi d'emails (notifications)
- [ ] Champ `must_change_password` au modèle User
- [ ] Rate limiting (throttling)
- [ ] 2FA (authentification à deux facteurs)
- [ ] Récupération mot de passe par email
- [ ] Webhooks pour actions critiques
- [ ] Alertes Slack/Teams pour actions admin

---

## 🐛 Debug

### Voir les logs
```bash
# Logs généraux
tail -f logs/app.log

# Logs de sécurité
tail -f logs/security.log
```

### Tester les permissions dans le shell Django
```python
python manage.py shell

from accounts.models import User

user = User.objects.get(email='agent@moov.tg')
print(user.has_permission('billing.publish'))
print(user.has_permission('billing.cancel'))

target_user = User.objects.get(email='autre@moov.tg')
print(user.can_manage_user(target_user))
```

---

## ✅ Phase 1 Complète

**Prêt pour Phase 2** : Gestion Contrats & Lignes

Date : 30 juillet 2026
