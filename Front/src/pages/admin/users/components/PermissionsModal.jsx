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
      setChargement(true)
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
          {/* Header */}
          <div className="px-6 py-4 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-zinc-900 dark:text-white">Gérer les permissions</h2>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-1">
                {user.first_name} {user.last_name} - {user.role}
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
                <p className="text-zinc-500">Chargement des permissions...</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Info */}
                <div className="p-4 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/30 rounded-lg text-sm text-blue-800 dark:text-blue-300">
                  ℹ️ Les permissions cochées en grisé sont héritées du rôle et ne peuvent pas être retirées.
                </div>

                {Object.entries(PERMISSIONS_LIST).map(([category, { label, permissions: perms }]) => (
                  <div key={category}>
                    <h3 className="text-sm font-semibold text-zinc-900 dark:text-white mb-3 flex items-center gap-2">
                      <span className="w-1 h-4 bg-[#002a7a] rounded"></span>
                      {label}
                    </h3>
                    <div className="space-y-2 ml-3">
                      {perms.map(perm => {
                        const isFromRole = permissions.role_permissions.includes(perm.key)
                        const isCustom = permissions.custom_permissions.includes(perm.key)
                        const isActive = isFromRole || isCustom
                        
                        return (
                          <label
                            key={perm.key}
                            className={`flex items-center gap-3 p-3 border rounded-lg transition-colors ${
                              isFromRole 
                                ? 'bg-zinc-50 dark:bg-zinc-800/50 border-zinc-200 dark:border-zinc-700 cursor-not-allowed' 
                                : 'hover:bg-zinc-50 dark:hover:bg-zinc-800 border-zinc-200 dark:border-zinc-700 cursor-pointer'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={isActive}
                              disabled={isFromRole}
                              onChange={() => togglePermission(perm.key)}
                              className="w-4 h-4 text-[#002a7a] rounded disabled:opacity-50"
                            />
                            <div className="flex-1">
                              <p className="text-sm font-medium text-zinc-900 dark:text-white">
                                {perm.label}
                                {perm.restricted && (
                                  <span className="ml-2 px-2 py-0.5 bg-rose-100 dark:bg-rose-950/20 text-rose-700 dark:text-rose-400 text-xs rounded">
                                    Restreint
                                  </span>
                                )}
                              </p>
                              {isFromRole && (
                                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
                                  🔒 Hérité du rôle {permissions.role}
                                </p>
                              )}
                              {isCustom && !isFromRole && (
                                <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-0.5">
                                  ✅ Permission personnalisée
                                </p>
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
          
          {/* Footer */}
          <div className="px-6 py-4 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
            <div className="text-sm text-zinc-500 dark:text-zinc-400">
              {permissions && (
                <span>
                  {permissions.all_permissions.length} permission{permissions.all_permissions.length > 1 ? 's' : ''} active{permissions.all_permissions.length > 1 ? 's' : ''}
                </span>
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
