import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { getTarifs, creerTarif, desactiverTarif, activerTarif } from '../../services/adminService'

// Gestion des forfaits avec système de paliers
export default function GestionForfaits() {
  const [tarifs, setTarifs] = useState([])
  const [chargement, setChargement] = useState(true)
  const [formOuvert, setFormOuvert] = useState(false)
  const [modeEdition, setModeEdition] = useState(false)
  const [tarifEnEdition, setTarifEnEdition] = useState(null)
  const [message, setMessage] = useState(null)
  const [rechercheNom, setRechercheNom] = useState('')
  
  const [form, setForm] = useState({ 
    nom: '',
    type: 'VOIX', // VOIX, SMS, DATA
    prixUnitaire: 0,
    unite: 'minute' // minute, sms, Go
  })

  useEffect(() => { chargerTarifs() }, [])

  const chargerTarifs = () => {
    getTarifs()
      .then(setTarifs)
      .catch(console.error)
      .finally(() => setChargement(false))
  }

  const tarifActif = tarifs.find(t => t.estActif)

  // Filtrage des tarifs
  const tarifsFiltres = tarifs.filter(tarif => {
    return rechercheNom === '' || tarif.nom.toLowerCase().includes(rechercheNom.toLowerCase())
  })

  // Statistiques
  const stats = {
    totalForfaits: tarifs.length,
    derniereModification: tarifs.length > 0 ? tarifs[0].dateApplication : 'N/A'
  }

  const resetForm = () => {
    setForm({ 
      nom: '',
      type: 'VOIX',
      prixUnitaire: 0,
      unite: 'minute'
    })
  }

  const handleModifier = (tarif) => {
    setModeEdition(true)
    setTarifEnEdition(tarif)
    setForm({ 
      nom: tarif.nom,
      type: tarif.type || 'VOIX',
      prixUnitaire: tarif.prixUnitaire || 0,
      unite: tarif.unite || 'minute'
    })
    setFormOuvert(true)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const serviceData = {
        nom: form.nom,
        type: form.type,
        prixUnitaire: parseFloat(form.prixUnitaire),
        unite: form.unite,
      }

      if (modeEdition && tarifEnEdition) {
        // Mode modification
        const tarifModifie = {
          ...tarifEnEdition,
          ...serviceData
        }
        setTarifs(tarifs.map(t => t.id === tarifEnEdition.id ? tarifModifie : t))
        setMessage({ type: 'success', texte: `Service « ${form.nom} » modifié avec succès` })
        setModeEdition(false)
        setTarifEnEdition(null)
      } else {
        // Mode création
        await creerTarif(serviceData)
        setMessage({ type: 'success', texte: 'Nouveau service créé et activé' })
        chargerTarifs()
      }
      
      resetForm()
      setFormOuvert(false)
      setTimeout(() => setMessage(null), 5000)
    } catch {
      setMessage({ type: 'error', texte: 'Erreur lors de l\'opération' })
      setTimeout(() => setMessage(null), 5000)
    }
  }

  const handleDesactiver = async (id) => {
    if (!window.confirm('Désactiver ce service ?')) return
    try {
      await desactiverTarif(id)
      chargerTarifs()
      setMessage({ type: 'success', texte: 'Service désactivé' })
      setTimeout(() => setMessage(null), 3000)
    } catch {
      setMessage({ type: 'error', texte: 'Erreur lors de la désactivation' })
    }
  }

  const handleActiver = async (id) => {
    if (!window.confirm('Activer ce service ? Cela désactivera le service actif actuel.')) return
    try {
      await activerTarif(id)
      chargerTarifs()
      setMessage({ type: 'success', texte: 'Service activé' })
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
            Gestion des Services
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            Configuration des services de base (SMS, Data, Voix) avec système de paliers
          </p>
        </div>
        <button
          onClick={() => { setFormOuvert(!formOuvert); if (!formOuvert) resetForm() }}
          className="px-4 py-2 bg-[#002a7a] hover:bg-[#003087] text-white rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M12 5v14M5 12h14" />
          </svg>
          Nouveau service
        </button>
      </div>

      {/* Dashboard KPI */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#002a7a]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{stats.totalForfaits}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Total services</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <p className="text-lg font-bold text-zinc-900 dark:text-white">{stats.derniereModification}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Dernière MAJ</p>
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
                ? 'bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/30 text-emerald-800 dark:text-emerald-300' 
                : 'bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-900/30 text-rose-800 dark:text-rose-300'
            }`}
          >
            {message.texte}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Formulaire simplifié pour créer un service */}
      <AnimatePresence>
        {formOuvert && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">
                {modeEdition ? 'Modifier le service' : 'Créer un nouveau service'}
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Nom du service */}
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                      Nom du service *
                    </label>
                    <input
                      type="text"
                      required
                      value={form.nom}
                      onChange={(e) => setForm({...form, nom: e.target.value})}
                      className="w-full px-3 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg text-sm focus:ring-2 focus:ring-[#002a7a] outline-none"
                      placeholder="Ex: Service Voix Premium"
                    />
                  </div>

                  {/* Type de service */}
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                      Type de service *
                    </label>
                    <select
                      required
                      value={form.type}
                      onChange={(e) => {
                        const type = e.target.value
                        let unite = 'minute'
                        if (type === 'SMS') unite = 'sms'
                        if (type === 'DATA') unite = 'Go'
                        setForm({...form, type, unite})
                      }}
                      className="w-full px-3 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg text-sm focus:ring-2 focus:ring-[#002a7a] outline-none"
                    >
                      <option value="VOIX">📞 Voix</option>
                      <option value="SMS">💬 SMS</option>
                      <option value="DATA">📶 Data</option>
                    </select>
                  </div>

                  {/* Prix unitaire */}
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                      Prix unitaire (FCFA) *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      required
                      value={form.prixUnitaire}
                      onChange={(e) => setForm({...form, prixUnitaire: e.target.value})}
                      className="w-full px-3 py-2 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg text-sm focus:ring-2 focus:ring-[#002a7a] outline-none"
                      placeholder="Ex: 25"
                    />
                  </div>

                  {/* Unité (lecture seule, auto-complétée selon le type) */}
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                      Unité
                    </label>
                    <input
                      type="text"
                      readOnly
                      value={form.unite === 'minute' ? 'Minute' : form.unite === 'sms' ? 'SMS' : 'Go'}
                      className="w-full px-3 py-2 bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-300 dark:border-zinc-700 rounded-lg text-sm text-zinc-600 dark:text-zinc-400"
                    />
                  </div>
                </div>

                {/* Boutons d'action */}
                <div className="flex items-center gap-3 pt-2">
                  <button
                    type="submit"
                    className="px-5 py-2 bg-[#002a7a] hover:bg-[#003087] text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    {modeEdition ? 'Enregistrer' : 'Créer'}
                  </button>
                  <button
                    type="button"
                    onClick={() => { 
                      resetForm()
                      setFormOuvert(false)
                      setModeEdition(false)
                      setTarifEnEdition(null)
                    }}
                    className="px-5 py-2 bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 rounded-lg text-sm font-medium transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Liste des forfaits */}
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden">
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Liste des services</h2>
            <div className="relative">
              <svg className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"/>
                <path d="M21 21l-4.35-4.35"/>
              </svg>
              <input
                type="text"
                placeholder="Rechercher..."
                value={rechercheNom}
                onChange={(e) => setRechercheNom(e.target.value)}
                className="pl-10 pr-4 py-2 text-sm bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
              />
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-zinc-50 dark:bg-zinc-900/50 text-xs uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">Nom</th>
                <th className="px-6 py-3 text-center font-semibold">Type</th>
                <th className="px-6 py-3 text-center font-semibold">Prix Unitaire</th>
                <th className="px-6 py-3 text-center font-semibold">Unité</th>
                <th className="px-6 py-3 text-center font-semibold">Date</th>
                <th className="px-6 py-3 text-center font-semibold">Statut</th>
                <th className="px-6 py-3 text-center font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {tarifsFiltres.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-12 text-center">
                    <p className="text-zinc-500 dark:text-zinc-400">Aucun service trouvé</p>
                  </td>
                </tr>
              ) : (
                tarifsFiltres.map((t, idx) => (
                  <motion.tr
                    key={t.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.05 }}
                    className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50"
                  >
                    <td className="px-6 py-4 font-medium text-zinc-900 dark:text-white">{t.nom}</td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                        t.type === 'VOIX' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' :
                        t.type === 'SMS' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400' :
                        'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400'
                      }`}>
                        {t.type === 'VOIX' ? '📞' : t.type === 'SMS' ? '💬' : '📶'} {t.type || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="px-2 py-1 bg-[#002a7a]/10 dark:bg-[#002a7a]/20 text-[#002a7a] dark:text-blue-400 rounded text-sm font-bold">
                        {t.prixUnitaire || t.prixParSms || 0} FCFA
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-zinc-600 dark:text-zinc-400">
                      {t.unite || (t.type === 'SMS' ? 'sms' : t.type === 'DATA' ? 'Go' : 'minute')}
                    </td>
                    <td className="px-6 py-4 text-center text-sm text-zinc-600 dark:text-zinc-400">
                      {t.dateApplication}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${
                        t.estActif 
                          ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' 
                          : 'bg-zinc-500/10 text-zinc-600 dark:text-zinc-400'
                      }`}>
                        {t.estActif ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button
                          onClick={() => handleModifier(t)}
                          className="text-sm text-[#002a7a] hover:bg-[#002a7a]/10 dark:hover:bg-[#002a7a]/20 px-3 py-1 rounded-lg font-medium transition-colors"
                        >
                          Modifier
                        </button>
                        {t.estActif ? (
                          <button
                            onClick={() => handleDesactiver(t.id)}
                            className="text-sm text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-900/20 px-3 py-1 rounded-lg font-medium transition-colors"
                          >
                            Désactiver
                          </button>
                        ) : (
                          <button
                            onClick={() => handleActiver(t.id)}
                            className="text-sm text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 px-3 py-1 rounded-lg font-medium transition-colors"
                          >
                            Activer
                          </button>
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
