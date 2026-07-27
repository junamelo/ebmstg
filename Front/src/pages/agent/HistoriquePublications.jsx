import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { getHistoriquePublications } from '../../services/adminService'

export default function HistoriquePublications() {
  const [publications, setPublications] = useState([])
  const [chargement, setChargement] = useState(true)
  const [pageActuelle, setPageActuelle] = useState(1)
  const [filtreStatut, setFiltreStatut] = useState('tous')
  const [recherche, setRecherche] = useState('')
  
  const publicationsParPage = 15

  useEffect(() => {
    // Simuler le chargement des données
    setTimeout(() => {
      const mockPublications = Array.from({ length: 75 }, (_, i) => ({
        id: i + 1,
        date: new Date(2026, 6 - (i % 12), 5 + (i % 25)).toLocaleDateString('fr-FR'),
        periode: `${2026 - Math.floor(i / 12)}-${String(12 - (i % 12)).padStart(2, '0')}`,
        nbFactures: Math.floor(Math.random() * 2000) + 1000,
        statut: ['TRAITEE', 'EN_COURS', 'ERREUR'][Math.floor(Math.random() * 3)],
        tailleFichier: (Math.random() * 50 + 10).toFixed(1) + ' MB',
        tempsTraitement: Math.floor(Math.random() * 120 + 30) + ' min',
        nomFichier: `bloc_factures_${2026 - Math.floor(i / 12)}_${String(12 - (i % 12)).padStart(2, '0')}.pdf`
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
        return 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900/30'
      case 'EN_COURS':
        return 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-900/30'
      case 'ERREUR':
        return 'bg-red-500/10 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-900/30'
      default:
        return 'bg-zinc-500/10 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700'
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
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-zinc-50 dark:bg-zinc-900/50 text-xs uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">Date</th>
                <th className="px-6 py-3 text-left font-semibold">Période</th>
                <th className="px-6 py-3 text-left font-semibold">Fichier</th>
                <th className="px-6 py-3 text-right font-semibold">Factures</th>
                <th className="px-6 py-3 text-right font-semibold">Taille</th>
                <th className="px-6 py-3 text-right font-semibold">Traitement</th>
                <th className="px-6 py-3 text-center font-semibold">Statut</th>
                <th className="px-6 py-3 text-center font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {publicationsPaginees.length === 0 ? (
                <tr>
                  <td colSpan="8" className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <svg className="w-12 h-12 text-zinc-300 dark:text-zinc-600" fill="none" stroke="currentColor" strokeWidth="1" viewBox="0 0 24 24">
                        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                      </svg>
                      <p className="text-zinc-500 dark:text-zinc-400">Aucune publication trouvée</p>
                      <p className="text-sm text-zinc-400 dark:text-zinc-500">Modifiez vos critères de recherche</p>
                    </div>
                  </td>
                </tr>
              ) : (
                publicationsPaginees.map((pub, idx) => (
                  <motion.tr
                    key={pub.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.02 }}
                    className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
                  >
                    <td className="px-6 py-4 text-sm text-zinc-600 dark:text-zinc-400">{pub.date}</td>
                    <td className="px-6 py-4 font-medium text-zinc-900 dark:text-white">{pub.periode}</td>
                    <td className="px-6 py-4 text-sm text-zinc-600 dark:text-zinc-400 max-w-xs truncate">
                      {pub.nomFichier}
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-zinc-700 dark:text-zinc-300">
                      {pub.nbFactures.toLocaleString('fr-FR')}
                    </td>
                    <td className="px-6 py-4 text-right text-sm text-zinc-600 dark:text-zinc-400">
                      {pub.tailleFichier}
                    </td>
                    <td className="px-6 py-4 text-right text-sm text-zinc-600 dark:text-zinc-400">
                      {pub.tempsTraitement}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${getStatutBadge(pub.statut)}`}>
                        {getStatutTexte(pub.statut)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        <button className="text-[#002a7a] hover:text-[#003087] text-sm font-medium transition-colors">
                          Détails
                        </button>
                        <button className="text-[#e05500] hover:text-[#cc4d00] text-sm font-medium transition-colors">
                          Télécharger
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
          <div className="px-6 py-4 bg-zinc-50 dark:bg-zinc-900/50 border-t border-zinc-200 dark:border-zinc-800">
            <div className="flex items-center justify-between">
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Affichage {indexDebut + 1} à {Math.min(indexFin, publicationsFiltrees.length)} sur {publicationsFiltrees.length} publications
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => changerPage(pageActuelle - 1)}
                  disabled={pageActuelle === 1}
                  className="px-3 py-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  ← Précédent
                </button>
                
                <div className="flex items-center gap-1">
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
                        className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                          pageNum === pageActuelle
                            ? 'bg-[#002a7a] text-white'
                            : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800'
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
                  className="px-3 py-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Suivant →
                </button>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}