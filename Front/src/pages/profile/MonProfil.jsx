import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { useAuth } from '../../contexts/AuthContext'

export default function MonProfil() {
  const { user, isAdmin, isChefFacturation, isAgentFacturation, isPayeur, isEmploye } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    nom: '',
    prenom: '',
    email: '',
    login: '',
    telephone: '',
    raisonSociale: '',
    numeroContrat: '',
    numeroLigne: ''
  })
  const [passwordData, setPasswordData] = useState({
    ancienMdp: '',
    nouveauMdp: '',
    confirmationMdp: ''
  })
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    if (user) {
      setFormData({
        nom: user.nom || '',
        prenom: user.prenom || '',
        email: user.email || '',
        login: user.login || '',
        telephone: user.telephone || '',
        raisonSociale: user.raisonSociale || '',
        numeroContrat: user.numeroContrat || '',
        numeroLigne: user.numeroLigne || ''
      })
    }
  }, [user])

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handlePasswordChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      // Simuler une sauvegarde
      await new Promise(resolve => setTimeout(resolve, 1000))
      setMessage({ type: 'success', text: 'Profil mis à jour avec succès !' })
      setIsEditing(false)
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      setMessage({ type: 'error', text: 'Erreur lors de la mise à jour du profil.' })
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    if (passwordData.nouveauMdp !== passwordData.confirmationMdp) {
      setMessage({ type: 'error', text: 'Les mots de passe ne correspondent pas.' })
      return
    }
    if (passwordData.nouveauMdp.length < 6) {
      setMessage({ type: 'error', text: 'Le mot de passe doit contenir au moins 6 caractères.' })
      return
    }
    try {
      // Simuler un changement de mot de passe
      await new Promise(resolve => setTimeout(resolve, 1000))
      setMessage({ type: 'success', text: 'Mot de passe modifié avec succès !' })
      setPasswordData({ ancienMdp: '', nouveauMdp: '', confirmationMdp: '' })
      setShowPasswordForm(false)
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      setMessage({ type: 'error', text: 'Erreur lors du changement de mot de passe.' })
    }
  }

  const getRoleBadge = () => {
    if (isAdmin()) return { label: 'Super Admin', color: 'from-[#e05500] to-[#c2410c]', bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-700 dark:text-orange-400' }
    if (isChefFacturation()) return { label: 'Chef de Facturation', color: 'from-[#002a7a] to-[#003d9e]', bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400' }
    if (isAgentFacturation()) return { label: 'Agent de Facturation', color: 'from-[#002a7a] to-[#003d9e]', bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-700 dark:text-blue-400' }
    if (isPayeur()) return { label: 'Payeur', color: 'from-[#e05500] to-[#c2410c]', bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-700 dark:text-orange-400' }
    if (isEmploye()) return { label: 'Employé', color: 'from-[#e05500] to-[#c2410c]', bg: 'bg-orange-100 dark:bg-orange-900/30', text: 'text-orange-700 dark:text-orange-400' }
    return { label: 'Utilisateur', color: 'from-zinc-600 to-zinc-700', bg: 'bg-zinc-100 dark:bg-zinc-900/30', text: 'text-zinc-700 dark:text-zinc-400' }
  }

  const roleBadge = getRoleBadge()
  const accentColor = isPayeur() || isEmploye() || isAdmin() ? '#e05500' : '#002a7a'

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white mb-2">
          Mon Profil
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Gérez vos informations personnelles et vos préférences
        </p>
      </motion.div>

      {/* Message de succès/erreur */}
      {message.text && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-4 rounded-xl border ${
            message.type === 'success'
              ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400'
              : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400'
          }`}
        >
          <div className="flex items-center gap-3">
            {message.type === 'success' ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
              </svg>
            )}
            <span className="font-medium">{message.text}</span>
          </div>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Carte avatar et infos principales */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-1"
        >
          <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6 space-y-6">
            {/* Avatar */}
            <div className="flex flex-col items-center text-center">
              <div className={`w-28 h-28 bg-gradient-to-br ${roleBadge.color} rounded-full flex items-center justify-center text-white text-3xl font-bold shadow-lg mb-4`}>
                {user?.prenom?.[0] || ''}{user?.nom?.[0] || ''}
              </div>
              <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
                {user?.prenom} {user?.nom}
              </h2>
              <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-3">{user?.email}</p>
              <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold ${roleBadge.bg} ${roleBadge.text}`}>
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"/>
                </svg>
                {roleBadge.label}
              </span>
            </div>

            {/* Stats rapides */}
            <div className="pt-6 border-t border-zinc-200 dark:border-zinc-800 space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-600 dark:text-zinc-400">Identifiant</span>
                <span className="font-mono font-semibold text-zinc-900 dark:text-white">{user?.login}</span>
              </div>
              {user?.numeroLigne && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-600 dark:text-zinc-400">Numéro</span>
                  <span className="font-mono font-semibold text-zinc-900 dark:text-white">{user?.numeroLigne}</span>
                </div>
              )}
              {user?.numeroContrat && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-zinc-600 dark:text-zinc-400">Contrat</span>
                  <span className="font-mono font-semibold text-zinc-900 dark:text-white">{user?.numeroContrat}</span>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Formulaire d'édition */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-2 space-y-6"
        >
          {/* Informations personnelles */}
          <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-zinc-900 dark:text-white flex items-center gap-2">
                <svg className="w-5 h-5" style={{ color: accentColor }} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                Informations personnelles
              </h3>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold border rounded-lg transition-all duration-150"
                  style={{ 
                    color: accentColor, 
                    borderColor: accentColor 
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = accentColor
                    e.currentTarget.style.color = 'white'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent'
                    e.currentTarget.style.color = accentColor
                  }}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                  Modifier
                </button>
              )}
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Nom */}
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Nom {(isEmploye() || isAdmin()) && <span className="text-red-500">*</span>}
                  </label>
                  <input
                    type="text"
                    name="nom"
                    value={formData.nom}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all disabled:bg-zinc-100 dark:disabled:bg-zinc-900 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Prénom */}
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Prénom {(isEmploye() || isAdmin()) && <span className="text-red-500">*</span>}
                  </label>
                  <input
                    type="text"
                    name="prenom"
                    value={formData.prenom}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all disabled:bg-zinc-100 dark:disabled:bg-zinc-900 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all disabled:bg-zinc-100 dark:disabled:bg-zinc-900 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Téléphone */}
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    name="telephone"
                    value={formData.telephone}
                    onChange={handleChange}
                    disabled={!isEditing}
                    placeholder="Ex: 90 12 34 56"
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all disabled:bg-zinc-100 dark:disabled:bg-zinc-900 disabled:cursor-not-allowed"
                  />
                </div>

                {/* Raison sociale (si payeur) */}
                {isPayeur() && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                      Raison sociale
                    </label>
                    <input
                      type="text"
                      name="raisonSociale"
                      value={formData.raisonSociale}
                      onChange={handleChange}
                      disabled={!isEditing}
                      className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all disabled:bg-zinc-100 dark:disabled:bg-zinc-900 disabled:cursor-not-allowed"
                    />
                  </div>
                )}
              </div>

              {isEditing && (
                <div className="flex items-center gap-3 pt-4">
                  <button
                    type="submit"
                    className="inline-flex items-center gap-2 px-6 py-2.5 text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-150"
                    style={{ background: `linear-gradient(to bottom right, ${accentColor}, ${accentColor}dd)` }}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path d="M5 13l4 4L19 7"/>
                    </svg>
                    Enregistrer
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsEditing(false)}
                    className="px-6 py-2.5 bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-lg hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-all duration-150"
                  >
                    Annuler
                  </button>
                </div>
              )}
            </form>
          </div>

          {/* Sécurité */}
          <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-zinc-900 dark:text-white flex items-center gap-2">
                <svg className="w-5 h-5" style={{ color: accentColor }} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                Sécurité
              </h3>
              {!showPasswordForm && (
                <button
                  onClick={() => setShowPasswordForm(true)}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold border rounded-lg transition-all duration-150"
                  style={{ 
                    color: accentColor === '#e05500' ? '#e05500' : '#002a7a', 
                    borderColor: accentColor === '#e05500' ? '#e05500' : '#002a7a'
                  }}
                  onMouseEnter={(e) => {
                    const color = accentColor === '#e05500' ? '#e05500' : '#002a7a'
                    e.currentTarget.style.backgroundColor = color
                    e.currentTarget.style.color = 'white'
                  }}
                  onMouseLeave={(e) => {
                    const color = accentColor === '#e05500' ? '#e05500' : '#002a7a'
                    e.currentTarget.style.backgroundColor = 'transparent'
                    e.currentTarget.style.color = color
                  }}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                  </svg>
                  Changer le mot de passe
                </button>
              )}
            </div>

            {showPasswordForm ? (
              <form onSubmit={handlePasswordSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Ancien mot de passe <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    name="ancienMdp"
                    value={passwordData.ancienMdp}
                    onChange={handlePasswordChange}
                    required
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Nouveau mot de passe <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    name="nouveauMdp"
                    value={passwordData.nouveauMdp}
                    onChange={handlePasswordChange}
                    required
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                  />
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">Minimum 6 caractères</p>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Confirmer le mot de passe <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="password"
                    name="confirmationMdp"
                    value={passwordData.confirmationMdp}
                    onChange={handlePasswordChange}
                    required
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                  />
                </div>
                <div className="flex items-center gap-3 pt-2">
                  <button
                    type="submit"
                    className="inline-flex items-center gap-2 px-6 py-2.5 text-white font-semibold rounded-lg hover:shadow-lg transition-all duration-150"
                    style={{ 
                      background: accentColor === '#e05500' 
                        ? 'linear-gradient(to bottom right, #e05500, #c2410c)' 
                        : 'linear-gradient(to bottom right, #002a7a, #003d9e)' 
                    }}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path d="M5 13l4 4L19 7"/>
                    </svg>
                    Modifier le mot de passe
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowPasswordForm(false)
                      setPasswordData({ ancienMdp: '', nouveauMdp: '', confirmationMdp: '' })
                    }}
                    className="px-6 py-2.5 bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-lg hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-all duration-150"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            ) : (
              <div className="flex items-center gap-3 p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                <svg className="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
                <div>
                  <p className="text-sm font-semibold text-zinc-900 dark:text-white">Compte sécurisé</p>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400">Votre mot de passe est protégé</p>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
