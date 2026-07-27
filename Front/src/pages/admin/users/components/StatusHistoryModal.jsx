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
      setChargement(true)
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
          {/* Header */}
          <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-zinc-900 dark:text-white">Historique des statuts</h2>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                {user.first_name} {user.last_name}
              </p>
            </div>
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
          <div className="px-6 py-6 overflow-y-auto max-h-[calc(90vh-180px)]">
            {chargement ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-2 border-zinc-300 border-t-[#002a7a] rounded-full animate-spin mx-auto mb-3" />
                <p className="text-zinc-500 dark:text-zinc-400">Chargement de l'historique...</p>
              </div>
            ) : history.length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-zinc-300 dark:text-zinc-600 mb-4" fill="none" stroke="currentColor" strokeWidth="1" viewBox="0 0 24 24">
                  <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <p className="text-zinc-500 dark:text-zinc-400">Aucun historique de changement de statut</p>
                <p className="text-sm text-zinc-400 dark:text-zinc-500 mt-2">
                  Cet utilisateur n'a jamais changé de statut
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Timeline */}
                <div className="relative">
                  {/* Ligne verticale */}
                  <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-zinc-200 dark:bg-zinc-700"></div>
                  
                  {history.map((item, idx) => {
                    const oldStatus = USER_STATUS[item.old_status] || USER_STATUS.ACTIF
                    const newStatus = USER_STATUS[item.new_status] || USER_STATUS.ACTIF
                    
                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="relative flex gap-4 pb-6"
                      >
                        {/* Point sur la timeline */}
                        <div 
                          className="relative z-10 flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl border-4 border-white dark:border-zinc-900"
                          style={{ background: newStatus.color }}
                        >
                          {newStatus.icon}
                        </div>
                        
                        {/* Contenu */}
                        <div className="flex-1 pt-1">
                          <div className="bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg p-4">
                            {/* Changement de statut */}
                            <div className="flex items-center gap-2 mb-2">
                              <span 
                                className="px-2.5 py-0.5 rounded-full text-xs font-medium"
                                style={{ 
                                  background: `${oldStatus.color}20`, 
                                  color: oldStatus.color 
                                }}
                              >
                                {oldStatus.label}
                              </span>
                              <svg className="w-4 h-4 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                <path d="M14 5l7 7m0 0l-7 7m7-7H3"/>
                              </svg>
                              <span 
                                className="px-2.5 py-0.5 rounded-full text-xs font-medium"
                                style={{ 
                                  background: `${newStatus.color}20`, 
                                  color: newStatus.color 
                                }}
                              >
                                {newStatus.label}
                              </span>
                            </div>
                            
                            {/* Raison */}
                            <p className="text-sm text-zinc-700 dark:text-zinc-300 mb-3 bg-zinc-50 dark:bg-zinc-900 p-2 rounded">
                              "{item.reason}"
                            </p>
                            
                            {/* Métadonnées */}
                            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-zinc-500 dark:text-zinc-400">
                              <span className="flex items-center gap-1">
                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                                </svg>
                                Par {item.changed_by_name || 'Système'}
                              </span>
                              <span className="flex items-center gap-1">
                                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                  <rect x="3" y="4" width="18" height="18" rx="2"/>
                                  <line x1="16" y1="2" x2="16" y2="6"/>
                                  <line x1="8" y1="2" x2="8" y2="6"/>
                                  <line x1="3" y1="10" x2="21" y2="10"/>
                                </svg>
                                {new Date(item.changed_at).toLocaleString('fr-FR', {
                                  day: '2-digit',
                                  month: 'long',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </span>
                              {item.end_date && (
                                <span className="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                                    <path d="M12 8v4l3 3"/>
                                  </svg>
                                  Jusqu'au {new Date(item.end_date).toLocaleDateString('fr-FR')}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
          
          {/* Footer */}
          <div className="px-6 py-4 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
            <div className="text-sm text-zinc-500 dark:text-zinc-400">
              {history.length > 0 && (
                <span>{history.length} changement{history.length > 1 ? 's' : ''}</span>
              )}
            </div>
            <button 
              onClick={onClose} 
              className="px-4 py-2 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg transition-colors font-medium"
            >
              Fermer
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
