import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { useAuth } from '../../contexts/AuthContext'

// Mock API - À remplacer par les vrais appels
const mockGetAgents = async () => {
  return [
    {
      id: 1,
      username: 'agent.dupont',
      email: 'agent.dupont@moov.africa',
      first_name: 'Jean',
      last_name: 'Dupont',
      role: 'AGENT_FACTURATION',
      status: 'ACTIF',
      custom_permissions: ['accounts.create_agent'],
      date_creation: '2026-01-15',
      last_login: '2026-07-26 14:30',
    },
    {
      id: 2,
      username: 'agent.martin',
      email: 'agent.martin@moov.africa',
      first_name: 'Marie',
      last_name: 'Martin',
      role: 'AGENT_FACTURATION',
      status: 'ACTIF',
      custom_permissions: [],
      date_creation: '2026-02-20',
      last_login: '2026-07-27 09:15',
    },
  ]
}

const mockCreerAgent = async (data) => {
  return {
    id: Date.now(),
    ...data,
    status: 'ACTIF',
    date_creation: new Date().toISOString().split('T')[0],
    last_login: null,
  }
}

const mockModifierAgent = async (id, data) => {
  return { id, ...data }
}

const mockToggleStatus = async (id) => {
  return { success: true }
}

export default function GestionAgents() {
  const { user, isChefFacturation, canCreateAgents } = useAuth()
  const [agents, setAgents] = useState([])
  const [chargement, setChargement] = useState(true)
  const [message, setMessage] = useState(null)
  const [formOuvert, setFormOuvert] = useState(false)
  const [modeEdition, setModeEdition] = useState(false)
  const [agentEnEdition, setAgentEnEdition] = useState(null)
  const [recherche, setRecherche] = useState('')

  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    confirmPassword: '',
    custom_permissions: []
  })

  useEffect(() => {
    chargerAgents()
  }, [])

  const chargerAgents = () => {
    mockGetAgents()
      .then(setAgents)
      .catch(console.error)
      .finally(() => setChargement(false))
  }

  const showMsg = (type, texte) => {
    setMessage({ type, texte })
    setTimeout(() => setMessage(null), 4000)
  }

  const resetForm = () => {
    setForm({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      confirmPassword: '',
      custom_permissions: []
    })
    setModeEdition(false)
    setAgentEnEdition(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    // Validation
    if (!modeEdition && form.password !== form.confirmPassword) {
      showMsg('error', 'Les mots de passe ne correspondent pas')
      return
    }

    if (!modeEdition && form.password.length < 6) {
      showMsg('error', 'Le mot de passe doit contenir au moins 6 caractères')
      return
    }

    try {
      if (modeEdition && agentEnEdition) {
        // Modification
        const agentModifie = await mockModifierAgent(agentEnEdition.id, {
          ...agentEnEdition,
          username: form.username,
          email: form.email,
          first_name: form.first_name,
          last_name: form.last_name,
          custom_permissions: form.custom_permissions
        })
        setAgents(agents.map(a => a.id === agentEnEdition.id ? agentModifie : a))
        showMsg('success', `Agent « ${form.username} » modifié avec succès`)
      } else {
        // Création
        const nouvelAgent = await mockCreerAgent({
          username: form.username,
          email: form.email,
          first_name: form.first_name,
          last_name: form.last_name,
          password: form.password,
          role: 'AGENT_FACTURATION',
          custom_permissions: form.custom_permissions
        })
        setAgents([nouvelAgent, ...agents])
        showMsg('success', `Agent « ${form.username} » créé avec succès`)
      }

      resetForm()
      setFormOuvert(false)
    } catch (error) {
      showMsg('error', 'Erreur lors de l\'opération')
      console.error(error)
    }
  }

  const handleModifier = (agent) => {
    setModeEdition(true)
    setAgentEnEdition(agent)
    setForm({
      username: agent.username,
      email: agent.email,
      first_name: agent.first_name,
      last_name: agent.last_name,
      password: '',
      confirmPassword: '',
      custom_permissions: agent.custom_permissions || []
    })
    setFormOuvert(true)
  }

  const handleToggleStatus = async (agent) => {
    const nouveauStatut = agent.status === 'ACTIF' ? 'INACTIF' : 'ACTIF'
    if (!window.confirm(`${nouveauStatut === 'INACTIF' ? 'Désactiver' : 'Activer'} cet agent ?`)) return

    try {
      await mockToggleStatus(agent.id)
      setAgents(agents.map(a =>
        a.id === agent.id ? { ...a, status: nouveauStatut } : a
      ))
      showMsg('success', `Agent ${nouveauStatut === 'INACTIF' ? 'désactivé' : 'activé'}`)
    } catch {
      showMsg('error', 'Erreur lors du changement de statut')
    }
  }

  const togglePermission = (permission) => {
    setForm(prev => ({
      ...prev,
      custom_permissions: prev.custom_permissions.includes(permission)
        ? prev.custom_permissions.filter(p => p !== permission)
        : [...prev.custom_permissions, permission]
    }))
  }

  const agentsFiltres = agents.filter(agent => {
    if (!recherche) return true
    const terme = recherche.toLowerCase()
    return (
      agent.username.toLowerCase().includes(terme) ||
      agent.email.toLowerCase().includes(terme) ||
      `${agent.first_name} ${agent.last_name}`.toLowerCase().includes(terme)
    )
  })

  const stats = {
    total: agents.length,
    actifs: agents.filter(a => a.status === 'ACTIF').length,
    avecPermissions: agents.filter(a => a.custom_permissions?.includes('accounts.create_agent')).length
  }

  if (chargement) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-zinc-300 border-t-[#002a7a] rounded-full animate-spin" />
          <span className="text-sm text-zinc-600">Chargement...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 mb-2">
            Gestion des Agents
          </h1>
          <p className="text-zinc-600">
            {isChefFacturation() 
              ? 'Gérez vos agents de facturation et leurs permissions'
              : 'Liste des agents de facturation'
            }
          </p>
        </div>
        {(isChefFacturation() || canCreateAgents()) && (
          <button
            onClick={() => { setFormOuvert(!formOuvert); if (!formOuvert) resetForm() }}
            className="px-4 py-2 bg-[#002a7a] hover:bg-[#003087] text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M12 5v14M5 12h14" />
            </svg>
            Nouvel agent
          </button>
        )}
      </div>

      {/* Stats KPI */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl border border-zinc-200 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#002a7a]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900">{stats.total}</p>
              <p className="text-sm text-zinc-500">Total agents</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl border border-zinc-200 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900">{stats.actifs}</p>
              <p className="text-sm text-zinc-500">Agents actifs</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl border border-zinc-200 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900">{stats.avecPermissions}</p>
              <p className="text-sm text-zinc-500">Avec permissions</p>
            </div>
          </div>
        </motion.div>
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
                ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
                : 'bg-rose-50 border border-rose-200 text-rose-800'
            }`}
          >
            {message.texte}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Formulaire création/édition */}
      <AnimatePresence>
        {formOuvert && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-white rounded-xl border border-zinc-200 p-6">
              <h2 className="text-lg font-semibold text-zinc-900 mb-6">
                {modeEdition ? 'Modifier l\'agent' : 'Créer un nouvel agent'}
              </h2>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-2">Nom d'utilisateur *</label>
                    <input
                      required
                      type="text"
                      value={form.username}
                      onChange={(e) => setForm({ ...form, username: e.target.value })}
                      className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                      placeholder="agent.dupont"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-2">Email *</label>
                    <input
                      required
                      type="email"
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                      placeholder="agent.dupont@moov.africa"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-2">Prénom *</label>
                    <input
                      required
                      type="text"
                      value={form.first_name}
                      onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                      className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                      placeholder="Jean"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-2">Nom *</label>
                    <input
                      required
                      type="text"
                      value={form.last_name}
                      onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                      className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                      placeholder="Dupont"
                    />
                  </div>

                  {!modeEdition && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-zinc-700 mb-2">Mot de passe *</label>
                        <input
                          required={!modeEdition}
                          type="password"
                          value={form.password}
                          onChange={(e) => setForm({ ...form, password: e.target.value })}
                          className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                          placeholder="••••••••"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-zinc-700 mb-2">Confirmer mot de passe *</label>
                        <input
                          required={!modeEdition}
                          type="password"
                          value={form.confirmPassword}
                          onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                          className="w-full px-4 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                          placeholder="••••••••"
                        />
                      </div>
                    </>
                  )}
                </div>

                {/* Permissions */}
                <div>
                  <label className="block text-sm font-medium text-zinc-700 mb-3">Permissions spéciales</label>
                  <div className="bg-zinc-50 rounded-lg p-4 space-y-2">
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={form.custom_permissions.includes('accounts.create_agent')}
                        onChange={() => togglePermission('accounts.create_agent')}
                        className="w-4 h-4 rounded border-zinc-300 text-[#002a7a] focus:ring-[#002a7a]"
                      />
                      <div>
                        <span className="text-sm font-medium text-zinc-900">Créer d'autres agents</span>
                        <p className="text-xs text-zinc-500">Permet à cet agent de créer d'autres agents de facturation</p>
                      </div>
                    </label>
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    type="submit"
                    className="px-6 py-2 bg-[#002a7a] hover:bg-[#003087] text-white rounded-lg font-medium transition-colors"
                  >
                    {modeEdition ? 'Enregistrer les modifications' : 'Créer l\'agent'}
                  </button>
                  <button
                    type="button"
                    onClick={() => { resetForm(); setFormOuvert(false) }}
                    className="px-6 py-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-700 rounded-lg font-medium transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Liste des agents */}
      <div className="bg-white rounded-xl border border-zinc-200 overflow-hidden">
        <div className="p-6 border-b border-zinc-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-zinc-900">Liste des agents</h2>
            <div className="relative">
              <svg className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8" />
                <path d="M21 21l-4.35-4.35" />
              </svg>
              <input
                type="text"
                placeholder="Rechercher..."
                value={recherche}
                onChange={(e) => setRecherche(e.target.value)}
                className="pl-10 pr-4 py-2 text-sm border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
              />
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-zinc-50 text-xs uppercase tracking-wider text-zinc-600">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">Agent</th>
                <th className="px-6 py-3 text-left font-semibold">Email</th>
                <th className="px-6 py-3 text-center font-semibold">Permissions</th>
                <th className="px-6 py-3 text-center font-semibold">Statut</th>
                <th className="px-6 py-3 text-center font-semibold">Dernière connexion</th>
                <th className="px-6 py-3 text-center font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100">
              {agentsFiltres.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center">
                    <p className="text-zinc-500">Aucun agent trouvé</p>
                  </td>
                </tr>
              ) : (
                agentsFiltres.map((agent, idx) => (
                  <motion.tr
                    key={agent.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.05 }}
                    className="hover:bg-zinc-50"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-[#002a7a]/10 text-[#002a7a] rounded-full flex items-center justify-center font-bold text-sm">
                          {agent.first_name[0]}{agent.last_name[0]}
                        </div>
                        <div>
                          <p className="font-medium text-zinc-900">{agent.first_name} {agent.last_name}</p>
                          <p className="text-sm text-zinc-500">@{agent.username}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-zinc-600">{agent.email}</td>
                    <td className="px-6 py-4 text-center">
                      {agent.custom_permissions?.includes('accounts.create_agent') ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-700">
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M10 2a5 5 0 00-5 5v2a2 2 0 00-2 2v5a2 2 0 002 2h10a2 2 0 002-2v-5a2 2 0 00-2-2H7V7a3 3 0 015.905-.75 1 1 0 001.937-.5A5.002 5.002 0 0010 2z" />
                          </svg>
                          Étendues
                        </span>
                      ) : (
                        <span className="text-xs text-zinc-400">Standard</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${agent.status === 'ACTIF'
                          ? 'bg-emerald-500/10 text-emerald-700'
                          : 'bg-zinc-500/10 text-zinc-600'
                        }`}>
                        {agent.status === 'ACTIF' ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-zinc-600">
                      {agent.last_login || 'Jamais'}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        {(isChefFacturation() || canCreateAgents()) && (
                          <>
                            <button
                              onClick={() => handleModifier(agent)}
                              className="text-sm text-[#002a7a] hover:bg-[#002a7a]/10 px-3 py-1 rounded-lg font-medium"
                            >
                              Modifier
                            </button>
                            <button
                              onClick={() => handleToggleStatus(agent)}
                              className={`text-sm px-3 py-1 rounded-lg font-medium ${agent.status === 'ACTIF'
                                  ? 'text-rose-600 hover:bg-rose-50'
                                  : 'text-emerald-600 hover:bg-emerald-50'
                                }`}
                            >
                              {agent.status === 'ACTIF' ? 'Désactiver' : 'Activer'}
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
