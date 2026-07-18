import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { getTarifs, creerTarif, desactiverTarif, activerTarif } from '../../services/adminService'

// Design moderne - Gestion des forfaits/services
// DESIGN_VARIANCE: 6 | MOTION_INTENSITY: 4 | VISUAL_DENSITY: 6

export default function GestionForfaits() {
  const [tarifs, setTarifs] = useState([])
  const [chargement, setChargement] = useState(true)
  const [formOuvert, setFormOuvert] = useState(false)
  const [message, setMessage] = useState(null)
  const [form, setForm] = useState({ 
    nom: '', 
    prixParMinute: '', 
    prixParSms: '', 
    prixParGo: '' 
  })

  useEffect(() => { chargerTarifs() }, [])

  const chargerTarifs = () => {
    getTarifs()
      .then(setTarifs)
      .catch(console.error)
      .finally(() => setChargement(false))
  }

  const tarifActif = tarifs.find(t => t.estActif)

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await creerTarif({
        nom: form.nom,
        prixParMinute: parseFloat(form.prixParMinute),
        prixParSms: parseFloat(form.prixParSms),
        prixParGo: parseFloat(form.prixParGo),
      })
      setMessage({ type: 'success', texte: 'Nouveau forfait créé et activé' })
      setForm({ nom: '', prixParMinute: '', prixParSms: '', prixParGo: '' })
      setFormOuvert(false)
      chargerTarifs()
      setTimeout(() => setMessage(null), 5000)
    } catch {
      setMessage({ type: 'error', texte: 'Erreur lors de la création' })
      setTimeout(() => setMessage(null), 5000)
    }
  }

  const handleDesactiver = async (id) => {
    if (!window.confirm('Désactiver ce forfait ?')) return
    try {
      await desactiverTarif(id)
      chargerTarifs()
      setMessage({ type: 'success', texte: 'Forfait désactivé' })
      setTimeout(() => setMessage(null), 3000)
    } catch {
      setMessage({ type: 'error', texte: 'Erreur lors de la désactivation' })
    }
  }

  const handleActiver = async (id) => {
    if (!window.confirm('Activer ce forfait ? Cela désactivera le forfait actif actuel.')) return
    try {
      await activerTarif(id)
      chargerTarifs()
      setMessage({ type: 'success', texte: 'Forfait activé' })
      setTimeout(() => setMessage(null), 3000)
    } catch {
      setMessage({ type: 'error', texte: 'Erreur lors de l\'activation' })
    }
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
            Forfaits et Tarifs
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            Gestion des grilles tarifaires pour la simulation
          </p>
        </div>
        <button
          onClick={() => setFormOuvert(!formOuvert)}
          className="px-4 py-2 bg-[#002a7a] hover:bg-[#003087] text-white rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Nouveau forfait
        </button>
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

      {/* Formulaire */}
      <AnimatePresence>
        {formOuvert && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-6">
                Créer un nouveau forfait
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                    Nom du forfait
                  </label>
                  <input
                    type="text"
                    required
                    value={form.nom}
                    onChange={(e) => setForm({...form, nom: e.target.value})}
                    className="w-full px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                    placeholder="Ex: Forfait Juillet 2026"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                      Prix / minute (FCFA)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={form.prixParMinute}
                      onChange={(e) => setForm({...form, prixParMinute: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                      placeholder="25"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                      Prix / SMS (FCFA)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={form.prixParSms}
                      onChange={(e) => setForm({...form, prixParSms: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                      placeholder="10"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                      Prix / Go (FCFA)
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={form.prixParGo}
                      onChange={(e) => setForm({...form, prixParGo: e.target.value})}
                      className="w-full px-4 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
                      placeholder="2000"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    type="submit"
                    className="px-6 py-2 bg-[#002a7a] hover:bg-[#003087] text-white rounded-lg font-medium transition-colors"
                  >
                    Créer le forfait
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormOuvert(false)}
                    className="px-6 py-2 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg font-medium transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Forfait actif */}
      {tarifActif && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 border border-emerald-200 dark:border-emerald-900/30 rounded-xl p-6"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-700 dark:text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Actif
                </span>
              </div>
              <h3 className="text-xl font-bold text-zinc-900 dark:text-white">{tarifActif.nom}</h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">
                Appliqué depuis le {tarifActif.dateApplication}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="bg-white/50 dark:bg-zinc-900/50 backdrop-blur-sm rounded-lg p-4">
              <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-1">Appel</p>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">
                {tarifActif.prixParMinute} <span className="text-sm font-normal text-zinc-500">FCFA/min</span>
              </p>
            </div>
            <div className="bg-white/50 dark:bg-zinc-900/50 backdrop-blur-sm rounded-lg p-4">
              <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-1">SMS</p>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">
                {tarifActif.prixParSms} <span className="text-sm font-normal text-zinc-500">FCFA/SMS</span>
              </p>
            </div>
            <div className="bg-white/50 dark:bg-zinc-900/50 backdrop-blur-sm rounded-lg p-4">
              <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-1">Data</p>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">
                {tarifActif.prixParGo} <span className="text-sm font-normal text-zinc-500">FCFA/Go</span>
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Historique */}
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden">
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Historique des forfaits</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-zinc-50 dark:bg-zinc-900/50 text-xs uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">Nom</th>
                <th className="px-6 py-3 text-right font-semibold">Appel</th>
                <th className="px-6 py-3 text-right font-semibold">SMS</th>
                <th className="px-6 py-3 text-right font-semibold">Data</th>
                <th className="px-6 py-3 text-center font-semibold">Date</th>
                <th className="px-6 py-3 text-center font-semibold">Statut</th>
                <th className="px-6 py-3 text-center font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {tarifs.map((t, idx) => (
                <motion.tr
                  key={t.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: idx * 0.05 }}
                  className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
                >
                  <td className="px-6 py-4 font-medium text-zinc-900 dark:text-white">{t.nom}</td>
                  <td className="px-6 py-4 text-right font-mono text-sm text-zinc-700 dark:text-zinc-300">{t.prixParMinute} FCFA</td>
                  <td className="px-6 py-4 text-right font-mono text-sm text-zinc-700 dark:text-zinc-300">{t.prixParSms} FCFA</td>
                  <td className="px-6 py-4 text-right font-mono text-sm text-zinc-700 dark:text-zinc-300">{t.prixParGo} FCFA</td>
                  <td className="px-6 py-4 text-center text-sm text-zinc-600 dark:text-zinc-400">{t.dateApplication}</td>
                  <td className="px-6 py-4 text-center">
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                      t.estActif 
                        ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' 
                        : 'bg-zinc-500/10 text-zinc-600 dark:text-zinc-400'
                    }`}>
                      {t.estActif ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {t.estActif ? (
                      <button
                        onClick={() => handleDesactiver(t.id)}
                        className="text-sm text-rose-600 dark:text-rose-400 hover:underline font-medium"
                      >
                        Désactiver
                      </button>
                    ) : (
                      <button
                        onClick={() => handleActiver(t.id)}
                        className="text-sm text-emerald-600 dark:text-emerald-400 hover:underline font-medium"
                      >
                        Activer
                      </button>
                    )}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
