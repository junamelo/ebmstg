# 🎨 Frontend - Gestion des Utilisateurs

## ✅ Fichiers créés

### 1. Service API (`src/services/userService.js`)
- ✅ Toutes les fonctions d'appel API
- ✅ Constantes USER_STATUS et USER_ROLES
- ✅ Liste complète des permissions
- ✅ Gestion des erreurs

### 2. Page principale (`src/pages/admin/users/UsersManagement.jsx`)
- ✅ Liste des utilisateurs avec cartes
- ✅ Statistiques (Total, Actifs, Inactifs, Admins)
- ✅ Filtres par rôle et statut
- ✅ Recherche par nom/email
- ✅ Actions : Statut, Permissions, Historique, Supprimer
- ✅ Messages flash de succès/erreur

### 3. Modal de création (`src/pages/admin/users/components/CreateUserModal.jsx`)
- ✅ Formulaire complet (prénom, nom, email, username, password)
- ✅ Sélection du rôle et statut
- ✅ Téléphone optionnel
- ✅ Validation côté client
- ✅ Animation fluide

### 4. Modal de changement de statut (`src/pages/admin/users/components/ChangeStatusModal.jsx`)
- ✅ Sélection du nouveau statut avec radio buttons
- ✅ Raison obligatoire
- ✅ Date de fin optionnelle (réactivation auto)
- ✅ Option d'envoi de notification
- ✅ Affichage visuel du statut actuel vs nouveau

## 📋 Fichiers à créer manuellement

Vous devez créer ces 2 derniers fichiers :

### 5. Modal de permissions
**Fichier** : `src/pages/admin/users/components/PermissionsModal.jsx`

```jsx
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { getUserPermissions, managePermission, PERMISSIONS_LIST } from '../../../../services/userService'

export default function PermissionsModal({ isOpen, onClose, user, onSuccess }) {
  const [permissions, setPermissions] = useState(null)
  const [chargement, setChargement] = useState(true)
  
  useEffect(() => {
    if (isOpen && user) {
      chargerPermissions()
    }
  }, [isOpen, user])
  
  const chargerPermissions = async () => {
    try {
      const data = await getUserPermissions(user.id)
      setPermissions(data)
    } catch (error) {
      console.error(error)
    } finally {
      setChargement(false)
    }
  }
  
  const togglePermission = async (permission) => {
    const isActive = permissions.custom_permissions.includes(permission)
    try {
      await managePermission(user.id, {
        permission,
        action: isActive ? 'remove' : 'add'
      })
      await chargerPermissions()
      onSuccess()
    } catch (error) {
      console.error(error)
    }
  }
  
  if (!isOpen || !user) return null
  
  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={onClose}
        />
        
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="relative bg-white dark:bg-zinc-900 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800">
            <h2 className="text-xl font-bold">Gérer les permissions</h2>
          </div>
          
          <div className="px-6 py-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            {chargement ? (
              <div className="text-center py-8">Chargement...</div>
            ) : (
              <div className="space-y-6">
                {Object.entries(PERMISSIONS_LIST).map(([category, { label, permissions: perms }]) => (
                  <div key={category}>
                    <h3 className="font-semibold mb-3">{label}</h3>
                    <div className="space-y-2">
                      {perms.map(perm => {
                        const isFromRole = permissions.role_permissions.includes(perm.key)
                        const isCustom = permissions.custom_permissions.includes(perm.key)
                        const isActive = isFromRole || isCustom
                        
                        return (
                          <label
                            key={perm.key}
                            className="flex items-center gap-3 p-3 border rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800"
                          >
                            <input
                              type="checkbox"
                              checked={isActive}
                              disabled={isFromRole}
                              onChange={() => togglePermission(perm.key)}
                              className="w-4 h-4"
                            />
                            <div className="flex-1">
                              <p className="text-sm font-medium">{perm.label}</p>
                              {isFromRole && (
                                <p className="text-xs text-zinc-500">Hérité du rôle</p>
                              )}
                            </div>
                          </label>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <div className="px-6 py-4 border-t border-zinc-200 dark:border-zinc-800">
            <button onClick={onClose} className="px-4 py-2 bg-zinc-100 rounded-lg">
              Fermer
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
```

### 6. Modal d'historique
**Fichier** : `src/pages/admin/users/components/StatusHistoryModal.jsx`

