import api from './api'

// Backend Django prêt - Plus besoin des mocks

// ─── PUBLICATION PDF ─────────────────────────────────────────
/**
 * Upload d'un bloc PDF de factures
 * Endpoint: POST /api/billing/invoices/upload_bulk_pdf/
 */
export const uploadBlocPdf = async (fichier, cycle, periodeDebut, periodeFin, onProgress, typeFacture = 'SOM') => {
  const formData = new FormData()
  formData.append('fichier', fichier)
  formData.append('auto_match', 'true')
  formData.append('type_facture', typeFacture)
  formData.append('cycle', cycle)
  formData.append('periode_debut', periodeDebut)
  formData.append('periode_fin', periodeFin)
  
  const response = await api.post('/billing/invoices/upload_bulk_pdf/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total))
    },
  })
  return response.data
}

/**
 * Récupère l'historique des publications
 * Endpoint: GET /api/billing/publications/
 */
export const getHistoriquePublications = async () => {
  const response = await api.get('/billing/publications/')
  return response.data.results || response.data
}

// ─── TARIFS ──────────────────────────────────────────────────
/**
 * Récupère la liste des tarifs
 * Endpoint: GET /api/billing/tarifs/
 */
export const getTarifs = async () => {
  const response = await api.get('/billing/tarifs/')
  return response.data.results || response.data
}

/**
 * Crée un nouveau tarif
 * Endpoint: POST /api/billing/tarifs/
 */
export const creerTarif = async (tarif) => {
  const response = await api.post('/billing/tarifs/', tarif)
  return response.data
}

/**
 * Modifie un tarif
 * Endpoint: PUT /api/billing/tarifs/{id}/
 */
export const modifierTarif = async (id, tarif) => {
  const response = await api.put(`/billing/tarifs/${id}/`, tarif)
  return response.data
}

/**
 * Désactive un tarif
 * Endpoint: PATCH /api/billing/tarifs/{id}/ avec is_active=false
 */
export const desactiverTarif = async (id) => {
  const response = await api.patch(`/billing/tarifs/${id}/`, { is_active: false })
  return response.data
}

/**
 * Active un tarif (et désactive les autres)
 * Endpoint: PATCH /api/billing/tarifs/{id}/ avec is_active=true
 */
export const activerTarif = async (id) => {
  const response = await api.patch(`/billing/tarifs/${id}/`, { is_active: true })
  return response.data
}

// ─── COMPTES ─────────────────────────────────────────────────
/**
 * Récupère la liste des utilisateurs
 * Endpoint: GET /api/auth/users/
 */
export const getUtilisateurs = async (filtres = {}) => {
  const params = new URLSearchParams(filtres)
  const response = await api.get(`/auth/users/?${params.toString()}`)
  return response.data.results || response.data
}

/**
 * Active un compte utilisateur
 * Endpoint: PATCH /api/auth/users/{id}/ avec is_active=true
 */
export const activerCompte = async (id) => {
  const response = await api.patch(`/auth/users/${id}/`, { is_active: true })
  return response.data
}

/**
 * Suspend un compte utilisateur
 * Endpoint: PATCH /api/auth/users/{id}/ avec is_active=false
 */
export const suspendreCompte = async (id) => {
  const response = await api.patch(`/auth/users/${id}/`, { is_active: false })
  return response.data
}

/**
 * Réinitialise le mot de passe d'un utilisateur (Admin)
 * Endpoint: POST /api/auth/users/{id}/reset_password/
 */
export const reinitialiserMotDePasseAdmin = async (id) => {
  const response = await api.post(`/auth/users/${id}/reset_password/`)
  return response.data
}

// ─── STATISTIQUES ────────────────────────────────────────────
/**
 * Récupère les statistiques admin
 * Endpoint: GET /api/billing/stats/admin/
 */
export const getStatistiques = async () => {
  const response = await api.get('/billing/stats/admin/')
  const data = response.data
  const global = data.statistiques_globales || {}
  return {
    ...data,
    totalContrats: global.total_entreprises || 0,
    totalLignesActives: global.total_lignes || 0,
    totalUtilisateursActifs: (data.stats_agents?.agents_actifs || 0) + (data.stats_utilisateurs?.total_payeurs || 0) + (data.stats_utilisateurs?.total_employes || 0),
    facturationMensuelle: data.evolution_mensuelle || [],
    historiquePublications: [],
    dernieresConnexions: [],
  }
}

/**
 * Récupère les statistiques payeur
 * Endpoint: GET /api/billing/stats/payeur/
 */
export const getStatsPayeur = async () => {
  const response = await api.get('/billing/stats/payeur/')
  const data = response.data
  const stats = data.statistiques || {}
  return {
    ...data,
    nombreLignesActives: stats.nombre_lignes || 0,
    lignesDetail: (data.lignes_a_surveiller || []).map(ligne => ({
      ...ligne, montant: ligne.montant_facture || 0, forfait: '-', statut: 'ACTIF'
    })),
    lignesASurveiller: [],
    dernieresSimulations: [],
  }
}

/**
 * Récupère les statistiques employé
 * Endpoint: GET /api/billing/stats/employe/
 */
export const getStatsEmploye = async () => {
  const response = await api.get('/billing/stats/employe/')
  const data = response.data
  return {
    ...data,
    dernieresSimulations: (data.simulations?.dernieres || []).map(simulation => ({
      date: simulation.date_simulation, montant: simulation.montant_estime
    }))
  }
}

/**
 * Récupère les statistiques de l'agent de facturation connecté.
 * Endpoint: GET /api/billing/stats/agent/
 */
export const getStatsAgentFacturation = async () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isChef = user.role === 'CHEF_FACTURATION'
  const response = await api.get(isChef ? '/billing/stats/chef/' : '/billing/stats/agent/')
  if (isChef) {
    const performance = response.data.performance_equipe || {}
    return {
      ...response.data,
      facturesNonPubliees: 0,
      erreursDecoupage: 0,
      lignesSansForfait: 0,
      servicesActifs: [],
      historiquePublications: (response.data.agents || []).map(agent => ({ date: '-', periode: agent.nom_complet || agent.email, nbFactures: agent.nombre_publications || 0, statut: 'TRAITEE' })),
      statistiques: {
        total_publications: performance.total_publications || 0,
        montant_total: performance.montant_total || 0,
        lignes_traitees: 0,
      },
      evolution_quotidienne: response.data.publications_periode || [],
      dernieres_publications: response.data.agents || [],
    }
  }
  const data = response.data
  return {
    ...data,
    facturesNonPubliees: 0,
    erreursDecoupage: 0,
    lignesSansForfait: 0,
    servicesActifs: [],
    historiquePublications: (data.dernieres_publications || []).map(publication => ({ date: publication.date_publication ? new Date(publication.date_publication).toLocaleDateString('fr-FR') : '-', periode: `${publication.periode_debut || ''} - ${publication.periode_fin || ''}`, nbFactures: publication.nombre_lignes_traitees || 0, statut: publication.statut || 'VALIDEE' })),
  }
}
