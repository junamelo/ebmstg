import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { updateUser, USER_ROLES } from '../../../../services/userService'

export default function ChangeRoleModal({ isOpen, onClose, user, onSuccess }) {
  const [newRole, setNewRole] = useState(user?.role || 'EMPLOYE')
  const [reason, setReason] = useState('')
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErreur(null)
    setChargement(true)

    try {
      await updateUser(user.id, {
        role: newRole
      })
      onSuccess()
    } catch (error) {
      setErreur(error.response?.data?.message || 'Erreur lors du changement de rôle')
    } finally {
      setChargement(false)
    }
  }

  if (!isOpen || !user) return null

  const currentRoleInfo = USER_ROLES[user.role] || USER_ROLES.EMPLOYE
  const newRoleInfo = USER_ROLES[newRole] || USER_ROLES.EMPLOYE

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        {/* Overlay */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative bg-white dark:bg-zinc-900 rounded-2xl shadow-2xl w-full max-w-md"
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
            <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
              Changer le rôle
            </h2>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Body */}
          <form onSubmit={handleSubmit} className="px-6 py-6 space-y-6">
            {erreur && (
              <div className="p-4 bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/30 rounded-lg text-rose-800 dark:text-rose-300 text-sm">
                {erreur}
              </div>
            )}

            {/* Utilisateur */}
            <div className="flex items-center gap-3 p-4 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
              <div 
                className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold"
                style={{ background: currentRoleInfo.color }}
              >
                {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
              </div>
              <div>
                <p className="font-semibold text-zinc-900 dark:text-white">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-sm text-zinc-500 dark:text-zinc-400">{user.email}</p>
              </div>
            </div>

            {/* Rôle actuel */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Rôle actuel
              </label>
              <div 
                className="px-4 py-2 rounded-lg font-medium text-sm"
                style={{ 
                  background: `${currentRoleInfo.color}20`,
                  color: currentRoleInfo.color 
                }}
              >
                {currentRoleInfo.label}
              </div>
            </div>

            {/* Nouveau rôle */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Nouveau rôle *
              </label>
              <div className="space-y-2">
                {Object.values(USER_ROLES).map(role => (
                  <label
                    key={role.value}
                    className={`flex items-center gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all ${
                      newRole === role.value
                        ? 'border-[#002a7a] bg-[#002a7a]/5'
                        : 'border-zinc-200 dark:border-zinc-700 hover:border-zinc-300 dark:hover:border-zinc-600'
                    }`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value={role.value}
                      checked={newRole === role.value}
                      onChange={(e) => setNewRole(e.target.value)}
                      className="w-4 h-4 text-[#002a7a]"
                    />
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ background: role.color }}
                    />
                    <div className="flex-1">
                      <p className="font-medium text-zinc-900 dark:text-white">{role.label}</p>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400">
                        {role.value === 'SUPER_ADMIN' && 'Accès complet à toute la plateforme'}
                        {role.value === 'CHEF_FACTURATION' && 'Gère les agents de facturation'}
                        {role.value === 'AGENT_FACTURATION' && 'Publication de factures et gestion des forfaits'}
                        {role.value === 'PAYEUR' && 'Responsable d\'une entreprise cliente'}
                        {role.value === 'EMPLOYE' && 'Utilisateur d\'une entreprise cliente'}
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Note importante */}
            <div className="p-4 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/30 rounded-lg">
              <div className="flex gap-3">
                <svg className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                <div className="text-sm text-amber-800 dark:text-amber-300">
                  <p className="font-semibold mb-1">⚠️ Attention</p>
                  <p>Le changement de rôle modifie immédiatement les permissions de l'utilisateur. Cette action peut être réversible en changeant à nouveau le rôle.</p>
                </div>
              </div>
            </div>

            {/* Raison (optionnel) */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Note / Raison (optionnel)
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows="2"
                className="w-full px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all resize-none"
                placeholder="Ex: Promotion, Changement de poste..."
              />
            </div>
          </form>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg transition-colors"
            >
              Annuler
            </button>
            <button
              onClick={handleSubmit}
              disabled={chargement || newRole === user.role}
              className="px-4 py-2 text-sm font-medium bg-[#002a7a] hover:bg-[#003087] text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {chargement ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Modification...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M5 13l4 4L19 7" />
                  </svg>
                  Confirmer le changement
                </>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
