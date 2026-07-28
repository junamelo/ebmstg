import { useState } from 'react'
import { motion } from 'motion/react'
import { useAuth } from '../../contexts/AuthContext'

export default function MesLignes() {
  const { user } = useAuth()
  
  const [lignes, setLignes] = useState([
    {
      id: '1',
      numero: '79 34 27 35',
      nom: 'TOTSOVI',
      prenom: 'Eyram',
      email: 'e.totsovi@biospartners.com',
      statut: 'ACTIF',
      forfaits: ['No Limit AI50', 'Facture Détaillée'],
      consommation: {
        voix: 450,
        sms: 120,
        data: 15.5
      },
      dateActivation: '20/03/2020'
    },
    {
      id: '2',
      numero: '79 34 27 36',
      nom: 'AGBEKO',
      prenom: 'Koffi',
      email: 'k.agbeko@biospartners.com',
      statut: 'ACTIF',
      forfaits: ['BlackBerry BB15_6'],
      consommation: {
        voix: 320,
        sms: 85,
        data: 8.2
      },
      dateActivation: '15/06/2020'
    },
    {
      id: '3',
      numero: '79 34 27 37',
      nom: 'MENSAH',
      prenom: 'Divine',
      email: 'd.mensah@biospartners.com',
      statut: 'SUSPENDU',
      forfaits: ['No Limit AI70'],
      consommation: {
        voix: 0,
        sms: 0,
        data: 0
      },
      dateActivation: '10/08/2021'
    }
  ])

  const [recherche, setRecherche] = useState('')
  const [filtreStatut, setFiltreStatut] = useState('tous')

  const lignesFiltrees = lignes.filter(ligne => {
    const matchStatut = filtreStatut === 'tous' || ligne.statut === filtreStatut
    const matchRecherche = recherche === '' ||
      ligne.numero.includes(recherche) ||
      ligne.nom.toLowerCase().includes(recherche.toLowerCase()) ||
      ligne.prenom.toLowerCase().includes(recherche.toLowerCase())
    return matchStatut && matchRecherche
  })

  const getStatutBadge = (statut) => {
    return statut === 'ACTIF'
      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white mb-2">
          Mes Lignes
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Gérez et consultez toutes les lignes de votre entreprise
        </p>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#e05500]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#e05500]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{lignes.length}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Total lignes</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">
                {lignes.filter(l => l.statut === 'ACTIF').length}
              </p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Lignes actives</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">
                {lignes.filter(l => l.statut === 'SUSPENDU').length}
              </p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Suspendues</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#002a7a]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">
                {new Set(lignes.map(l => l.nom + l.prenom)).size}
              </p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Employés</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Filtres */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
      >
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <svg className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"/>
                <path d="M21 21l-4.35-4.35"/>
              </svg>
              <input
                type="text"
                placeholder="Rechercher par numéro, nom ou prénom..."
                value={recherche}
                onChange={(e) => setRecherche(e.target.value)}
                className="pl-10 pr-4 py-2 w-full bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#e05500] focus:border-transparent outline-none"
              />
            </div>
          </div>
          <select
            value={filtreStatut}
            onChange={(e) => setFiltreStatut(e.target.value)}
            className="px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#e05500] outline-none"
          >
            <option value="tous">Tous les statuts</option>
            <option value="ACTIF">Actives</option>
            <option value="SUSPENDU">Suspendues</option>
          </select>
        </div>
      </motion.div>

      {/* Tableau des lignes */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden shadow-sm"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-zinc-50 to-zinc-100 dark:from-zinc-900/80 dark:to-zinc-900/50 border-b border-zinc-200 dark:border-zinc-800">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">Numéro</th>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">Employé</th>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">Forfaits</th>
                <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">Consommation</th>
                <th className="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">Statut</th>
                <th className="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {lignesFiltrees.map((ligne, idx) => (
                <motion.tr
                  key={ligne.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.015 }}
                  className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/40 transition-all"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="w-10 h-10 bg-[#e05500]/10 rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5 text-[#e05500]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                        </svg>
                      </div>
                      <div>
                        <p className="font-mono font-bold text-zinc-900 dark:text-white">{ligne.numero}</p>
                        <p className="text-xs text-zinc-500 dark:text-zinc-400">Depuis {ligne.dateActivation}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-semibold text-zinc-900 dark:text-white">{ligne.prenom} {ligne.nom}</p>
                      <p className="text-sm text-zinc-500 dark:text-zinc-400">{ligne.email}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {ligne.forfaits.map((forfait, i) => (
                        <span key={i} className="inline-flex px-2 py-1 rounded-md text-xs font-medium bg-[#002a7a]/10 text-[#002a7a] dark:bg-[#002a7a]/20 dark:text-blue-400">
                          {forfait}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="text-sm space-y-1">
                      <p className="text-zinc-700 dark:text-zinc-300">
                        <span className="font-semibold">{ligne.consommation.voix}</span> min
                      </p>
                      <p className="text-zinc-700 dark:text-zinc-300">
                        <span className="font-semibold">{ligne.consommation.sms}</span> SMS
                      </p>
                      <p className="text-zinc-700 dark:text-zinc-300">
                        <span className="font-semibold">{ligne.consommation.data}</span> Go
                      </p>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold ${getStatutBadge(ligne.statut)}`}>
                      {ligne.statut === 'ACTIF' ? (
                        <>
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                          </svg>
                          Active
                        </>
                      ) : (
                        <>
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
                          </svg>
                          Suspendue
                        </>
                      )}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-[#002a7a] hover:text-white hover:bg-[#002a7a] border border-[#002a7a] rounded-lg transition-all">
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                      Détails
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  )
}
