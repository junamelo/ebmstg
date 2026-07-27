import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { getUsers, deleteUser } from '../../../services/userService'
import { USER_STATUS, USER_ROLES } from '../../../services/userService'
import CreateUserModal from './components/CreateUserModal'
import ChangeRoleModal from './components/ChangeRoleModal'
import ChangeStatusModal from './components/ChangeStatusModal'
import PermissionsModal from './components/PermissionsModal'
import StatusHistoryModal from './components/StatusHistoryModal'

export default function UsersManagement() {
  const [users, setUsers] = useState([])
  const [chargement, setChargement] = useState(true)
  const [recherche, setRecherche] = useState('')
  const [filtreRole, setFiltreRole] = useState('tous')
  const [filtreStatus, setFiltreStatus] = useState('tous')
  const [message, setMessage] = useState(null)

  // Modals
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [roleModalOpen, setRoleModalOpen] = useState(false)
  const [statusModalOpen, setStatusModalOpen] = useState(false)
  const [permissionsModalOpen, setPermissionsModalOpen] = useState(false)
  const [historyModalOpen, setHistoryModalOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)

  useEffect(() => {
    chargerUtilisateurs()
  }, [])

  const chargerUtilisateurs = async () => {
    try {
      setChargement(true)
      const data = await getUsers()
      setUsers(data)
    } catch (error) {
      afficherMessage('error', 'Erreur lors du chargement des utilisateurs')
    } finally {
      setChargement(false)
    }
  }

  const afficherMessage = (type, texte) => {
    setMessage({ type, texte })
    setTimeout(() => setMessage(null), 5000)
  }

  const handleDelete = async (user) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer ${user.first_name} ${user.last_name} ?`)) {
      return
    }

    try {
      await deleteUser(user.id)
      afficherMessage('success', 'Utilisateur supprimé avec succès')
      chargerUtilisateurs()
    } catch (error) {
      afficherMessage('error', 'Erreur lors de la suppression')
    }
  }

  const openRoleModal = (user) => {
    setSelectedUser(user)
    setRoleModalOpen(true)
  }

  const openStatusModal = (user) => {
    setSelectedUser(user)
    setStatusModalOpen(true)
  }

  const openPermissionsModal = (user) => {
    setSelectedUser(user)
    setPermissionsModalOpen(true)
  }

  const openHistoryModal = (user) => {
    setSelectedUser(user)
    setHistoryModalOpen(true)
  }

  // Filtrage des utilisateurs
  const usersFiltres = users.filter(user => {
    const matchRecherche = recherche === '' || 
      user.first_name.toLowerCase().includes(recherche.toLowerCase()) ||
      user.last_name.toLowerCase().includes(recherche.toLowerCase()) ||
      user.email.toLowerCase().includes(recherche.toLowerCase())
    
    const matchRole = filtreRole === 'tous' || user.role === filtreRole
    const matchStatus = filtreStatus === 'tous' || user.status === filtreStatus
    
    return matchRecherche && matchRole && matchStatus
  })

  // Statistiques
  const stats = {
    total: users.length,
    actifs: users.filter(u => u.status === 'ACTIF').length,
    inactifs: users.filter(u => u.status !== 'ACTIF').length,
    admins: users.filter(u => u.role === 'SUPER_ADMIN' || u.role === 'CHEF_FACTURATION').length,
  }

  if (chargement) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-zinc-300 border-t-[#002a7a] rounded-full animate-spin" />
          <span className="text-sm text-zinc-600 dark:text-zinc-400">Chargement...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white mb-2">
            Gestion des Utilisateurs
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            Gérez les comptes, permissions et statuts des utilisateurs
          </p>
        </div>
        <button
          onClick={() => setCreateModalOpen(true)}
          className="px-4 py-2 bg-[#002a7a] hover:bg-[#003087] text-white rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Nouvel utilisateur
        </button>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Total utilisateurs', value: stats.total, color: '#002a7a', icon: '👥' },
          { label: 'Actifs', value: stats.actifs, color: '#10b981', icon: '🟢' },
          { label: 'Inactifs', value: stats.inactifs, color: '#f59e0b', icon: '🟡' },
          { label: 'Administrateurs', value: stats.admins, color: '#dc2626', icon: '🛡️' },
        ].map((stat, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
          >
            <div className="flex items-center gap-3">
              <div className="text-3xl">{stat.icon}</div>
              <div>
                <p className="text-2xl font-bold text-zinc-900 dark:text-white">{stat.value}</p>
                <p className="text-sm text-zinc-500 dark:text-zinc-400">{stat.label}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Message Flash */}
      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`rounded-lg p-4 ${
              message.type === 'success' 
                ? 'bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/30 text-emerald-800 dark:text-emerald-300' 
                : 'bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/30 text-rose-800 dark:text-rose-300'
            }`}
          >
            {message.texte}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filtres et recherche */}
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
        <div className="flex flex-wrap items-center gap-4">
          {/* Recherche */}
          <div className="flex-1 min-w-[250px] relative">
            <svg className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
            <input
              type="text"
              placeholder="Rechercher par nom ou email..."
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
              className="w-full pl-10 pr-4 py-2 text-sm bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
            />
          </div>

          {/* Filtre Rôle */}
          <select
            value={filtreRole}
            onChange={(e) => setFiltreRole(e.target.value)}
            className="px-4 py-2 text-sm border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none"
          >
            <option value="tous">Tous les rôles</option>
            {Object.values(USER_ROLES).map(role => (
              <option key={role.value} value={role.value}>{role.label}</option>
            ))}
          </select>

          {/* Filtre Statut */}
          <select
            value={filtreStatus}
            onChange={(e) => setFiltreStatus(e.target.value)}
            className="px-4 py-2 text-sm border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none"
          >
            <option value="tous">Tous les statuts</option>
            {Object.values(USER_STATUS).map(status => (
              <option key={status.value} value={status.value}>{status.icon} {status.label}</option>
            ))}
          </select>

          {usersFiltres.length !== users.length && (
            <span className="text-sm text-zinc-500">
              {usersFiltres.length} résultat{usersFiltres.length > 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Liste des utilisateurs */}
      <div className="space-y-4">
        {usersFiltres.length === 0 ? (
          <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-12 text-center">
            <svg className="w-16 h-16 mx-auto text-zinc-300 dark:text-zinc-600 mb-4" fill="none" stroke="currentColor" strokeWidth="1" viewBox="0 0 24 24">
              <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            <p className="text-zinc-500 dark:text-zinc-400">Aucun utilisateur trouvé</p>
            <p className="text-sm text-zinc-400 dark:text-zinc-500 mt-2">Modifiez vos critères de recherche</p>
          </div>
        ) : (
          usersFiltres.map((user, idx) => (
            <UserCard
              key={user.id}
              user={user}
              index={idx}
              onChangeRole={() => openRoleModal(user)}
              onChangeStatus={() => openStatusModal(user)}
              onPermissions={() => openPermissionsModal(user)}
              onHistory={() => openHistoryModal(user)}
              onDelete={() => handleDelete(user)}
            />
          ))
        )}
      </div>

      {/* Modals */}
      <CreateUserModal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onSuccess={() => {
          setCreateModalOpen(false)
          chargerUtilisateurs()
          afficherMessage('success', 'Utilisateur créé avec succès')
        }}
      />

      {selectedUser && (
        <>
          <ChangeRoleModal
            isOpen={roleModalOpen}
            onClose={() => setRoleModalOpen(false)}
            user={selectedUser}
            onSuccess={() => {
              setRoleModalOpen(false)
              chargerUtilisateurs()
              afficherMessage('success', 'Rôle modifié avec succès')
            }}
          />

          <ChangeStatusModal
            isOpen={statusModalOpen}
            onClose={() => setStatusModalOpen(false)}
            user={selectedUser}
            onSuccess={() => {
              setStatusModalOpen(false)
              chargerUtilisateurs()
              afficherMessage('success', 'Statut modifié avec succès')
            }}
          />

          <PermissionsModal
            isOpen={permissionsModalOpen}
            onClose={() => setPermissionsModalOpen(false)}
            user={selectedUser}
            onSuccess={() => {
              afficherMessage('success', 'Permissions modifiées avec succès')
            }}
          />

          <StatusHistoryModal
            isOpen={historyModalOpen}
            onClose={() => setHistoryModalOpen(false)}
            user={selectedUser}
          />
        </>
      )}
    </div>
  )
}

// Composant pour une carte utilisateur
function UserCard({ user, index, onChangeRole, onChangeStatus, onPermissions, onHistory, onDelete }) {
  const statusInfo = USER_STATUS[user.status] || USER_STATUS.ACTIF
  const roleInfo = USER_ROLES[user.role] || USER_ROLES.EMPLOYE

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6 hover:shadow-lg transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4 flex-1">
          {/* Avatar */}
          <div 
            className="w-14 h-14 rounded-full flex items-center justify-center text-white font-bold text-lg"
            style={{ background: roleInfo.color }}
          >
            {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
          </div>

          {/* Infos utilisateur */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h3 className="text-lg font-semibold text-zinc-900 dark:text-white">
                {user.first_name} {user.last_name}
              </h3>
              <span 
                className="px-2.5 py-0.5 rounded-full text-xs font-medium"
                style={{ 
                  background: `${statusInfo.color}20`,
                  color: statusInfo.color 
                }}
              >
                {statusInfo.icon} {statusInfo.label}
              </span>
              <span 
                className="px-2.5 py-0.5 rounded-full text-xs font-medium"
                style={{ 
                  background: `${roleInfo.color}20`,
                  color: roleInfo.color 
                }}
              >
                {roleInfo.label}
              </span>
            </div>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">{user.email}</p>
            <div className="flex items-center gap-4 text-xs text-zinc-500 dark:text-zinc-400">
              <span>📅 Créé le {new Date(user.date_creation).toLocaleDateString('fr-FR')}</span>
              {user.last_login && (
                <span>🕐 Dernière connexion: {new Date(user.last_login).toLocaleDateString('fr-FR')}</span>
              )}
              {user.created_by_name && (
                <span>👤 Par {user.created_by_name}</span>
              )}
            </div>
            {user.status_reason && (
              <div className="mt-2 text-xs text-amber-600 dark:text-amber-400 flex items-start gap-1">
                <span>⚠️</span>
                <span>{user.status_reason}</span>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={onChangeRole}
            className="px-3 py-1.5 text-sm bg-purple-100 dark:bg-purple-950/20 hover:bg-purple-200 dark:hover:bg-purple-950/40 text-purple-700 dark:text-purple-400 rounded-lg transition-colors font-medium"
            title="Changer le rôle"
          >
            🎭 Rôle
          </button>
          <button
            onClick={onChangeStatus}
            className="px-3 py-1.5 text-sm bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg transition-colors"
            title="Changer le statut"
          >
            ⚙️ Statut
          </button>
          <button
            onClick={onPermissions}
            className="px-3 py-1.5 text-sm bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg transition-colors"
            title="Gérer les permissions"
          >
            🔐 Permissions
          </button>
          <button
            onClick={onHistory}
            className="px-3 py-1.5 text-sm bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg transition-colors"
            title="Voir l'historique"
          >
            📜 Historique
          </button>
          <button
            onClick={onDelete}
            className="px-3 py-1.5 text-sm bg-rose-100 dark:bg-rose-950/20 hover:bg-rose-200 dark:hover:bg-rose-950/40 text-rose-700 dark:text-rose-400 rounded-lg transition-colors"
            title="Supprimer"
          >
            🗑️
          </button>
        </div>
      </div>
    </motion.div>
  )
}
