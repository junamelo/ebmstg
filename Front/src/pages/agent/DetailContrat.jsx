import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../services/api'

export default function DetailContrat() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [ongletActif, setOngletActif] = useState('infos')
  const [contrat, setContrat] = useState(null)
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState(null)
  const [modalAffectation, setModalAffectation] = useState(null)
  const [modalAjoutLigne, setModalAjoutLigne] = useState(false)
  const [modalModifierServices, setModalModifierServices] = useState(null)
  const [servicesLigne, setServicesLigne] = useState({})
  const [employes, setEmployes] = useState([])
  const [message, setMessage] = useState(null)
  const [auditLog, setAuditLog] = useState([])
  const [auditChargement, setAuditChargement] = useState(false)

  useEffect(() => {
    chargerContrat()
    chargerEmployes()
    chargerAudit()
  }, [id])

  const chargerEmployes = async () => {
    try {
      // Charger tous les employés disponibles pour affectation
      const response = await api.get('/auth/users/', { params: { role: 'EMPLOYE' } })
      const users = response.data.results || response.data
      setEmployes(users)
    } catch (error) {
      console.error('Erreur chargement employés:', error)
    }
  }

  const chargerContrat = async () => {
    try {
      setChargement(true)
      setErreur(null)
      // Charger les données de l'entreprise
      const response = await api.get(`/billing/companies/${id}/`)
      const company = response.data
      
      // Charger les lignes de l'entreprise
      const lignesResponse = await api.get(`/billing/lines/`, { params: { company: id } })
      const lignes = lignesResponse.data.results || lignesResponse.data
      
      // Adapter les données
      setContrat({
        id: company.id,
        numeroContrat: company.compte,
        typePayeur: 'ENTREPRISE',
        raisonSociale: company.raison_sociale || company.nom_commercial,
        email: company.payeur_info?.email || '',
        telephone: '',
        adresse: company.adresse || '',
        dateCreation: company.date_creation,
        statut: company.statut || 'ACTIF',
        typeContrat: company.categorie || '',
        lignes: lignes.map(l => {
          // Construire liste des services actifs
          const services = []
          if (l.facture_detaillee) services.push('Facturation détaillée')
          if (l.option_nolimit) services.push(`No Limit: ${l.option_nolimit}`)
          if (l.option_blackberry) services.push(`BlackBerry: ${l.option_blackberry}`)
          if (l.est_incognito) services.push('Incognito')
          if (l.est_roaming) services.push('Roaming')
          if (l.est_internet) services.push('Internet')
          if (l.est_international) services.push('International')
          if (l.est_non_revenu) services.push('Non Revenu')
          
          return {
            id: l.id,
            numero: l.msisdn,
            employe: l.employe_info ? {
              id: l.employe,
              nom: l.employe_info.nom?.split(' ').pop() || '',
              prenom: l.employe_info.nom?.split(' ')[0] || '',
              email: l.employe_info.email || ''
            } : null,
            statut: l.statut || 'ACTIF',
            dateActivation: l.date_creation,
            services: services,
            // Garder les données brutes pour modification
            _raw: {
              facture_detaillee: l.facture_detaillee,
              option_nolimit: l.option_nolimit || '',
              option_blackberry: l.option_blackberry || '',
              est_incognito: l.est_incognito,
              est_roaming: l.est_roaming,
              est_internet: l.est_internet,
              est_international: l.est_international,
              est_non_revenu: l.est_non_revenu
            },
            forfaits: [],
            consommation: { voix: 0, sms: 0, data: 0 },
            montantEstime: parseFloat(l.forfait) || 0
          }
        }),
        historiqueFacturation: [],
        est_resilie: company.est_resilie || false,
        date_resiliation: company.date_resiliation || null,
        motif_resiliation: company.motif_resiliation || '',
        statut_factures: company.statut_factures || '',
        mode_reglement: company.mode_reglement || '',
        commercial: company.commercial_info || null,
      })
    } catch (error) {
      console.error('Erreur chargement contrat:', error)
      setErreur('Impossible de charger les détails du contrat')
    } finally {
      setChargement(false)
    }
  }

  const chargerAudit = async () => {
    try {
      setAuditChargement(true)
      const r = await api.get(`/billing/companies/${id}/historique/`)
      setAuditLog(r.data.results || r.data || [])
    } catch {
      setAuditLog([])
    } finally {
      setAuditChargement(false)
    }
  }

  const affecterEmploye = async (ligneId, employeId) => {
    try {
      await api.post(`/billing/lines/${ligneId}/assigner_employe/`, { employe_id: employeId })
      setMessage({ type: 'success', text: 'Employé affecté avec succès' })
      chargerContrat()
      setModalAffectation(null)
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Erreur lors de l\'affectation'
      setMessage({ type: 'error', text: errorMsg })
    }
  }

  const retirerEmploye = async (ligneId) => {
    if (!window.confirm('Retirer l\'employé de cette ligne ?')) return
    try {
      await api.post(`/billing/lines/${ligneId}/retirer_employe/`)
      setMessage({ type: 'success', text: 'Employé retiré avec succès' })
      chargerContrat()
    } catch (error) {
      setMessage({ type: 'error', text: 'Erreur lors du retrait' })
    }
  }

  const ajouterLigne = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    try {
      // Ne pas envoyer les valeurs par défaut des services
      // Le backend appliquera automatiquement les valeurs du contrat
      await api.post('/billing/lines/', {
        company: parseInt(id),
        msisdn: formData.get('msisdn'),
        utilisateur: formData.get('utilisateur') || '',
        cycle: formData.get('cycle'),
        forfait: parseFloat(formData.get('forfait')) || 0
        // Les services seront hérités automatiquement du contrat
        // employe: optionnel, laissé vide pour l'instant
      })
      setMessage({ type: 'success', text: 'Ligne ajoutée avec succès' })
      setModalAjoutLigne(false)
      chargerContrat()
      e.target.reset()
    } catch (error) {
      const errorMsg = error.response?.data?.msisdn?.[0] || error.response?.data?.error || 'Erreur lors de l\'ajout'
      setMessage({ type: 'error', text: errorMsg })
    }
  }

  const ouvrirModalServices = (ligne) => {
    setModalModifierServices(ligne)
    setServicesLigne(ligne._raw || {})
  }

  const modifierServicesLigne = async () => {
    if (!modalModifierServices) return
    
    try {
      await api.patch(`/billing/lines/${modalModifierServices.id}/`, servicesLigne)
      setMessage({ type: 'success', text: 'Services modifiés avec succès' })
      setModalModifierServices(null)
      setServicesLigne({})
      chargerContrat()
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Erreur lors de la modification'
      setMessage({ type: 'error', text: errorMsg })
    }
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

  if (erreur || !contrat) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{erreur || 'Contrat introuvable'}</p>
          <button
            onClick={() => navigate('/agent/contrats')}
            className="px-4 py-2 bg-[#002a7a] text-white rounded-lg hover:bg-[#003399]"
          >
            Retour aux contrats
          </button>
        </div>
      </div>
    )
  }

  const lignesActives = contrat.lignes.filter(l => l.statut === 'ACTIF').length
  const caMensuel = contrat.lignes.reduce((sum, l) => sum + l.montantEstime, 0)

  const getStatutStyle = (statut) => {
    return statut === 'ACTIF'
      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
      : statut === 'SUSPENDU'
      ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Message de notification */}
      {message && (
        <div className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg ${
          message.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        }`}>
          {message.text}
        </div>
      )}

      {/* Modal d'affectation */}
      {modalAffectation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold mb-4">Affecter un employé</h3>
            <p className="text-sm text-zinc-600 mb-4">Ligne : {modalAffectation.numero}</p>
            {employes.length === 0 ? (
              <p className="text-sm text-zinc-500 mb-4">Aucun employé disponible</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {employes.map(emp => (
                  <button
                    key={emp.id}
                    onClick={() => affecterEmploye(modalAffectation.id, emp.id)}
                    className="w-full text-left px-4 py-3 hover:bg-zinc-100 rounded-lg"
                  >
                    <p className="font-semibold">{emp.first_name} {emp.last_name}</p>
                    <p className="text-sm text-zinc-500">{emp.email}</p>
                  </button>
                ))}
              </div>
            )}
            <button
              onClick={() => setModalAffectation(null)}
              className="mt-4 w-full px-4 py-2 bg-zinc-200 rounded-lg hover:bg-zinc-300"
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      {/* Modal ajout ligne */}
      {modalAjoutLigne && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-bold mb-4">Ajouter une ligne</h3>
            <form onSubmit={ajouterLigne} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">MSISDN *</label>
                <input
                  name="msisdn"
                  required
                  pattern="[0-9]{8}"
                  placeholder="99123456"
                  className="w-full px-3 py-2 border rounded-lg"
                />
                <p className="text-xs text-zinc-500 mt-1">8 chiffres sans espaces</p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Utilisateur</label>
                <input
                  name="utilisateur"
                  placeholder="Nom de l'utilisateur"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Cycle *</label>
                <select name="cycle" required className="w-full px-3 py-2 border rounded-lg">
                  <option value="HYB">Hybride (HYB)</option>
                  <option value="OP">Open (OP)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Forfait mensuel (F)</label>
                <input
                  name="forfait"
                  type="number"
                  step="0.01"
                  placeholder="0"
                  defaultValue="0"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-[#002a7a] text-white rounded-lg hover:bg-[#003399]"
                >
                  Ajouter
                </button>
                <button
                  type="button"
                  onClick={() => setModalAjoutLigne(false)}
                  className="flex-1 px-4 py-2 bg-zinc-200 rounded-lg hover:bg-zinc-300"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal modification services ligne */}
      {modalModifierServices && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm overflow-y-auto p-4">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 my-8">
            <h3 className="text-lg font-bold mb-2">Modifier les services de la ligne</h3>
            <p className="text-sm text-zinc-600 mb-4">Ligne : {modalModifierServices.numero}</p>
            <p className="text-xs text-zinc-500 mb-6 bg-amber-50 border border-amber-200 rounded-lg p-3">
              ⚠️ Les modifications s'appliquent uniquement à cette ligne. Le contrat et les autres lignes ne seront pas affectés.
            </p>
            
            <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
              {/* Checkboxes pour services booléens */}
              <div className="grid grid-cols-2 gap-3">
                <label className="flex items-center gap-3 p-3 rounded-lg border border-zinc-300 hover:bg-zinc-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={servicesLigne.facture_detaillee || false}
                    onChange={(e) => setServicesLigne(prev => ({ ...prev, facture_detaillee: e.target.checked }))}
                    className="w-4 h-4 text-[#002a7a] border-zinc-300 rounded focus:ring-[#002a7a]"
                  />
                  <span className="text-sm font-medium text-zinc-700">Facturation détaillée</span>
                </label>

                <label className="flex items-center gap-3 p-3 rounded-lg border border-zinc-300 hover:bg-zinc-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={servicesLigne.est_incognito || false}
                    onChange={(e) => setServicesLigne(prev => ({ ...prev, est_incognito: e.target.checked }))}
                    className="w-4 h-4 text-[#002a7a] border-zinc-300 rounded focus:ring-[#002a7a]"
                  />
                  <span className="text-sm font-medium text-zinc-700">Incognito</span>
                </label>

                <label className="flex items-center gap-3 p-3 rounded-lg border border-zinc-300 hover:bg-zinc-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={servicesLigne.est_roaming || false}
                    onChange={(e) => setServicesLigne(prev => ({ ...prev, est_roaming: e.target.checked }))}
                    className="w-4 h-4 text-[#002a7a] border-zinc-300 rounded focus:ring-[#002a7a]"
                  />
                  <span className="text-sm font-medium text-zinc-700">Roaming</span>
                </label>

                <label className="flex items-center gap-3 p-3 rounded-lg border border-zinc-300 hover:bg-zinc-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={servicesLigne.est_internet || false}
                    onChange={(e) => setServicesLigne(prev => ({ ...prev, est_internet: e.target.checked }))}
                    className="w-4 h-4 text-[#002a7a] border-zinc-300 rounded focus:ring-[#002a7a]"
                  />
                  <span className="text-sm font-medium text-zinc-700">Internet</span>
                </label>

                <label className="flex items-center gap-3 p-3 rounded-lg border border-zinc-300 hover:bg-zinc-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={servicesLigne.est_international || false}
                    onChange={(e) => setServicesLigne(prev => ({ ...prev, est_international: e.target.checked }))}
                    className="w-4 h-4 text-[#002a7a] border-zinc-300 rounded focus:ring-[#002a7a]"
                  />
                  <span className="text-sm font-medium text-zinc-700">International</span>
                </label>

                <label className="flex items-center gap-3 p-3 rounded-lg border border-zinc-300 hover:bg-zinc-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={servicesLigne.est_non_revenu || false}
                    onChange={(e) => setServicesLigne(prev => ({ ...prev, est_non_revenu: e.target.checked }))}
                    className="w-4 h-4 text-[#002a7a] border-zinc-300 rounded focus:ring-[#002a7a]"
                  />
                  <span className="text-sm font-medium text-zinc-700">Non Revenu</span>
                </label>
              </div>

              {/* Champs texte pour No Limit et BlackBerry */}
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <label className="block text-sm font-medium text-zinc-700 mb-2">Option No Limit</label>
                  <input
                    type="text"
                    value={servicesLigne.option_nolimit || ''}
                    onChange={(e) => setServicesLigne(prev => ({ ...prev, option_nolimit: e.target.value }))}
                    placeholder="Ex: No Limit 5000"
                    className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  />
                  <p className="text-xs text-zinc-500 mt-1">Laissez vide pour désactiver</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-zinc-700 mb-2">Option BlackBerry</label>
                  <input
                    type="text"
                    value={servicesLigne.option_blackberry || ''}
                    onChange={(e) => setServicesLigne(prev => ({ ...prev, option_blackberry: e.target.value }))}
                    placeholder="Ex: BlackBerry Pro"
                    className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  />
                  <p className="text-xs text-zinc-500 mt-1">Laissez vide pour désactiver</p>
                </div>
              </div>
            </div>

            <div className="flex gap-2 mt-6 pt-4 border-t">
              <button
                type="button"
                onClick={modifierServicesLigne}
                className="flex-1 px-4 py-2 bg-[#002a7a] text-white rounded-lg hover:bg-[#003399]"
              >
                Enregistrer les modifications
              </button>
              <button
                type="button"
                onClick={() => {
                  setModalModifierServices(null)
                  setServicesLigne({})
                }}
                className="flex-1 px-4 py-2 bg-zinc-200 rounded-lg hover:bg-zinc-300"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header avec retour */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <button onClick={() => navigate('/agent/contrats')}
          className="inline-flex items-center gap-2 text-[#002a7a] hover:text-[#003d9e] font-semibold mb-4">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Retour aux contrats
        </button>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
                {contrat.typePayeur === 'ENTREPRISE' ? contrat.raisonSociale : `${contrat.prenom} ${contrat.nom}`}
              </h1>
              <span className={`px-3 py-1 rounded-full text-sm font-bold ${getStatutStyle(contrat.statut)}`}>
                {contrat.statut}
              </span>
            </div>
            <p className="text-zinc-600 dark:text-zinc-400 font-mono text-lg">{contrat.numeroContrat}</p>
          </div>
          <button className="px-4 py-2.5 bg-gradient-to-br from-[#e05500] to-[#c2410c] text-white font-semibold rounded-lg hover:shadow-lg transition-all" onClick={() => setModalAjoutLigne(true)}>
            + Nouvelle Ligne
          </button>
        </div>
      </motion.div>

      {/* Stats rapides */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#002a7a]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{contrat.lignes.length}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Total lignes</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{lignesActives}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Lignes actives</p>
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
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{caMensuel.toLocaleString()}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">CA mensuel (F)</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">-</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Engagement (non défini)</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Onglets */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden">
        <div className="border-b border-zinc-200 dark:border-zinc-800">
          <div className="flex">
            {['infos', 'lignes', 'historique_contrat'].map((onglet) => (
              <button key={onglet} onClick={() => setOngletActif(onglet)}
                className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                  ongletActif === onglet
                    ? 'text-[#002a7a] border-b-2 border-[#002a7a] bg-[#002a7a]/5'
                    : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'
                }`}>
                {onglet === 'infos' && 'Informations'}
                {onglet === 'lignes' && `Lignes (${contrat.lignes.length})`}
                {onglet === 'historique_contrat' && 'Historique'}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {/* Onglet Infos */}
          {ongletActif === 'infos' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-bold text-zinc-500 uppercase mb-4">Informations Client</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Email</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">{contrat.email}</p>
                    </div>
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Téléphone</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">{contrat.telephone}</p>
                    </div>
                    {contrat.adresse && (
                      <div>
                        <p className="text-xs text-zinc-500 mb-1">Adresse</p>
                        <p className="text-zinc-900 dark:text-white font-semibold">{contrat.adresse}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-zinc-500 uppercase mb-4">Détails Contrat</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Type de contrat</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">{contrat.typeContrat || 'Non défini'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Date de création</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">
                        {new Date(contrat.dateCreation).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                    {contrat.mode_reglement && (
                      <div>
                        <p className="text-xs text-zinc-500 mb-1">Mode de règlement</p>
                        <p className="text-zinc-900 dark:text-white font-semibold">{contrat.mode_reglement}</p>
                      </div>
                    )}
                    {contrat.commercial && (
                      <div>
                        <p className="text-xs text-zinc-500 mb-1">Commercial</p>
                        <p className="text-zinc-900 dark:text-white font-semibold">{contrat.commercial.prenom} {contrat.commercial.nom}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              {contrat.est_resilie && (
                <div className="col-span-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm font-bold text-red-700 mb-2">Contrat résilié</p>
                  <p className="text-xs text-red-600">Date : {contrat.date_resiliation ? new Date(contrat.date_resiliation).toLocaleDateString('fr-FR') : '—'}</p>
                  <p className="text-xs text-red-600">Motif : {contrat.motif_resiliation}</p>
                </div>
              )}
            </motion.div>
          )}

          {/* Onglet Lignes */}
          {ongletActif === 'lignes' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-zinc-50 dark:bg-zinc-900/50 border-b border-zinc-200 dark:border-zinc-800">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Numéro</th>
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Employé</th>
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Services actifs</th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Consommation</th>
                      <th className="px-4 py-3 text-center text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Statut</th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                    {contrat.lignes.map((ligne, idx) => (
                      <tr key={ligne.id} className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/40">
                        <td className="px-4 py-4 font-mono font-semibold text-zinc-900 dark:text-white">{ligne.numero}</td>
                        <td className="px-4 py-4">
                          {ligne.employe ? (
                            <>
                              <p className="font-semibold text-zinc-900 dark:text-white">{ligne.employe.prenom} {ligne.employe.nom}</p>
                              <p className="text-sm text-zinc-500">{ligne.employe.email}</p>
                            </>
                          ) : (
                            <span className="text-sm text-zinc-400 italic">Non affecté</span>
                          )}
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex flex-wrap gap-1 max-w-xs">
                            {ligne.services && ligne.services.map((service, i) => (
                              <span key={i} className="px-2 py-0.5 rounded text-xs font-medium bg-[#002a7a]/10 text-[#002a7a]">
                                {service}
                              </span>
                            ))}
                            {(!ligne.services || ligne.services.length === 0) && (
                              <span className="text-xs text-zinc-400 italic">Aucun service actif</span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-4 text-right text-sm">
                          <p>{ligne.consommation.voix} min</p>
                          <p>{ligne.consommation.sms} SMS</p>
                          <p>{ligne.consommation.data} Go</p>
                        </td>
                        <td className="px-4 py-4 text-center">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getStatutStyle(ligne.statut)}`}>
                            {ligne.statut}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-right">
                          <div className="flex flex-col gap-1 items-end">
                            {ligne.employe ? (
                              <button
                                onClick={() => retirerEmploye(ligne.id)}
                                className="text-red-600 hover:text-red-800 text-sm font-medium"
                              >
                                Retirer employé
                              </button>
                            ) : (
                              <button
                                onClick={() => setModalAffectation(ligne)}
                                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                              >
                                Affecter employé
                              </button>
                            )}
                            <button
                              onClick={() => ouvrirModalServices(ligne)}
                              className="text-[#002a7a] hover:text-[#003399] text-sm font-medium"
                            >
                              Modifier services
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {/* Onglet Historique Contrat */}
          {ongletActif === 'historique_contrat' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              {auditChargement ? (
                <div className="py-8 flex justify-center">
                  <div className="w-6 h-6 border-2 border-zinc-200 border-t-[#002a7a] rounded-full animate-spin"/>
                </div>
              ) : auditLog.length === 0 ? (
                <p className="text-center text-zinc-400 text-sm py-8">Aucune action enregistrée</p>
              ) : (
                <div className="space-y-2">
                  {auditLog.map((a) => (
                    <div key={a.id} className="flex items-start gap-3 p-3 rounded-lg bg-zinc-50 border border-zinc-100">
                      <div className="w-8 h-8 rounded-full bg-[#002a7a]/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <svg className="w-4 h-4 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                        </svg>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-xs font-semibold text-zinc-700">{a.type_action}</span>
                          <span className="text-xs text-zinc-400 flex-shrink-0">{new Date(a.date_action).toLocaleString('fr-FR')}</span>
                        </div>
                        <p className="text-xs text-zinc-600 mt-0.5">{a.description}</p>
                        <p className="text-xs text-zinc-400 mt-0.5">Par : {a.utilisateur_nom}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
