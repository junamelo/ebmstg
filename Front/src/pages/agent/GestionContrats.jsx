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
  const [filtreStatutFact, setFiltreStatutFact] = useState('tous')
  const [filtreResilie, setFiltreResilie] = useState('non_resilie')
  const [pageCourante, setPageCourante] = useState(1)
  const [demandes, setDemandes] = useState([])
  const [traitementDemande, setTraitementDemande] = useState(null)
  const [demandeDetail, setDemandeDetail] = useState(null)
  const [motifRejet, setMotifRejet] = useState('')
  const [rejetOuvert, setRejetOuvert] = useState(false)
  const ITEMS_PAR_PAGE = 6

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
              telephone: company.payeur_info?.telephone || '',
              dateCreation: company.date_creation,
              statut: company.statut || 'ACTIF',
              typeContrat: company.categorie || '',
              est_resilie: company.est_resilie || false,
              statut_factures: company.statut_factures || 'EN_ATTENTE',
              commercial: company.commercial_info || null,
              lignes: lignes.map(l => ({
                id: l.id,
                numero: l.msisdn,
                employe: l.employe_info ? {
                  nom: l.employe_info.nom?.split(' ')[1] || '',
                  prenom: l.employe_info.nom?.split(' ')[0] || ''
                } : null,
                statut: l.statut || 'ACTIF'
              })),
            }
          } catch (error) {
            console.error(`Erreur chargement lignes pour ${company.id}:`, error)
            return {
              id: company.id,
              numeroContrat: company.compte,
              typePayeur: 'ENTREPRISE',
              raisonSociale: company.raison_sociale || company.nom_commercial,
              email: company.payeur_info?.email || '',
              telephone: company.payeur_info?.telephone || '',
              dateCreation: company.date_creation,
              statut: company.statut || 'ACTIF',
              typeContrat: company.categorie || '',
              est_resilie: company.est_resilie || false,
              statut_factures: company.statut_factures || 'EN_ATTENTE',
              commercial: company.commercial_info || null,
              lignes: [],
            }
          }
        })
      )
      
      setContrats(contratsAvecLignes)
      try {
        const demandesResponse = await api.get('/billing/contract-requests/')
        const demandesData = demandesResponse.data.results || demandesResponse.data || []
        setDemandes(Array.isArray(demandesData) ? demandesData : [])
      } catch (demandesError) {
        console.error('Erreur chargement demandes de contrats:', demandesError)
      }
    } catch (error) {
      console.error('Erreur chargement contrats:', error)
      setErreur('Impossible de charger les contrats')
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => {
    setPageCourante(1)
  }, [recherche, filtreStatut, filtreType, filtreStatutFact, filtreResilie])

  const contratsFiltres = contrats.filter(contrat => {
    const matchStatut = filtreStatut === 'tous' || contrat.statut === filtreStatut
    const matchType = filtreType === 'tous' || contrat.typePayeur === filtreType
    const matchStatutFact = filtreStatutFact === 'tous' || contrat.statut_factures === filtreStatutFact
    const matchResilie = filtreResilie === 'tous' ||
      (filtreResilie === 'resilie' && contrat.est_resilie) ||
      (filtreResilie === 'non_resilie' && !contrat.est_resilie)
    const matchRecherche = recherche === '' ||
      contrat.numeroContrat.toLowerCase().includes(recherche.toLowerCase()) ||
      (contrat.raisonSociale && contrat.raisonSociale.toLowerCase().includes(recherche.toLowerCase()))
    return matchStatut && matchType && matchStatutFact && matchResilie && matchRecherche
  })

  const handleCreerContrat = async (payload) => {
    try {
      // 1) Créer le compte payeur
      const payeurResp = await api.post('/auth/users/', payload.payeur)
      const payeurId = payeurResp.data?.id

      // 2) Créer le contrat lié à ce payeur
      await api.post('/billing/companies/', {
        ...payload.contrat,
        payeur: payeurId,
      })

      setMessage({ type: 'success', text: 'Payeur et contrat créés avec succès' })
      setModalOuvert(false)
      chargerContrats()
    } catch (error) {
      const data = error.response?.data || {}
      const msg = data.compte?.[0] || data.username?.[0] || data.telephone?.[0] || data.payeur?.[0] || data.error || data.detail || 'Erreur lors de la création'
      setMessage({ type: 'error', text: msg })
    }
  }

  const handleVoirDetails = (contratId) => {
    navigate(`/agent/contrats/${contratId}`)
  }

  const traiterDemande = async (demande, action, commentaire = '') => {
    if (action === 'reject' && !commentaire.trim()) {
      setMessage({ type: 'error', text: 'Le motif du rejet est obligatoire.' })
      return
    }
    /*
    if (action === 'reject') {
      commentaire = window.prompt('Indiquez le motif du rejet :') || ''
      if (!commentaire.trim()) return
    } else if (!window.confirm(`Valider la demande ${demande.compte_propose} et créer le contrat ?`)) {
      return
    }

    */
    try {
      setTraitementDemande(demande.id)
      await api.post(`/billing/contract-requests/${demande.id}/${action}/`, { commentaire })
      setMessage({ type: 'success', text: action === 'approve' ? 'Demande validée : le contrat et le payeur ont été créés.' : 'Demande rejetée.' })
      setDemandeDetail(null)
      setMotifRejet('')
      setRejetOuvert(false)
      await chargerContrats()
    } catch (error) {
      const data = error.response?.data || {}
      setMessage({ type: 'error', text: data.error || data.detail || 'Impossible de traiter cette demande.' })
    } finally {
      setTraitementDemande(null)
    }
  }

  const totalLignes = contrats.reduce((sum, c) => sum + c.lignes.length, 0)
  const nbPages = Math.ceil(contratsFiltres.length / ITEMS_PAR_PAGE)
  const contratsAffichees = contratsFiltres.slice(
    (pageCourante - 1) * ITEMS_PAR_PAGE,
    pageCourante * ITEMS_PAR_PAGE
  )

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

      {demandes.filter(d => d.statut === 'PENDING').length > 0 && (
        <section className="rounded-xl border border-amber-200 bg-amber-50 p-5">
          <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="font-bold text-amber-950">Demandes de contrats à valider</h2>
              <p className="text-sm text-amber-800">Un contrat et son compte payeur ne sont créés qu'après votre validation.</p>
            </div>
            <span className="w-fit rounded-full bg-amber-200 px-2.5 py-1 text-xs font-semibold text-amber-900">
              {demandes.filter(d => d.statut === 'PENDING').length} en attente
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-sm">
              <thead className="text-left text-amber-900">
                <tr><th className="p-2">Code contrat</th><th className="p-2">Client</th><th className="p-2">Commercial</th><th className="p-2">Soumise le</th><th className="p-2 text-right">Décision</th></tr>
              </thead>
              <tbody>
                {demandes.filter(d => d.statut === 'PENDING').map(demande => (
                  <tr key={demande.id} className="border-t border-amber-200">
                    <td className="p-2 font-semibold">{demande.compte_propose}</td>
                    <td className="p-2">{demande.raison_sociale || '—'}</td>
                    <td className="p-2">{demande.commercial_nom}</td>
                    <td className="p-2">{demande.date_soumission ? new Date(demande.date_soumission).toLocaleDateString('fr-FR') : '—'}</td>
                    <td className="p-2 text-right">
                      <button onClick={() => { setDemandeDetail(demande); setMotifRejet(''); setRejetOuvert(false) }} className="rounded-md bg-[#002a7a] px-3 py-1.5 font-medium text-white">Voir le dossier</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
          <select value={filtreResilie} onChange={(e) => setFiltreResilie(e.target.value)}
            className="px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none">
            <option value="tous">Tous (résilié inclus)</option>
            <option value="non_resilie">Non résiliés</option>
            <option value="resilie">Résiliés</option>
          </select>
          <select value={filtreStatutFact} onChange={(e) => setFiltreStatutFact(e.target.value)}
            className="px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none">
            <option value="tous">Tous statuts fact.</option>
            <option value="ACTIF">Actif</option>
            <option value="EN_ATTENTE">En attente</option>
            <option value="SUSPENDU">Suspendu</option>
            <option value="CLOS">Clos</option>
          </select>
          <select value={filtreStatut} onChange={(e) => setFiltreStatut(e.target.value)}
            className="px-4 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none">
            <option value="tous">Tous statuts</option>
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
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {contratsAffichees.map((contrat, idx) => (
              <ContratCard key={contrat.id} contrat={contrat} delay={idx * 0.05} onVoirDetails={handleVoirDetails} />
            ))}
          </div>

          {nbPages > 1 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Affichage {(pageCourante - 1) * ITEMS_PAR_PAGE + 1}–{Math.min(pageCourante * ITEMS_PAR_PAGE, contratsFiltres.length)} sur <strong>{contratsFiltres.length}</strong> contrat(s)
              </p>
              <div className="flex items-center gap-1.5">
                <button
                  disabled={pageCourante === 1}
                  onClick={() => setPageCourante(p => p - 1)}
                  className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-sm text-zinc-600 dark:text-zinc-400 disabled:opacity-40 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
                >
                  &#8592; Préc.
                </button>
                {Array.from({ length: nbPages }, (_, i) => i + 1).map(p => (
                  <button
                    key={p}
                    onClick={() => setPageCourante(p)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      p === pageCourante
                        ? 'bg-[#002a7a] text-white shadow-sm'
                        : 'border border-zinc-200 dark:border-zinc-700 text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800'
                    }`}
                  >
                    {p}
                  </button>
                ))}
                <button
                  disabled={pageCourante === nbPages}
                  onClick={() => setPageCourante(p => p + 1)}
                  className="px-3 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-700 text-sm text-zinc-600 dark:text-zinc-400 disabled:opacity-40 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors"
                >
                  Suiv. &#8594;
                </button>
              </div>
            </motion.div>
          )}
        </>
      ) : (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12">
          <svg className="w-16 h-16 mx-auto text-zinc-400 mb-4" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
            <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p className="text-zinc-500 text-lg">Aucun contrat trouvé</p>
        </motion.div>
      )}

      {demandeDetail && (
        <div className="fixed inset-0 z-[1100] flex items-center justify-center bg-black/45 p-4">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="sticky top-0 flex items-center justify-between border-b border-zinc-200 bg-white px-6 py-4">
              <div><h3 className="font-bold text-zinc-900">Dossier de demande : {demandeDetail.compte_propose}</h3><p className="text-sm text-zinc-500">Soumis par {demandeDetail.commercial_nom} le {demandeDetail.date_soumission ? new Date(demandeDetail.date_soumission).toLocaleDateString('fr-FR') : '—'}</p></div>
              <button onClick={() => setDemandeDetail(null)} className="rounded-md px-2 py-1 text-zinc-500 hover:bg-zinc-100">✕</button>
            </div>
            <div className="space-y-5 p-6 text-sm">
              <section><h4 className="mb-2 font-semibold text-zinc-900">Informations du contrat</h4><div className="grid grid-cols-1 gap-3 sm:grid-cols-2"><div><p className="text-zinc-500">Raison sociale</p><p className="font-medium">{demandeDetail.payload?.contrat?.raison_sociale || demandeDetail.raison_sociale || '—'}</p></div><div><p className="text-zinc-500">Catégorie</p><p className="font-medium">{demandeDetail.payload?.contrat?.categorie || '—'}</p></div><div><p className="text-zinc-500">Mode de règlement</p><p className="font-medium">{demandeDetail.payload?.contrat?.mode_reglement || '—'}</p></div><div><p className="text-zinc-500">Période</p><p className="font-medium">{demandeDetail.payload?.contrat?.date_effet || '—'} au {demandeDetail.payload?.contrat?.date_fin || '—'}</p></div><div><p className="text-zinc-500">Adresse</p><p className="font-medium">{demandeDetail.payload?.contrat?.adresse || '—'}</p></div><div><p className="text-zinc-500">Observation</p><p className="font-medium">{demandeDetail.payload?.contrat?.observation || '—'}</p></div></div></section>
              <section className="border-t border-zinc-200 pt-5"><h4 className="mb-2 font-semibold text-zinc-900">Compte payeur à créer</h4><div className="grid grid-cols-1 gap-3 sm:grid-cols-2"><div><p className="text-zinc-500">Nom</p><p className="font-medium">{demandeDetail.payload?.payeur?.first_name} {demandeDetail.payload?.payeur?.last_name}</p></div><div><p className="text-zinc-500">Identifiant</p><p className="font-medium">{demandeDetail.payload?.payeur?.username || '—'}</p></div><div><p className="text-zinc-500">Téléphone</p><p className="font-medium">{demandeDetail.payload?.payeur?.telephone || '—'}</p></div><div><p className="text-zinc-500">E-mail</p><p className="font-medium">{demandeDetail.payload?.payeur?.email || '—'}</p></div></div></section>
              <section className="border-t border-zinc-200 pt-5"><h4 className="mb-2 font-semibold text-zinc-900">Services prévus</h4><div className="grid grid-cols-2 gap-2 text-zinc-700"><span>Facture détaillée : {demandeDetail.payload?.contrat?.facture_detaillee_defaut ? 'Oui' : 'Non'}</span><span>Roaming : {demandeDetail.payload?.contrat?.roaming_defaut ? 'Oui' : 'Non'}</span><span>Internet : {demandeDetail.payload?.contrat?.internet_defaut ? 'Oui' : 'Non'}</span><span>International : {demandeDetail.payload?.contrat?.international_defaut ? 'Oui' : 'Non'}</span><span>No Limit : {demandeDetail.payload?.contrat?.option_nolimit_defaut || 'Non'}</span><span>BlackBerry : {demandeDetail.payload?.contrat?.option_blackberry_defaut || 'Non'}</span></div></section>
              {rejetOuvert && <div><label className="mb-1 block font-semibold text-red-800">Motif du rejet *</label><textarea value={motifRejet} onChange={e => setMotifRejet(e.target.value)} className="min-h-24 w-full rounded-lg border border-red-300 p-3 outline-none focus:ring-2 focus:ring-red-400" placeholder="Expliquez précisément au commercial pourquoi le dossier est rejeté." /></div>}
            </div>
            <div className="sticky bottom-0 flex flex-wrap justify-end gap-2 border-t border-zinc-200 bg-white px-6 py-4">
              <button onClick={() => setDemandeDetail(null)} className="rounded-lg border border-zinc-300 px-4 py-2 text-sm">Fermer</button>
              {!rejetOuvert ? <button onClick={() => setRejetOuvert(true)} disabled={traitementDemande === demandeDetail.id} className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-700">Rejeter</button> : <button onClick={() => traiterDemande(demandeDetail, 'reject', motifRejet)} disabled={traitementDemande === demandeDetail.id} className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50">Confirmer le rejet</button>}
              <button onClick={() => traiterDemande(demandeDetail, 'approve')} disabled={traitementDemande === demandeDetail.id} className="rounded-lg bg-[#002a7a] px-4 py-2 text-sm font-medium text-white disabled:opacity-50">Valider et créer le contrat</button>
            </div>
          </div>
        </div>
      )}

      {modalOuvert && <ModalNouveauContrat onClose={() => setModalOuvert(false)} onCreate={handleCreerContrat} />}
    </div>
  )
}
