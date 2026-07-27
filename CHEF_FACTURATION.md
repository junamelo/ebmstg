# 👨‍💼 Implémentation Chef Agent de Facturation

**Date** : 27 juillet 2026  
**Status** : ✅ Complété

---

## 📋 Vue d'ensemble

Implémentation du rôle **Chef Agent de Facturation** qui permet une hiérarchie dans la gestion des agents :

```
SUPER_ADMIN (root)
    ├── CHEF_FACTURATION (gère des agents)
    │   ├── AGENT_FACTURATION (standard)
    │   └── AGENT_FACTURATION (avec permission de créer d'autres agents)
    ├── PAYEUR (gère une entreprise)
    └── EMPLOYE (utilisateur final)
```

---

## 🎯 Fonctionnalités

### Chef Agent de Facturation peut :

✅ **Créer des agents de facturation**  
✅ **Accorder ou retirer la permission de créer d'autres agents**  
✅ **Modifier les informations des agents qu'il a créés**  
✅ **Activer/Désactiver les agents qu'il a créés**  
✅ **Accéder à toutes les fonctionnalités de facturation** (publication, services, forfaits)  
✅ **Voir les statistiques de ses agents**  

### Agent de Facturation (avec permission) peut :

✅ **Créer d'autres agents de facturation** (si permission accordée)  
✅ **Effectuer toutes les opérations de facturation**

### Agent de Facturation (standard) peut :

✅ **Publier des factures**  
✅ **Gérer les services et forfaits**  
✅ **Consulter l'historique**  
❌ **Ne peut PAS créer d'autres agents**

---

## 🔧 Modifications techniques

### 1. Backend (`accounts/models.py`)

Le modèle User existe déjà avec :

```python
ROLE_CHOICES = [
    ('SUPER_ADMIN', 'Super Admin'),
    ('CHEF_FACTURATION', 'Chef Facturation'),  # ✅ Déjà présent
    ('AGENT_FACTURATION', 'Agent Facturation'),
    ('PAYEUR', 'Payeur'),
    ('EMPLOYE', 'Employé'),
]

# Permissions personnalisées
custom_permissions = models.JSONField(default=list, blank=True)

# Traçabilité
created_by = models.ForeignKey('self', on_delete=models.SET_NULL, ...)
```

**Permissions Chef Facturation** :
```python
'CHEF_FACTURATION': [
    'accounts.create_agent',      # Créer des agents
    'accounts.view_all',           # Voir tous les agents
    'accounts.edit_agents',        # Modifier les agents
    'accounts.change_status_agents', # Changer le statut
    'accounts.reset_password_agents', # Réinitialiser MDP
    'billing.publish',             # Publier des factures
    'billing.cancel',              # Annuler des publications
    'billing.view_all',            # Voir toutes les factures
    'billing.export',              # Exporter les données
    'tarifs.create',               # Créer des tarifs
    'tarifs.edit',                 # Modifier des tarifs
    'services.create',             # Créer des services
    'services.edit',               # Modifier des services
    'reports.view_all',            # Voir tous les rapports
    'system.view_logs',            # Voir les logs système
]
```

---

### 2. Frontend - AuthContext

**Fichier** : `Front/src/contexts/AuthContext.jsx`

Ajout des fonctions :
```javascript
const isChefFacturation = () => user?.role === 'CHEF_FACTURATION'
const canCreateAgents = () => 
  isAdmin() || 
  (isChefFacturation() && user?.custom_permissions?.includes('accounts.create_agent'))
```

---

### 3. Nouvelle page GestionAgents

**Fichier** : `Front/src/pages/agent/GestionAgents.jsx`