```jsx
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { getUserStatusHistory, USER_STATUS } from '../../../../services/userService'

export default function StatusHistoryModal({ isOpen, onClose, user }) {
  const [history, setHistory] = useState([])
  const [chargement, setChargement] = useState(true)
  
  useEffect(() => {
    if (isOpen && user) {
      chargerHistorique()
    }
  }, [isOpen, user])
  
  const chargerHistorique = async () => {
    try {
      const data = await getUserStatusHistory(user.id)
      setHistory(data)
    } catch (error) {
      console.error(error)
    } finally {
      setChargement(false)
    }
  }
  
  if (!isOpen || !user) return null
  
  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={onClose}
        />
        
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="relative bg-white dark:bg-zinc-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
        >
          <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800">
            <h2 className="text-xl font-bold">Historique des statuts</h2>
          </div>
          
          <div className="px-6 py-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            {chargement ? (
              <div className="text-center py-8">Chargement...</div>
            ) : history.length === 0 ? (
              <div className="text-center py-8 text-zinc-500">Aucun historique</div>
            ) : (
              <div className="space-y-4">
                {history.map((item, idx) => {
                  const oldStatus = USER_STATUS[item.old_status]
                  const newStatus = USER_STATUS[item.new_status]
                  
                  return (
                    <div key={idx} className="flex gap-4 p-4 border border-zinc-200 dark:border-zinc-800 rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-2xl">
                          {newStatus.icon}
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="px-2 py-0.5 rounded text-xs" style={{ background: `${oldStatus.color}20`, color: oldStatus.color }}>
                            {oldStatus.label}
                          </span>
                          <span>→</span>
                          <span className="px-2 py-0.5 rounded text-xs" style={{ background: `${newStatus.color}20`, color: newStatus.color }}>
                            {newStatus.label}
                          </span>
                        </div>
                        <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">{item.reason}</p>
                        <div className="flex items-center gap-4 text-xs text-zinc-500">
                          <span>👤 Par {item.changed_by_name}</span>
                          <span>📅 {new Date(item.changed_at).toLocaleString('fr-FR')}</span>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
          
          <div className="px-6 py-4 border-t border-zinc-200 dark:border-zinc-800">
            <button onClick={onClose} className="px-4 py-2 bg-zinc-100 rounded-lg">
              Fermer
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
```

## 🔧 Configuration à faire

### 1. Ajouter la route dans le router

**Fichier** : `src/App.jsx` (ou votre fichier de routes)

```jsx
import UsersManagement from './pages/admin/users/UsersManagement'

// Dans vos routes protégées Admin
<Route path="/admin/users" element={<UsersManagement />} />
```

### 2. Ajouter le lien dans la Sidebar

**Fichier** : `src/components/layout/Sidebar.jsx`

```jsx
const menusAdmin = [
  { path: '/admin/dashboard', label: 'Tableau de bord', icon: <IconDashboard /> },
  { path: '/admin/users', label: 'Utilisateurs', icon: <IconUsers /> },  // ⭐ NOUVEAU
  { path: '/admin/comptes', label: 'Gestion comptes', icon: <IconComptes /> },
]

// Ajouter l'icône
const IconUsers = () => <i className="ti ti-users" style={{ fontSize: 18 }} />
```

## 🎨 Fonctionnalités

### Page principale
- ✅ Vue en cartes des utilisateurs
- ✅ 4 KPI en haut (Total, Actifs, Inactifs, Admins)
- ✅ Filtres : Recherche, Rôle, Statut
- ✅ Actions par utilisateur : Statut, Permissions, Historique, Supprimer

### Modal de création
- ✅ Formulaire complet en 4 sections
- ✅ Validation des champs obligatoires
- ✅ Animation d'entrée/sortie

### Modal de statut
- ✅ Sélection visuelle avec radio buttons
- ✅ Raison obligatoire
- ✅ Date de réactivation optionnelle
- ✅ Toggle notification email

### Modal de permissions
- ✅ Permissions groupées par catégorie
- ✅ Checkboxes interactives
- ✅ Distinction permissions rôle vs custom
- ✅ Permissions rôle grisées (non modifiables)

### Modal d'historique
- ✅ Timeline des changements
- ✅ Affichage visuel ancien → nouveau statut
- ✅ Raison et auteur du changement
- ✅ Date et heure précises

## 🚀 Pour tester

1. **Démarrer le backend** :
```bash
cd Back
python manage.py runserver
```

2. **Démarrer le frontend** :
```bash
cd Front
npm run dev
```

3. **Se connecter en admin** et aller sur `/admin/users`

## 📝 Notes

- Les couleurs s'adaptent automatiquement au rôle de l'utilisateur
- Les animations sont fluides avec Framer Motion
- Le design est cohérent avec le reste de l'application
- Mode dark supporté (si implémenté globalement)

---

**Date de création** : 23/07/2026  
**Version** : 1.0.0
