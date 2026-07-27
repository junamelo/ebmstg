# 🔐 API de Gestion des Utilisateurs

## 📋 Nouveaux Endpoints

### Base URL
```
/api/accounts/
```

## 🎯 Endpoints Disponibles

### 1. **Liste des utilisateurs**
```http
GET /api/accounts/users/
```
**Permissions** : Admin ou Chef (voit seulement ses agents)

**Réponse** :
```json
[
  {
    "id": 1,
    "email": "k.attiogbe@moov-africa.tg",
    "first_name": "Koffi",
    "last_name": "ATTIOGBE",
    "role": "AGENT_FACTURATION",
    "status": "ACTIF",
    "telephone": "+228 XX XX XX XX",
    "est_actif": true,
    "created_by_name": "Admin Système",
    "date_creation": "2024-03-15T10:30:00Z",
    "last_login": "2026-07-23T14:30:00Z"
  }
]
```

---

### 2. **Détail d'un utilisateur**
```http
GET /api/accounts/users/{id}/
```
**Permissions** : Admin ou Chef (pour ses agents)

---

### 3. **Créer un utilisateur**
```http
POST /api/accounts/users/
```
**Permissions** : 
- Admin (peut créer tout rôle)
- Chef (peut créer seulement AGENT_FACTURATION)

**Corps de la requête** :
```json
{
  "email": "nouveau@moov-africa.tg",
  "username": "nouveau",
  "password": "MotDePasse123!",
  "first_name": "Nouveau",
  "last_name": "AGENT",
  "role": "AGENT_FACTURATION",
  "status": "ACTIF",
  "telephone": "+228 90 XX XX XX",
  "custom_permissions": []
}
```

---

### 4. **Modifier un utilisateur**
```http
PUT /api/accounts/users/{id}/
PATCH /api/accounts/users/{id}/
```
**Permissions** : Admin ou Chef (pour ses agents)

---

### 5. **Supprimer un utilisateur**
```http
DELETE /api/accounts/users/{id}/
```
**Permissions** : Admin uniquement

---

### 6. **Changer le statut d'un utilisateur** ⭐
```http
POST /api/accounts/users/{id}/change_status/
```
**Permissions** : Admin ou Chef (pour ses agents)

**Corps de la requête** :
```json
{
  "new_status": "INACTIF",
  "reason": "Congé annuel jusqu'au 30/07/2026",
  "end_date": "2026-07-30T00:00:00Z",
  "send_notification": true
}
```

**Statuts disponibles** :
- `ACTIF` - Utilisateur actif
- `INACTIF` - Désactivé temporairement
- `SUSPENDU` - Suspendu (enquête)
- `EN_ATTENTE` - En attente d'activation
- `BLOQUE` - Bloqué définitivement

**Réponse** :
```json
{
  "message": "Statut modifié avec succès",
  "user": {
    "id": 1,
    "status": "INACTIF",
    "status_reason": "Congé annuel jusqu'au 30/07/2026",
    "status_changed_at": "2026-07-23T10:00:00Z",
    "status_changed_by_name": "Chef Service",
    "status_end_date": "2026-07-30T00:00:00Z"
  }
}
```

---

### 7. **Historique des changements de statut**
```http
GET /api/accounts/users/{id}/status_history/
```
**Permissions** : Admin, Chef (pour ses agents), ou l'utilisateur lui-même

**Réponse** :
```json
[
  {
    "id": 1,
    "user": 5,
    "user_name": "Koffi ATTIOGBE",
    "old_status": "ACTIF",
    "new_status": "INACTIF",
    "changed_by": 2,
    "changed_by_name": "Chef Service",
    "changed_at": "2026-07-23T10:00:00Z",
    "reason": "Congé annuel",
    "end_date": "2026-07-30T00:00:00Z"
  }
]
```

---

### 8. **Gérer les permissions** ⭐
```http
POST /api/accounts/users/{id}/assign_permission/
```
**Permissions** : Admin uniquement

**Corps de la requête** :
```json
{
  "permission": "billing.cancel",
  "action": "add"
}
```

**Actions** : `add` ou `remove`

**Réponse** :
```json
{
  "message": "Permission \"billing.cancel\" ajoutée",
  "user": {
    "id": 1,
    "custom_permissions": ["billing.cancel", "reports.export"]
  }
}
```

---

### 9. **Voir toutes les permissions d'un utilisateur**
```http
GET /api/accounts/users/{id}/permissions/
```
**Permissions** : Admin ou Chef

**Réponse** :
```json
{
  "role": "AGENT_FACTURATION",
  "role_permissions": [
    "billing.publish",
    "billing.view_all",
    "tarifs.create",
    "services.create",
    "reports.view_all"
  ],
  "custom_permissions": [
    "billing.cancel",
    "reports.export"
  ],
  "all_permissions": [
    "billing.publish",
    "billing.view_all",
    "tarifs.create",
    "services.create",
    "reports.view_all",
    "billing.cancel",
    "reports.export"
  ]
}
```