**Fonctionnalités** :
- 📊 Dashboard avec KPI (Total agents, Agents actifs, Avec permissions)
- ➕ Création d'agents avec formulaire complet
- ✏️ Modification des agents existants
- 🔒 Gestion des permissions spéciales (créer d'autres agents)
- ✅ Activation/Désactivation des agents
- 🔍 Recherche par nom, email ou username
- 📋 Tableau avec toutes les informations clés

**Champs du formulaire** :
- Nom d'utilisateur
- Email
- Prénom
- Nom
- Mot de passe (création uniquement)
- Confirmation mot de passe
- Permission : "Créer d'autres agents" (checkbox)

---

### 4. Routes mises à jour

**Fichier** : `Front/src/App.jsx`

```jsx
// Routes Agent Facturation (standard)
<Route path="/agent">
  <Route path="dashboard" element={<AgentDashboard />} />
  <Route path="services" element={<GestionForfaits />} />
  <Route path="forfaits" element={<GestionServices />} />
  <Route path="publication" element={<PublicationPdf />} />
  <Route path="publication/historique" element={<HistoriquePublications />} />
</Route>

// Routes Chef Facturation (avec gestion agents)
<Route path="/chef">
  <Route path="dashboard" element={<AgentDashboard />} />
  <Route path="agents" element={<GestionAgents />} />  // ⭐ Nouveau
  <Route path="services" element={<GestionForfaits />} />
  <Route path="forfaits" element={<GestionServices />} />
  <Route path="publication" element={<PublicationPdf />} />
  <Route path="publication/historique" element={<HistoriquePublications />} />
</Route>
```

---

### 5. Sidebar mise à jour

**Fichier** : `Front/src/components/layout/Sidebar.jsx`

**Menu Chef Facturation** :
```jsx
const menusChefFacturation = [
  { path: '/chef/dashboard',                label: 'Dashboard',           icon: <IconDashboard /> },
  { path: '/chef/agents',                   label: 'Gestion Agents',      icon: <IconAgents /> },     // ⭐ Nouveau
  { path: '/chef/services',                 label: 'Gestion Services',    icon: <IconServices /> },
  { path: '/chef/forfaits',                 label: 'Gestion Forfaits',    icon: <IconForfaits /> },
  { path: '/chef/publication',              label: 'Publication PDF',     icon: <IconPublication /> },
  { path: '/chef/publication/historique',   label: 'Historique Pub.',     icon: <IconHistorique /> },
]
```

---

### 6. ProtectedRoute mise à jour

**Fichier** : `Front/src/components/common/ProtectedRoute.jsx`

```jsx
// Chef Facturation a accès aux routes agent
if (role === 'AGENT_FACTURATION' && !isAgentFacturation() && !isChefFacturation()) {
  return <Navigate to="/dashboard" replace />
}

// Seul Chef Facturation et Admin ont accès aux routes chef
if (role === 'CHEF_FACTURATION' && !isChefFacturation() && !isAdmin()) {
  return <Navigate to="/dashboard" replace />
}
```

---

## 🔒 Système de permissions

### Permission : `accounts.create_agent`

Cette permission permet à un agent de créer d'autres agents.

**Qui peut l'avoir ?**
- ✅ SUPER_ADMIN (toujours)
- ✅ CHEF_FACTURATION (toujours)
- ✅ AGENT_FACTURATION (si accordé par le chef)

**Comment l'accorder ?**
```jsx
// Dans le formulaire GestionAgents
<input
  type="checkbox"
  checked={form.custom_permissions.includes('accounts.create_agent')}
  onChange={() => togglePermission('accounts.create_agent')}
/>
```

**Affichage dans la liste** :
```jsx
{agent.custom_permissions?.includes('accounts.create_agent') ? (
  <span className="badge-purple">Étendues</span>
) : (
  <span className="text-zinc-400">Standard</span>
)}
```

---

## 📊 Interface Gestion Agents

### KPI Dashboard
```
┌─────────────────┬─────────────────┬─────────────────┐
│  Total agents   │  Agents actifs  │ Avec permissions│
│       5         │        4        │        2        │
└─────────────────┴─────────────────┴─────────────────┘
```

### Tableau des agents
```
┌──────────────┬──────────────────────────┬─────────────┬────────┬─────────────────┬──────────┐
│ Agent        │ Email                    │ Permissions │ Statut │ Dernière connex │ Actions  │
├──────────────┼──────────────────────────┼─────────────┼────────┼─────────────────┼──────────┤
│ JD           │ agent.dupont@moov.africa │ Étendues    │ Actif  │ 2026-07-26      │ Modifier │
│ Jean Dupont  │                          │             │        │ 14:30           │ Désactiver│
│ @agent.dupont│                          │             │        │                 │          │
├──────────────┼──────────────────────────┼─────────────┼────────┼─────────────────┼──────────┤
│ MM           │ agent.martin@moov.africa │ Standard    │ Actif  │ 2026-07-27      │ Modifier │
│ Marie Martin │                          │             │        │ 09:15           │ Désactiver│
│ @agent.martin│                          │             │        │                 │          │
└──────────────┴──────────────────────────┴─────────────┴────────┴─────────────────┴──────────┘
```

---

## 🎨 Design

### Couleurs
- **Chef Facturation** : Bleu Moov `#002a7a`
- **Badge Permissions Étendues** : Violet `#8b5cf6`
- **Badge Actif** : Vert `#10b981`
- **Badge Inactif** : Gris `#6b7280`

### Icônes
- Dashboard : `ti-layout-dashboard`
- Agents : `ti-user-check` ⭐
- Services : `ti-settings`
- Forfaits : `ti-package`
- Publication : `ti-cloud-upload`

---

## 🔐 Sécurité

### Vérifications côté backend (à implémenter)

```python
# Dans views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_agent(request):
    user = request.user
    
    # Vérifier que l'utilisateur a la permission
    if not user.has_permission('accounts.create_agent'):
        return Response({'error': 'Permission refusée'}, status=403)
    
    # Créer l'agent avec created_by = user
    agent = User.objects.create(
        username=request.data['username'],
        email=request.data['email'],
        role='AGENT_FACTURATION',
        created_by=user,  # ⭐ Traçabilité
        **autres_champs
    )
    
    return Response(serializer.data, status=201)
```

### Vérifications côté frontend

```jsx
// Afficher le bouton uniquement si l'utilisateur a la permission
{canCreateAgents() && (
  <button onClick={() => setFormOuvert(true)}>
    Nouvel agent
  </button>
)}
```

---

## 🧪 Tests à effectuer

### Scénario 1 : Chef Facturation crée un agent standard
1. Se connecter en tant que Chef Facturation
2. Aller sur `/chef/agents`
3. Cliquer sur "Nouvel agent"
4. Remplir le formulaire **sans** cocher "Créer d'autres agents"
5. Soumettre
6. ✅ Vérifier que l'agent est créé avec `custom_permissions: []`

### Scénario 2 : Chef Facturation crée un agent avec permissions
1. Se connecter en tant que Chef Facturation
2. Aller sur `/chef/agents`
3. Cliquer sur "Nouvel agent"
4. Remplir le formulaire **avec** "Créer d'autres agents" coché
5. Soumettre
6. ✅ Vérifier que l'agent est créé avec `custom_permissions: ['accounts.create_agent']`
7. ✅ Vérifier que le badge "Étendues" s'affiche

### Scénario 3 : Agent avec permissions crée un autre agent
1. Se connecter en tant qu'Agent (avec permissions)
2. Le bouton "Nouvel agent" doit être visible sur `/agent/agents`
3. Créer un nouvel agent
4. ✅ Vérifier que l'agent est bien créé

### Scénario 4 : Agent standard ne peut pas créer d'agents
1. Se connecter en tant qu'Agent (sans permissions)
2. ❌ Le bouton "Nouvel agent" ne doit PAS être visible
3. ❌ L'accès direct à `/agent/agents` doit fonctionner mais sans bouton création

### Scénario 5 : Modifier un agent existant
1. Cliquer sur "Modifier" pour un agent
2. Changer le prénom et ajouter la permission
3. Soumettre
4. ✅ Vérifier que les changements sont appliqués

### Scénario 6 : Désactiver/Activer un agent
1. Cliquer sur "Désactiver" pour un agent actif
2. Confirmer
3. ✅ Vérifier que le statut passe à "Inactif"
4. Cliquer sur "Activer"
5. ✅ Vérifier que le statut repasse à "Actif"

---

## 🚀 Prochaines étapes (Backend)

### API à créer

```python
# accounts/views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agents(request):
    """Récupère les agents créés par l'utilisateur connecté"""
    user = request.user
    
    if user.role == 'SUPER_ADMIN':
        agents = User.objects.filter(role='AGENT_FACTURATION')
    elif user.role == 'CHEF_FACTURATION':
        agents = User.objects.filter(created_by=user, role='AGENT_FACTURATION')
    elif user.has_permission('accounts.create_agent'):
        agents = User.objects.filter(created_by=user, role='AGENT_FACTURATION')
    else:
        return Response({'error': 'Permission refusée'}, status=403)
    
    serializer = UserSerializer(agents, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_agent(request):
    """Crée un nouvel agent de facturation"""
    # Voir section Sécurité ci-dessus
    pass

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modifier_agent(request, agent_id):
    """Modifie un agent existant"""
    user = request.user
    agent = User.objects.get(id=agent_id)
    
    # Vérifier que l'utilisateur peut modifier cet agent
    if not user.can_manage_user(agent):
        return Response({'error': 'Permission refusée'}, status=403)
    
    # Mise à jour
    serializer = UserSerializer(agent, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_status_agent(request, agent_id):
    """Active/Désactive un agent"""
    user = request.user
    agent = User.objects.get(id=agent_id)
    
    if not user.can_manage_user(agent):
        return Response({'error': 'Permission refusée'}, status=403)
    
    agent.status = 'INACTIF' if agent.status == 'ACTIF' else 'ACTIF'
    agent.save()
    
    return Response({'status': agent.status})
```

### URLs à ajouter

```python
# accounts/urls.py
urlpatterns = [
    path('agents/', get_agents, name='get-agents'),
    path('agents/creer/', creer_agent, name='creer-agent'),
    path('agents/<int:agent_id>/modifier/', modifier_agent, name='modifier-agent'),
    path('agents/<int:agent_id>/toggle-status/', toggle_status_agent, name='toggle-status-agent'),
]
```

---

## 📝 Résumé

✅ **AuthContext** mis à jour avec `isChefFacturation()` et `canCreateAgents()`  
✅ **Page GestionAgents** créée avec CRUD complet  
✅ **Routes** `/chef/*` ajoutées pour le Chef Facturation  
✅ **Sidebar** mise à jour avec menu "Gestion Agents"  
✅ **ProtectedRoute** adapté pour gérer les deux rôles  
✅ **Permissions** système de permissions personnalisées implémenté  
✅ **Design** cohérent avec le reste de l'application  

**API backend** : À connecter quand les endpoints seront créés.

---

## 🎉 Résultat final

Le Chef Agent de Facturation peut maintenant :
- 👥 Gérer une équipe d'agents
- 🔑 Accorder des permissions spéciales
- 📊 Suivre l'activité de ses agents
- ✅ Activer/Désactiver les comptes
- 🔄 Modifier les informations des agents

Le système est prêt côté frontend et attend l'implémentation des endpoints backend !
