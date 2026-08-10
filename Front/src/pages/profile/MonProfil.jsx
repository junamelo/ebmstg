import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { useAuth } from '../../contexts/AuthContext'
import api from '../../services/api'

export default function MonProfil() {
  const { user, isAdmin, isChefFacturation, isAgentFacturation, isPayeur, isEmploye } = useAuth()
  const [passwordData, setPasswordData] = useState({
    ancienMdp: '',
    nouveauMdp: '',
    confirmationMdp: '',
    twoFactorCode: ''
  })
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)
  const [twoFactorStep, setTwoFactorStep] = useState('idle')
  const [twoFactorPassword, setTwoFactorPassword] = useState('')
  const [twoFactorCode, setTwoFactorCode] = useState('')
  const [twoFactorSetup, setTwoFactorSetup] = useState(null)
  const [loadingTwoFactor, setLoadingTwoFactor] = useState(false)

  useEffect(() => {
    api.get('/auth/two-factor/status/')
      .then(response => setTwoFactorEnabled(Boolean(response.data.enabled)))
      .catch(() => setMessage({ type: 'error', text: 'Impossible de vérifier le statut de sécurité du compte.' }))
  }, [])

  const handlePasswordChange = (e) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value })
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    if (passwordData.nouveauMdp !== passwordData.confirmationMdp) {
      setMessage({ type: 'error', text: 'Les mots de passe ne correspondent pas.' })
      return
    }
    if (passwordData.nouveauMdp.length < 8) {
      setMessage({ type: 'error', text: 'Le mot de passe doit contenir au moins 8 caractères.' })
      return
    }
    try {
      const response = await api.post('/auth/change-password/', {
        old_password: passwordData.ancienMdp,
        new_password: passwordData.nouveauMdp,
        new_password_confirm: passwordData.confirmationMdp,
        two_factor_code: passwordData.twoFactorCode,
      })
      if (response.data.access) localStorage.setItem('token', response.data.access)
      setMessage({ type: 'success', text: 'Mot de passe modifié avec succès !' })
      setPasswordData({ ancienMdp: '', nouveauMdp: '', confirmationMdp: '', twoFactorCode: '' })
      setShowPasswordForm(false)
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || Object.values(error.response?.data || {}).flat().join(' ') || 'Erreur lors du changement de mot de passe.' })
    }
  }

  const demarrerTwoFactor = async (event) => {
    event.preventDefault()
    try {
      setLoadingTwoFactor(true)
      const response = await api.post('/auth/two-factor/setup/', { password: twoFactorPassword })
      setTwoFactorSetup(response.data)
      setTwoFactorCode('')
      setTwoFactorStep('confirm')
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || 'Impossible de démarrer la configuration.' })
    } finally {
      setLoadingTwoFactor(false)
    }
  }

  const confirmerTwoFactor = async (event) => {
    event.preventDefault()
    try {
      setLoadingTwoFactor(true)
      const response = await api.post('/auth/two-factor/confirm/', { code: twoFactorCode })
      setTwoFactorEnabled(true)
      setTwoFactorStep('idle')
      setTwoFactorSetup(null)
      setTwoFactorPassword('')
      setTwoFactorCode('')
      setMessage({ type: 'success', text: response.data.message })
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || 'Code invalide.' })
    } finally {
      setLoadingTwoFactor(false)
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
          {/* Informations personnelles - lecture seule */}
          <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-bold text-zinc-900 dark:text-white flex items-center gap-2">
                <svg className="w-5 h-5" style={{ color: accentColor }} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                Informations personnelles
              </h3>
              <span className="text-xs text-zinc-500 dark:text-zinc-400 bg-zinc-100 dark:bg-zinc-800 px-3 py-1 rounded-full">
                Lecture seule
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Nom */}
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                  Nom
                </label>
                <div className="w-full px-4 py-2.5 bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 rounded-lg text-zinc-900 dark:text-white">
                  {user?.nom || '-'}
                </div>
              </div>

              {/* Prénom */}
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                  Prénom
                </label>
                <div className="w-full px-4 py-2.5 bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 rounded-lg text-zinc-900 dark:text-white">
                  {user?.prenom || '-'}
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                  Email
                </label>
                <div className="w-full px-4 py-2.5 bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 rounded-lg text-zinc-900 dark:text-white">
                  {user?.email || '-'}
                </div>
              </div>

              {/* Téléphone */}
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                  Téléphone
                </label>
                <div className="w-full px-4 py-2.5 bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 rounded-lg text-zinc-900 dark:text-white">
                  {user?.telephone || '-'}
                </div>
              </div>

              {/* Raison sociale (si payeur) */}
              {isPayeur() && (
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Raison sociale
                  </label>
                  <div className="w-full px-4 py-2.5 bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 rounded-lg text-zinc-900 dark:text-white">
                    {user?.raisonSociale || '-'}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-xs text-blue-700 dark:text-blue-400">
                <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
                </svg>
                Pour modifier vos informations personnelles, contactez l'administrateur.
              </p>
            </div>
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
              {!twoFactorEnabled && twoFactorStep === 'idle' && (
                <button onClick={() => setTwoFactorStep('password')} className="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-[#002a7a] text-white hover:bg-[#003d9e]">
                  Activer Google Authenticator
                </button>
              )}
            </div>

            {twoFactorStep === 'password' && (
              <form onSubmit={demarrerTwoFactor} className="mb-5 space-y-4 rounded-xl border border-blue-200 bg-blue-50 p-4">
                <div>
                  <h4 className="font-semibold text-blue-950">Configurer Google Authenticator</h4>
                  <p className="mt-1 text-sm text-blue-800">Saisissez votre mot de passe actuel pour recevoir un QR code personnel.</p>
                </div>
                <label className="block text-sm font-medium text-zinc-700">Mot de passe actuel *
                  <input type="password" required value={twoFactorPassword} onChange={e => setTwoFactorPassword(e.target.value)} className="mt-1 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2.5" />
                </label>
                <div className="flex gap-3">
                  <button type="button" onClick={() => { setTwoFactorStep('idle'); setTwoFactorPassword('') }} className="rounded-lg bg-zinc-200 px-4 py-2 text-sm font-medium">Annuler</button>
                  <button disabled={loadingTwoFactor} className="rounded-lg bg-[#002a7a] px-4 py-2 text-sm font-medium text-white disabled:opacity-60">{loadingTwoFactor ? 'Préparation…' : 'Afficher le QR code'}</button>
                </div>
              </form>
            )}

            {twoFactorStep === 'confirm' && twoFactorSetup && (
              <form onSubmit={confirmerTwoFactor} className="mb-5 space-y-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
                <div>
                  <h4 className="font-semibold text-emerald-950">1. Scannez ce QR code</h4>
                  <p className="mt-1 text-sm text-emerald-800">Dans Google Authenticator, appuyez sur « + », puis « Scanner un code QR ».</p>
                </div>
                <img src={twoFactorSetup.qr_code} alt="QR code Google Authenticator" className="mx-auto h-48 w-48 rounded-lg border border-white bg-white p-2" />
                <p className="break-all rounded bg-white p-2 text-xs text-zinc-600"><span className="font-semibold">Clé manuelle :</span> {twoFactorSetup.manual_key}</p>
                <label className="block text-sm font-medium text-zinc-700">2. Code à 6 chiffres affiché par l’application *
                  <input required inputMode="numeric" pattern="[0-9]{6}" maxLength="6" value={twoFactorCode} onChange={e => setTwoFactorCode(e.target.value.replace(/\D/g, ''))} className="mt-1 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2.5 font-mono tracking-[0.35em]" />
                </label>
                <button disabled={loadingTwoFactor} className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-60">{loadingTwoFactor ? 'Vérification…' : 'Confirmer et activer'}</button>
              </form>
            )}

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
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">Minimum 8 caractères</p>
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
                {twoFactorEnabled && <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Code Google Authenticator <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]{6}"
                    maxLength="6"
                    name="twoFactorCode"
                    value={passwordData.twoFactorCode}
                    onChange={(e) => setPasswordData({ ...passwordData, twoFactorCode: e.target.value.replace(/\D/g, '') })}
                    required
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg font-mono tracking-[0.35em] focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                  />
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">Ouvrez Google Authenticator et saisissez le code actuel à 6 chiffres.</p>
                </div>}
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
                      setPasswordData({ ancienMdp: '', nouveauMdp: '', confirmationMdp: '', twoFactorCode: '' })
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
                  <p className="text-sm font-semibold text-zinc-900 dark:text-white">{twoFactorEnabled ? 'Google Authenticator activé' : 'Google Authenticator non activé'}</p>
                  <p className="text-xs text-zinc-600 dark:text-zinc-400">{twoFactorEnabled ? 'Un code à usage unique sera demandé pour modifier votre mot de passe.' : 'La double authentification est optionnelle. Vous pouvez modifier votre mot de passe normalement.'}</p>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
