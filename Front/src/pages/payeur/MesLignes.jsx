import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { useAuth } from '../../contexts/AuthContext'
import api from '../../services/api'

export default function MesLignes() {
  const { user } = useAuth()
  const [lignes, setLignes] = useState([])
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState(null)
  const [recherche, setRecherche] = useState('')
  const [filtreStatut, setFiltreStatut] = useState('tous')

  useEffect(() => {
    chargerLignes()
  }, [])

  const chargerLignes = async () => {
    try {
      setChargement(true)
      setErreur(null)
      const response = await api.get('/billing/lines/')
      const data = response.data.results || response.data
      setLignes(data)
    } catch (e) {
      console.error('Erreur chargement lignes:', e)
      setErreur('Impossible de charger les lignes. Vérifiez votre connexion.')
    } finally {
      setChargement(false)
    }
  }

  const lignesFiltrees = lignes.filter(ligne => {
    const matchStatut = filtreStatut === 'tous' || ligne.statut === filtreStatut
    const nomUtilisateur = ligne.utilisateur || ''
    const matchRecherche = recherche === '' ||
      (ligne.msisdn || '').includes(recherche) ||
      nomUtilisateur.toLowerCase().includes(recherche.toLowerCase())
    return matchStatut && matchRecherche
  })

  const getStatutBadge = (statut) => {
    return statut === 'ACTIF'
      ? 'bg-emerald-100 text-emerald-700'
      : statut === 'SUSPENDU'
      ? 'bg-orange-100 text-orange-700'
      : 'bg-red-100 text-red-700'
  }

  const nbActives = lignes.filter(l => l.statut === 'ACTIF').length
  const nbSuspendues = lignes.filter(l => l.statut === 'SUSPENDU').length

  if (chargement) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-zinc-200 border-t-[#e05500] rounded-full animate-spin"/>
          <span className="text-sm text-zinc-500">Chargement des lignes...</span>
        </div>
      </div>
    )
  }

  if (erreur) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <p className="text-red-600">{erreur}</p>
        <button onClick={chargerLignes} className="px-4 py-2 bg-[#e05500] text-white rounded-lg text-sm">
          Réessayer
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white mb-2">
          Mes Lignes
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Consultez les lignes téléphoniques de votre contrat
        </p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Total lignes', value: lignes.length, color: 'text-[#e05500]', bg: 'bg-[#e05500]/10' },
          { label: 'Actives', value: nbActives, color: 'text-emerald-600', bg: 'bg-emerald-500/10' },
          { label: 'Suspendues', value: nbSuspendues, color: 'text-orange-600', bg: 'bg-orange-500/10' },
        ].map((stat, idx) => (
          <motion.div key={stat.label}
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1 }}
            className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 ${stat.bg} rounded-lg flex items-center justify-center`}>
                <svg className={`w-6 h-6 ${stat.color}`} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-zinc-900 dark:text-white">{stat.value}</p>
                <p className="text-sm text-zinc-500">{stat.label}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Filtres */}
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-5">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <svg className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
            </svg>
            <input type="text" placeholder="Rechercher par numéro ou utilisateur..."
              value={recherche} onChange={e => setRecherche(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-zinc-300 dark:border-zinc-700 rounded-lg text-sm focus:ring-2 focus:ring-[#e05500] outline-none bg-white dark:bg-zinc-800"/>
          </div>
          <select value={filtreStatut} onChange={e => setFiltreStatut(e.target.value)}
            className="px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white text-sm focus:ring-2 focus:ring-[#e05500] outline-none">
            <option value="tous">Tous les statuts</option>
            <option value="ACTIF">Actives</option>
            <option value="SUSPENDU">Suspendues</option>
            <option value="INACTIF">Inactives</option>
          </select>
        </div>
      </div>

      {/* Tableau */}
      {lignesFiltrees.length === 0 ? (
        <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-12 text-center">
          <svg className="w-12 h-12 mx-auto text-zinc-300 mb-3" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
            <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
          </svg>
          <p className="text-zinc-400 text-sm">Aucune ligne trouvée</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-zinc-50 dark:bg-zinc-900/50 border-b border-zinc-200 dark:border-zinc-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wide text-zinc-500">Numéro</th>
                  <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wide text-zinc-500">Utilisateur</th>
                  <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wide text-zinc-500">Cycle</th>
                  <th className="px-6 py-3 text-right text-xs font-bold uppercase tracking-wide text-zinc-500">Forfait</th>
                  <th className="px-6 py-3 text-center text-xs font-bold uppercase tracking-wide text-zinc-500">Statut</th>
                  <th className="px-6 py-3 text-left text-xs font-bold uppercase tracking-wide text-zinc-500">Services</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {lignesFiltrees.map((ligne, idx) => {
                  const services = []
                  if (ligne.facture_detaillee) services.push('Fact. détaillée')
                  if (ligne.option_nolimit) services.push(`No Limit: ${ligne.option_nolimit}`)
                  if (ligne.option_blackberry) services.push(`BB: ${ligne.option_blackberry}`)
                  if (ligne.est_incognito) services.push('Incognito')
                  if (ligne.est_roaming) services.push('Roaming')
                  if (ligne.est_internet) services.push('Internet')
                  if (ligne.est_international) services.push('International')

                  return (
                    <motion.tr key={ligne.id}
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: idx * 0.02 }}
                      className="hover:bg-zinc-50 dark:hover:bg-zinc-800/40 transition-colors">
                      <td className="px-6 py-4">
                        <span className="font-mono font-semibold text-zinc-900 dark:text-white text-sm">{ligne.msisdn}</span>
                      </td>
                      <td className="px-6 py-4 text-sm text-zinc-600 dark:text-zinc-400">
                        {ligne.utilisateur || <span className="italic text-zinc-400">—</span>}
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-xs font-medium px-2 py-0.5 rounded bg-zinc-100 text-zinc-600">{ligne.cycle || '—'}</span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="font-semibold text-[#e05500] text-sm">
                          {ligne.forfait ? `${Number(ligne.forfait).toLocaleString('fr-FR')} FCFA` : '—'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getStatutBadge(ligne.statut)}`}>
                          {ligne.statut}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {services.length === 0
                            ? <span className="text-xs text-zinc-400 italic">Aucun</span>
                            : services.map((s, i) => (
                              <span key={i} className="px-1.5 py-0.5 rounded text-xs font-medium bg-[#002a7a]/10 text-[#002a7a]">{s}</span>
                            ))}
                        </div>
                      </td>
                    </motion.tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
