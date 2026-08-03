import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { useNavigate } from 'react-router-dom'
import ModalNouveauContrat from './components/ModalNouveauContrat'
import ContratCard from './components/ContratCard'
import api from '../../services/api'

export default function GestionContrats() {
  const navigate = useNavigate()
  const [contrats, setContrats] = useState([])
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState(null)
  const [message, setMessage] = useState(null)
  const [modalOuvert, setModalOuvert] = useState(false)
  const [recherche, setRecherche] = useState('')
  const [filtreStatut, setFiltreStatut] = useState('tous')
  const [filtreType, setFiltreType] = useState('tous')

  useEffect(() => {
    chargerContrats()
  }, [])

  const chargerContrats = async () => {
    try {
      setChargement(true)
      setErreur(null)
      
      const response = await api.get('/billing/companies/')
      const companies = response.data.results || response.data
      
      // Charger les lignes pour chaque entreprise
      const contratsAvecLignes = await Promise.all(
        companies.map(async (company) => {
          try {
            const lignesResp = await api.get('/billing/lines/', { 
              params: { company: company.id } 
            })
            const lignes = lignesResp.data.results || lignesResp.data
            
            return {
              id: company.id,
              numeroContrat: company.compte,
              typePayeur: 'ENTREPRISE',
              raisonSociale: company.raison_sociale || company.nom_commercial,
              email: company.payeur_info?.email || '',
              telephone: '',
              dateCreation: company.date_creation,
              statut: company.statut || 'ACTIF',
              typeContrat: company.categorie || '',
              lignes: lignes.map(l => ({
                id: l.id,
                numero: l.msisdn,
                employe: l.employe_info ? {
                  nom: l.employe_info.nom?.split(' ')[1] || '',
                  prenom: l.employe_info.nom?.split(' ')[0] || ''
                } : null,
                statut: l.statut || 'ACTIF'
              })),
              caMensuel: lignes.reduce((sum, l) => sum + (parseFloat(l.forfait) || 0), 0)
            }
          } catch (error) {
            console.error(`Erreur chargement lignes pour ${company.id}:`, error)
            return {
              id: company.id,
              numeroContrat: company.compte,
              typePayeur: 'ENTREPRISE',
              raisonSociale: company.raison_sociale || company.nom_commercial,
              email: company.payeur_info?.email || '',
              telephone: '',
              dateCreation: company.date_creation,
              statut: company.statut || 'ACTIF',
              typeContrat: company.categorie || '',
              lignes: [],
              caMensuel: 0
            }
          }
        })
      )
      
      setContrats(contratsAvecLignes)
    } catch (error) {
      console.error('Erreur chargement contrats:', error)
      setErreur('Impossible de charger les contrats')
    } finally {
      setChargement(false)
    }
  }

  const contratsFiltres = contrats.filter(contrat => {
    const matchStatut = filtreStatut === 'tous' || contrat.statut === filtreStatut
    const matchType = filtreType === 'tous' || contrat.typePayeur === filtreType
    const matchRecherche = recherche === '' ||
      contrat.numeroContrat.toLowerCase().includes(recherche.toLowerCase()) ||
      (contrat.raisonSociale && contrat.raisonSociale.toLowerCase().includes(recherche.toLowerCase())) ||
      (contrat.nom && `${contrat.prenom} ${contrat.nom}`.toLowerCase().includes(recherche.toLowerCase()))
    return matchStatut && matchType && matchRecherche
  })

  const handleCreerContrat = async (nouveauContrat) => {
    try {
      const response = await api.post('/billing/companies/', {
        compte: nouveauContrat.numeroContrat,
        raison_sociale: nouveauContrat.raisonSociale || nouveauContrat.nom,
        nom_commercial: nouveauContrat.raisonSociale || nouveauContrat.nom,
        categorie: nouveauContrat.typePayeur === 'ENTREPRISE' ? 'ENTREPRISE' : 'PARTICULIER',
        adresse: nouveauContrat.adresse || '',
        payeur: nouveauContrat.payeur_id || null
      })
      
      setMessage({ type: 'success', text: 'Contrat créé avec succès' })
      setModalOuvert(false)
      chargerContrats()
    } catch (error) {
      const errorMsg = error.response?.data?.compte?.[0] || 
                       error.response?.data?.error || 
                       'Erreur lors de la création'
      setMessage({ type: 'error', text: errorMsg })
    }
  }

  const handleVoirDetails = (contratId) => {
    navigate(`/agent/contrats/${contratId}`)
  }

  const totalLignes = contrats.reduce((sum, c) => sum + c.lignes.length, 0)
  const caTotal = contrats.reduce((sum, c) => sum + c.caMensuel, 0)
  const nouveauxCeMois = contrats.filter(c => {
    const dateCreation = new Date(c.dateCreation)
    const maintenant = new Date()
    return dateCreation.getMonth() === maintenant.getMonth() && 
           dateCreation.getFullYear() === maintenant.getFullYear()
  }).length

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Message de notification */}
      {message && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg ${
            message.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
          }`}
        >
          {message.text}
        </motion.div>
      )}

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-2">Gestion des Contrats</h1>
          <p className="text-zinc-600 dark:text-zinc-400">Gérez tous vos contrats clients et leurs lignes</p>
        </div>
        <button 
          onClick={() => setModalOuvert(true)}
          className="px-4 py-2.5 bg-gradient-to-br from-[#002a7a] to-[#003d9e] text-white font-semibold rounded-lg hover:shadow-lg transition-all"
        >
          + Nouveau Contrat
        </button>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#002a7a]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{contrats.length}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Total contrats</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{totalLignes}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Total lignes</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#e05500]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#e05500]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{caTotal.toLocaleString()}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">CA mensuel (F CFA)</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{nouveauxCeMois}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Nouveaux ce mois</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Filtres */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <svg className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
              </svg>
              <input type="text" placeholder="Rechercher par numéro, raison sociale, nom..." value={recherche}
                onChange={(e) => setRecherche(e.target.value)}
                className="pl-10 pr-4 py-2 w-full bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none"/>
            </div>
          </div>
          <select value={filtreType} onChange={(e) => setFiltreType(e.target.value)}
            className="px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none">
            <option value="tous">Tous les types</option>
            <option value="ENTREPRISE">Entreprises</option>
            <option value="PARTICULIER">Particuliers</option>
          </select>
          <select value={filtreStatut} onChange={(e) => setFiltreStatut(e.target.value)}
            className="px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none">
            <option value="tous">Tous les statuts</option>
            <option value="ACTIF">Actifs</option>
            <option value="SUSPENDU">Suspendus</option>
            <option value="RESILIE">Résiliés</option>
          </select>
        </div>
      </motion.div>

      {/* Grid de cartes */}
      {chargement ? (
        <div className="min-h-[40vh] flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-zinc-300 border-t-[#002a7a] rounded-full animate-spin" />
            <span className="text-sm text-zinc-600">Chargement des contrats...</span>
          </div>
        </div>
      ) : erreur ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12">
          <p className="text-red-600 text-lg mb-4">{erreur}</p>
          <button 
            onClick={chargerContrats}
            className="px-4 py-2 bg-[#002a7a] text-white rounded-lg hover:bg-[#003399]"
          >
            Réessayer
          </button>
        </motion.div>
      ) : contratsFiltres.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {contratsFiltres.map((contrat, idx) => (
            <ContratCard key={contrat.id} contrat={contrat} delay={idx * 0.05} onVoirDetails={handleVoirDetails} />
          ))}
        </div>
      ) : (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12">
          <svg className="w-16 h-16 mx-auto text-zinc-400 mb-4" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p className="text-zinc-500 text-lg">Aucun contrat trouvé</p>
        </motion.div>
      )}

      {modalOuvert && <ModalNouveauContrat onClose={() => setModalOuvert(false)} onCreate={handleCreerContrat} />}
    </div>
  )
}
