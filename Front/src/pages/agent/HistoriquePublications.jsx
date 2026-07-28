import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { getHistoriquePublications } from '../../services/adminService'
import { useAuth } from '../../contexts/AuthContext'

export default function HistoriquePublications() {
  const { isAdmin } = useAuth()
  const [publications, setPublications] = useState([])
  const [chargement, setChargement] = useState(true)
  const [pageActuelle, setPageActuelle] = useState(1)
  const [filtreStatut, setFiltreStatut] = useState('tous')
  const [recherche, setRecherche] = useState('')
  
  const publicationsParPage = 15

  useEffect(() => {
    // Simuler le chargement des données
    setTimeout(() => {
      const agents = ['Koffi ATTIOGBE', 'Divine MENSAH', 'Edem KODJO', 'Adjoa MENSAH']
      const mockPublications = Array.from({ length: 75 }, (_, i) => ({
        id: i + 1,
        date: new Date(2026, 6 - (i % 12), 5 + (i % 25)).toLocaleDateString('fr-FR'),
        periode: `${2026 - Math.floor(i / 12)}-${String(12 - (i % 12)).padStart(2, '0')}`,
        nbFactures: Math.floor(Math.random() * 2000) + 1000,
        statut: ['TRAITEE', 'EN_COURS', 'ERREUR'][Math.floor(Math.random() * 3)],
        tailleFichier: (Math.random() * 50 + 10).toFixed(1) + ' MB',
        tempsTraitement: Math.floor(Math.random() * 120 + 30) + ' min',
        nomFichier: `bloc_factures_${2026 - Math.floor(i / 12)}_${String(12 - (i % 12)).padStart(2, '0')}.pdf`,
        publiePar: agents[Math.floor(Math.random() * agents.length)] // Ajout du nom de l'agent
      }))
      setPublications(mockPublications)
      setChargement(false)
    }, 500)
  }, [])

  // Filtrage des publications
  const publicationsFiltrees = publications.filter(pub => {
    const matchStatut = filtreStatut === 'tous' || pub.statut === filtreStatut
    const matchRecherche = recherche === '' || 
      pub.periode.toLowerCase().includes(recherche.toLowerCase()) ||
      pub.nomFichier.toLowerCase().includes(recherche.toLowerCase())
    return matchStatut && matchRecherche
  })

  // Pagination
  const indexDebut = (pageActuelle - 1) * publicationsParPage
  const indexFin = indexDebut + publicationsParPage
  const publicationsPaginees = publicationsFiltrees.slice(indexDebut, indexFin)
  const nombrePages = Math.ceil(publicationsFiltrees.length / publicationsParPage)

  const changerPage = (nouvellePage) => {
    if (nouvellePage >= 1 && nouvellePage <= nombrePages) {
      setPageActuelle(nouvellePage)
    }
  }

  const getStatutBadge = (statut) => {
    switch(statut) {
      case 'TRAITEE':
        return 'bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 text-emerald-700 dark:text-emerald-400 border-2 border-emerald-400 dark:border-emerald-500/50 shadow-sm'
      case 'EN_COURS':
        return 'bg-gradient-to-br from-amber-500/20 to-amber-600/10 text-amber-700 dark:text-amber-400 border-2 border-amber-400 dark:border-amber-500/50 shadow-sm'
      case 'ERREUR':
        return 'bg-gradient-to-br from-red-500/20 to-red-600/10 text-red-700 dark:text-red-400 border-2 border-red-400 dark:border-red-500/50 shadow-sm'
      default:
        return 'bg-zinc-500/10 text-zinc-600 dark:text-zinc-400 border-2 border-zinc-300 dark:border-zinc-700 shadow-sm'
    }
  }

  const getStatutTexte = (statut) => {
    switch(statut) {
      case 'TRAITEE': return 'Traitée'
      case 'EN_COURS': return 'En cours'
      case 'ERREUR': return 'Erreur'
      default: return 'Inconnu'
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
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white mb-2">
          Historique des Publications
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Historique complet des publications de blocs PDF
        </p>
      </motion.div>

      {/* Statistiques rapides */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#002a7a]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{publications.length}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Total publications</p>
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
                {publications.filter(p => p.statut === 'TRAITEE').length}
              </p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Traitées</p>
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
            <div className="w-12 h-12 bg-amber-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">
                {publications.filter(p => p.statut === 'EN_COURS').length}
              </p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">En cours</p>
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
            <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">
                {publications.filter(p => p.statut === 'ERREUR').length}
              </p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Erreurs</p>
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
                placeholder="Rechercher par période ou nom de fichier..."
                value={recherche}
                onChange={(e) => setRecherche(e.target.value)}
                className="pl-10 pr-4 py-2 w-full bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none transition-all"
              />
            </div>
          </div>
          <select
            value={filtreStatut}
            onChange={(e) => setFiltreStatut(e.target.value)}
            className="px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none"
          >
            <option value="tous">Tous les statuts</option>
            <option value="TRAITEE">Traitées</option>
            <option value="EN_COURS">En cours</option>
            <option value="ERREUR">Erreurs</option>
          </select>
        </div>
        {publicationsFiltrees.length !== publications.length && (
          <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-3">
            {publicationsFiltrees.length} publication{publicationsFiltrees.length > 1 ? 's' : ''} trouvée{publicationsFiltrees.length > 1 ? 's' : ''} sur {publications.length}
          </p>
        )}
      </motion.div>

      {/* Tableau */}
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
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                  Date
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                  Période
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                  Nom du fichier
                </th>
                {isAdmin() && (
                  <th className="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                    Publié par
                  </th>
                )}
                <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                  Factures
                </th>
                <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                  Taille
                </th>
                <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                  Durée
                </th>
                <th className="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                  Statut
                </th>
                <th className="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider text-zinc-700 dark:text-zinc-300">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {publicationsPaginees.length === 0 ? (
                <tr>
                  <td colSpan={isAdmin() ? "9" : "8"} className="px-6 py-16 text-center">
                    <div className="flex flex-col items-center gap-4">
                      <div className="w-16 h-16 bg-zinc-100 dark:bg-zinc-800 rounded-full flex items-center justify-center">
                        <svg className="w-8 h-8 text-zinc-400 dark:text-zinc-500" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
                          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                      </div>
                      <div>
                        <p className="text-base font-medium text-zinc-700 dark:text-zinc-300 mb-1">Aucune publication trouvée</p>
                        <p className="text-sm text-zinc-500 dark:text-zinc-400">Modifiez vos critères de recherche ou essayez d'autres filtres</p>
                      </div>
                    </div>
                  </td>
                </tr>
              ) : (
                publicationsPaginees.map((pub, idx) => (
                  <motion.tr
                    key={pub.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.015, duration: 0.2 }}
                    className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/40 transition-all duration-150"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
                          <line x1="16" x2="16" y1="2" y2="6"/>
                          <line x1="8" x2="8" y1="2" y2="6"/>
                          <line x1="3" x2="21" y1="10" y2="10"/>
                        </svg>
                        <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">{pub.date}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-[#002a7a]/10 text-[#002a7a] dark:bg-[#002a7a]/20 dark:text-blue-400">
                        {pub.periode}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 max-w-sm">
                        <svg className="w-4 h-4 text-zinc-400 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                        </svg>
                        <span className="text-sm text-zinc-700 dark:text-zinc-300 truncate font-mono">
                          {pub.nomFichier}
                        </span>
                      </div>
                    </td>
                    {isAdmin() && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 bg-gradient-to-br from-[#002a7a] to-[#003d9e] rounded-full flex items-center justify-center text-white font-bold text-xs shadow-md">
                            {pub.publiePar.split(' ').map(n => n[0]).join('')}
                          </div>
                          <div className="flex flex-col">
                            <span className="text-sm font-semibold text-zinc-800 dark:text-zinc-200">{pub.publiePar}</span>
                            <span className="text-xs text-zinc-500 dark:text-zinc-400">Agent</span>
                          </div>
                        </div>
                      </td>
                    )}
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <div className="flex flex-col items-end">
                        <span className="text-sm font-bold text-zinc-900 dark:text-white font-mono">
                          {pub.nbFactures.toLocaleString('fr-FR')}
                        </span>
                        <span className="text-xs text-zinc-500 dark:text-zinc-400">factures</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-100 dark:bg-zinc-800 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                        </svg>
                        {pub.tailleFichier}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right whitespace-nowrap">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-50 dark:bg-amber-900/20 text-sm font-medium text-amber-700 dark:text-amber-400">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <circle cx="12" cy="12" r="10"/>
                          <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        {pub.tempsTraitement}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold ${getStatutBadge(pub.statut)}`}>
                        {pub.statut === 'TRAITEE' && (
                          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                          </svg>
                        )}
                        {pub.statut === 'EN_COURS' && (
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10"/>
                          </svg>
                        )}
                        {pub.statut === 'ERREUR' && (
                          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
                          </svg>
                        )}
                        {getStatutTexte(pub.statut)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center whitespace-nowrap">
                      <div className="flex items-center justify-center gap-2">
                        <button className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-[#002a7a] hover:text-white hover:bg-[#002a7a] border border-[#002a7a] rounded-lg transition-all duration-150 hover:shadow-md">
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                            <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                          </svg>
                          Détails
                        </button>
                        <button className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-[#e05500] hover:text-white hover:bg-[#e05500] border border-[#e05500] rounded-lg transition-all duration-150 hover:shadow-md">
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                            <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                          </svg>
                          PDF
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {nombrePages > 1 && (
          <div className="px-6 py-4 bg-gradient-to-r from-zinc-50 to-zinc-100 dark:from-zinc-900/50 dark:to-zinc-900/30 border-t border-zinc-200 dark:border-zinc-800">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                Affichage <span className="font-bold text-zinc-900 dark:text-white">{indexDebut + 1}</span> à{' '}
                <span className="font-bold text-zinc-900 dark:text-white">{Math.min(indexFin, publicationsFiltrees.length)}</span> sur{' '}
                <span className="font-bold text-zinc-900 dark:text-white">{publicationsFiltrees.length}</span> publications
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => changerPage(pageActuelle - 1)}
                  disabled={pageActuelle === 1}
                  className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-zinc-700 dark:text-zinc-300 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-700 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white dark:disabled:hover:bg-zinc-800 transition-all duration-150 shadow-sm hover:shadow"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M15 19l-7-7 7-7"/>
                  </svg>
                  Précédent
                </button>
                
                <div className="flex items-center gap-1.5">
                  {Array.from({ length: Math.min(5, nombrePages) }, (_, i) => {
                    let pageNum
                    if (nombrePages <= 5) {
                      pageNum = i + 1
                    } else if (pageActuelle <= 3) {
                      pageNum = i + 1
                    } else if (pageActuelle >= nombrePages - 2) {
                      pageNum = nombrePages - 4 + i
                    } else {
                      pageNum = pageActuelle - 2 + i
                    }
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => changerPage(pageNum)}
                        className={`min-w-[40px] h-10 px-3 text-sm font-bold rounded-lg transition-all duration-150 ${
                          pageNum === pageActuelle
                            ? 'bg-gradient-to-br from-[#002a7a] to-[#003d9e] text-white shadow-lg shadow-[#002a7a]/30 scale-105'
                            : 'bg-white dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-300 dark:border-zinc-700 hover:bg-zinc-50 dark:hover:bg-zinc-700 hover:border-[#002a7a] dark:hover:border-[#002a7a] hover:text-[#002a7a] dark:hover:text-[#002a7a] shadow-sm'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                </div>

                <button
                  onClick={() => changerPage(pageActuelle + 1)}
                  disabled={pageActuelle === nombrePages}
                  className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-zinc-700 dark:text-zinc-300 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-700 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white dark:disabled:hover:bg-zinc-800 transition-all duration-150 shadow-sm hover:shadow"
                >
                  Suivant
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M9 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}