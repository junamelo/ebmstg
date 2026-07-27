# 📦 Instructions de Migration - Gestion des Utilisateurs

## ⚠️ Importantes modifications apportées

1. ✅ Nouveau rôle : `CHEF_FACTURATION`
2. ✅ Nouveau champ : `status` (ACTIF, INACTIF, SUSPENDU, EN_ATTENTE, BLOQUE)
3. ✅ Nouveau champ : `custom_permissions` (JSONField)
4. ✅ Nouveaux champs de traçabilité (created_by, status_changed_by, etc.)
5. ✅ Nouveau modèle : `StatusHistory`

## 🚀 Étapes pour appliquer les modifications

### 1. Créer les migrations

```bash
cd Back
python manage.py makemigrations accounts
```

Vous devriez voir :
```
Migrations for 'accounts':
  accounts/migrations/0XXX_add_user_management_fields.py
    - Add field status to user
    - Add field custom_permissions to user
    - Add field status_changed_at to user
    - Add field status_changed_by to user
    - Add field status_reason to user
    - Add field status_end_date to user
    - Add field created_by to user
    - Add field last_login_ip to user
    - Create model StatusHistory
    - Alter field role on user
```

### 2. Appliquer les migrations

```bash
python manage.py migrate accounts
```

### 3. Vérifier les migrations

```bash
python manage.py showmigrations accounts
```

Toutes les migrations doivent être cochées [X].

## 🔄 Migration des données existantes

### Si vous avez déjà des utilisateurs dans la base de données :

1. Tous les utilisateurs existants auront automatiquement :
   - `status = 'ACTIF'` (par défaut)
   - `custom_permissions = []` (liste vide)
   - Les autres champs seront NULL

2. Pour mettre à jour un utilisateur existant en CHEF_FACTURATION :

```bash
python manage.py shell
```

```python
from accounts.models import User

# Trouver l'utilisateur
user = User.objects.get(email='chef@moov-africa.tg')

# Changer le rôle
user.role = 'CHEF_FACTURATION'
user.status = 'ACTIF'
user.save()

print(f"✅ {user.email} est maintenant CHEF_FACTURATION")
```

## 🧪 Tester les nouveaux endpoints

### 1. Démarrer le serveur
```bash
python manage.py runserver
```

### 2. Aller sur Swagger
```
http://localhost:8000/api/swagger/
```

### 3. Tester les nouveaux endpoints

Vous devriez voir les nouveaux endpoints :
- `POST /api/accounts/users/` - Créer un utilisateur
- `GET /api/accounts/users/` - Liste des utilisateurs
- `GET /api/accounts/users/{id}/` - Détail d'un utilisateur
- `POST /api/accounts/users/{id}/change_status/` - Changer le statut
- `GET /api/accounts/users/{id}/status_history/` - Historique des statuts
- `POST /api/accounts/users/{id}/assign_permission/` - Gérer les permissions
- `GET /api/accounts/users/{id}/permissions/` - Voir les permissions
- `POST /api/accounts/users/{id}/reset_password/` - Réinitialiser le mot de passe

## ❌ En cas d'erreur

### Erreur : "no such table: status_history"
```bash
python manage.py migrate accounts --fake-initial
python manage.py migrate accounts
```

### Erreur : "column status does not exist"
```bash
python manage.py migrate accounts zero
python manage.py migrate accounts
```

### Erreur : "UNIQUE constraint failed"
Si vous avez des données de test :
```bash
python manage.py flush  # ⚠️ Supprime toutes les données
python manage.py migrate accounts
```

## 📊 Créer des données de test

```python
from accounts.models import User

# Créer un super admin
admin = User.objects.create_user(
    username='admin',
    email='admin@moov.tg',
    password='admin123',
    first_name='Admin',
    last_name='Système',
    role='SUPER_ADMIN',
    status='ACTIF'
)

# Créer un chef
chef = User.objects.create_user(
    username='chef',
    email='chef@moov-africa.tg',
    password='chef123',
    first_name='Chef',
    last_name='Service',
    role='CHEF_FACTURATION',
    status='ACTIF',
    created_by=admin
)

# Créer un agent
agent = User.objects.create_user(
    username='agent',
    email='agent@moov-africa.tg',
    password='agent123',
    first_name='Agent',
    last_name='Test',
    role='AGENT_FACTURATION',
    status='ACTIF',
    created_by=chef
)

print("✅ Utilisateurs de test créés avec succès")
```

## ✅ Vérification finale

Après la migration, vérifiez que :

1. ✅ Le serveur démarre sans erreur
2. ✅ Swagger affiche les nouveaux endpoints
3. ✅ Vous pouvez vous connecter avec vos utilisateurs existants
4. ✅ Les nouveaux champs apparaissent dans l'admin Django (`/admin/`)

---

**Prochaine étape** : Implémenter le Frontend (pages de gestion pour l'admin)