---

### 10. **Réinitialiser le mot de passe**
```http
POST /api/accounts/users/{id}/reset_password/
```
**Permissions** : Admin ou Chef (pour ses agents)

**Corps de la requête** :
```json
{
  "new_password": "NouveauMotDePasse123!"
}
```

**Réponse** :
```json
{
  "message": "Mot de passe réinitialisé avec succès"
}
```

---

## 📊 Permissions disponibles

### Gestion des comptes
- `accounts.create_admin` - Créer des admins
- `accounts.create_chef` - Créer des chefs de service
- `accounts.create_agent` - Créer des agents
- `accounts.create_payeur` - Créer des payeurs
- `accounts.view_all` - Voir tous les comptes
- `accounts.edit_all` - Modifier tous les comptes
- `accounts.edit_agents` - Modifier les agents uniquement
- `accounts.delete_all` - Supprimer des comptes
- `accounts.change_status` - Changer le statut
- `accounts.change_status_agents` - Changer le statut des agents uniquement
- `accounts.reset_password` - Réinitialiser les mots de passe
- `accounts.reset_password_agents` - Réinitialiser MDP des agents uniquement
- `accounts.assign_permissions` - Attribuer des permissions

### Facturation
- `billing.publish` - Publier des factures
- `billing.cancel` - Annuler des factures
- `billing.regenerate` - Régénérer des factures
- `billing.view_all` - Voir toutes les factures
- `billing.view_own` - Voir ses propres factures
- `billing.export` - Exporter les factures
- `billing.export_own` - Exporter ses propres factures

### Forfaits et services
- `tarifs.create` - Créer des forfaits
- `tarifs.edit` - Modifier des forfaits
- `tarifs.activate` - Activer/Désactiver des forfaits
- `tarifs.delete` - Supprimer des forfaits
- `services.create` - Créer des services
- `services.edit` - Modifier des services
- `services.activate` - Activer/Désactiver des services

### Rapports
- `reports.view_all` - Voir tous les rapports
- `reports.export` - Exporter des rapports

### Système
- `system.view_logs` - Voir les logs système
- `system.edit_settings` - Modifier les paramètres système
- `system.backup` - Gérer les sauvegardes

---

## 🏗️ Modifications du modèle User

### Nouveaux champs
```python
role = CharField(max_length=20)  # Ajout de 'CHEF_FACTURATION'
status = CharField(max_length=20)  # Nouveau champ
custom_permissions = JSONField(default=list)  # Nouveau champ
status_changed_at = DateTimeField(null=True)  # Nouveau champ
status_changed_by = ForeignKey(User, null=True)  # Nouveau champ
status_reason = TextField(blank=True)  # Nouveau champ
status_end_date = DateTimeField(null=True)  # Nouveau champ
created_by = ForeignKey(User, null=True)  # Nouveau champ
last_login_ip = GenericIPAddressField(null=True)  # Nouveau champ
```

### Nouveau modèle StatusHistory
```python
user = ForeignKey(User)
old_status = CharField(max_length=20)
new_status = CharField(max_length=20)
changed_by = ForeignKey(User, null=True)
changed_at = DateTimeField(auto_now_add=True)
reason = TextField()
end_date = DateTimeField(null=True)
```

---

## 🚀 Migration

Pour appliquer les modifications :

```bash
cd Back
python manage.py makemigrations accounts
python manage.py migrate accounts
```

---

## 🔒 Règles de sécurité

1. **SUPER_ADMIN** :
   - Peut gérer tous les utilisateurs
   - Peut créer n'importe quel rôle
   - Peut modifier toutes les permissions

2. **CHEF_FACTURATION** :
   - Peut créer/modifier/supprimer seulement ses AGENT_FACTURATION
   - Peut changer le statut de ses agents
   - Peut réinitialiser les mots de passe de ses agents
   - Ne peut PAS modifier les permissions

3. **AGENT_FACTURATION** :
   - Ne peut gérer aucun utilisateur
   - Peut voir son propre profil

4. **Connexion bloquée** :
   - Si `status != 'ACTIF'`, la connexion est refusée
   - Message d'erreur adapté au statut

---

## 📝 Notes importantes

1. **Réactivation automatique** :
   - Si `status_end_date` est défini, créer une tâche cron pour réactiver automatiquement

2. **Notifications** :
   - Implémenter l'envoi d'emails lors des changements de statut
   - Implémenter l'envoi d'emails lors de la réinitialisation de mot de passe

3. **Logs** :
   - Tous les changements de statut sont enregistrés dans `StatusHistory`
   - Traçabilité complète des actions

---

**Date de création** : 23/07/2026  
**Version** : 1.0.0
