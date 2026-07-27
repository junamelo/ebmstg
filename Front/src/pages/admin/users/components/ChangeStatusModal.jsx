import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { changeUserStatus, USER_STATUS } from '../../../../services/userService'

export default function ChangeStatusModal({ isOpen, onClose, user, onSuccess }) {
  const [newStatus, setNewStatus] = useState(user?.status || 'ACTIF')
  const [reason, setReason] = useState('')
  const [endDate, setEndDate] = useState('')
  const [sendNotification, setSendNotification] = useState(true)
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErreur(null)
    setChargement(true)

    try {
      await changeUserStatus(user.id, {
        new_status: newStatus,
        reason,
        end_date: endDate || null,
        send_notification: sendNotification
      })
      onSuccess()
    } catch (error) {
      setErreur(error.response?.data?.message || 'Erreur lors du changement de statut')
    } finally {
      setChargement(false)
    }
  }

  if (!isOpen || !user) return null

  const currentStatusInfo = USER_STATUS[user.status] || USER_STATUS.ACTIF
  const newStatusInfo = USER_STATUS[newStatus] || USER_STATUS.ACTIF

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
              Changer le statut
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
              <div className="w-12 h-12 rounded-full bg-[#002a7a] flex items-center justify-center text-white font-bold">
                {user.first_name?.charAt(0)}{user.last_name?.charAt(0)}
              </div>
              <div>
                <p className="font-semibold text-zinc-900 dark:text-white">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-sm text-zinc-500 dark:text-zinc-400">{user.email}</p>
              </div>
            </div>

            {/* Statut actuel */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Statut actuel
              </label>
              <div 
                className="px-4 py-2 rounded-lg font-medium text-sm"
                style={{ 
                  background: `${currentStatusInfo.color}20`,
                  color: currentStatusInfo.color 
                }}
              >
                {currentStatusInfo.icon} {currentStatusInfo.label}
              </div>
            </div>

            {/* Nouveau statut */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Nouveau statut *
              </label>
              <div className="space-y-2">
                {Object.values(USER_STATUS).map(status => (
                  <label
                    key={status.value}
                    className={`flex items-center gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all ${
                      newStatus === status.value
                        ? 'border-[#002a7a] bg-[#002a7a]/5'
                        : 'border-zinc-200 dark:border-zinc-700 hover:border-zinc-300 dark:hover:border-zinc-600'
                    }`}
                  >
                    <input
                      type="radio"
                      name="status"
                      value={status.value}
                      checked={newStatus === status.value}
                      onChange={(e) => setNewStatus(e.target.value)}
                      className="w-4 h-4 text-[#002a7a]"
                    />
                    <span className="text-2xl">{status.icon}</span>
                    <div className="flex-1">
                      <p className="font-medium text-zinc-900 dark:text-white">{status.label}</p>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400">
                        {status.value === 'ACTIF' && 'Accès complet à la plateforme'}
                        {status.value === 'INACTIF' && 'Désactivé temporairement'}
                        {status.value === 'SUSPENDU' && 'Accès bloqué (enquête)'}
                        {status.value === 'EN_ATTENTE' && 'En attente d\'activation'}
                        {status.value === 'BLOQUE' && 'Accès révoqué définitivement'}
                      </p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Raison */}
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                Raison du changement *
              </label>
              <textarea
                required
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows="3"
                className="w-full px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all resize-none"
                placeholder="Expliquez la raison du changement de statut..."
              />
            </div>

            {/* Date de fin (optionnel) */}
            {newStatus !== 'ACTIF' && (
              <div>
                <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                  Date de fin (réactivation automatique)
                </label>
                <input
                  type="datetime-local"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                />
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                  Laissez vide pour une durée indéterminée
                </p>
              </div>
            )}

            {/* Notification */}
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={sendNotification}
                onChange={(e) => setSendNotification(e.target.checked)}
                className="w-4 h-4 text-[#002a7a] rounded"
              />
              <span className="text-sm text-zinc-700 dark:text-zinc-300">
                Envoyer une notification par email
              </span>
            </label>
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
              disabled={chargement}
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
