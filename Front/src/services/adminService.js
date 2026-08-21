import api from './api'
import {
  isDashboardDemo,
  DEMO_ADMIN_STATS,
  DEMO_AGENT_STATS,
  DEMO_PAYEUR_STATS,
  DEMO_EMPLOYE_STATS,
} from './dashboardDemo'

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

export const getStatutTraitementPdf = async (jobId) => {
  const response = await api.get(`/billing/invoices/pdf-jobs/${jobId}/`)
  return response.data
}

/**
 * Génère un gros bloc PDF de démonstration à partir de contrats ou lignes
 * existants, puis l'envoie au même traitement Celery que les PDF importés.
 */
export const genererBlocPdfTest = async (payload) => {
  const response = await api.post('/billing/invoices/generate-test-block/', payload)
  return response.data
}

/** Télécharge le PDF source produit par le générateur de blocs de test. */
export const telechargerBlocPdfTest = async (jobId, filename = 'bloc_factures_test.pdf') => {
  const response = await api.get(`/billing/invoices/test-blocks/${jobId}/download/`, {
    responseType: 'blob',
  })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
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
  try {
    const response = await api.get('/billing/stats/admin/')
    const data = response.data
    const global = data.statistiques_globales || {}
    const normalized = {
      ...data,
      totalContrats: global.total_entreprises || 0,
      totalLignesActives: global.total_lignes || 0,
      totalUtilisateursActifs: (data.stats_agents?.agents_actifs || 0) + (data.stats_utilisateurs?.total_payeurs || 0) + (data.stats_utilisateurs?.total_employes || 0),
      facturationMensuelle: data.evolution_mensuelle || [],
      historiquePublications: [],
      dernieresConnexions: [],
    }
    return isDashboardDemo() ? { ...normalized, ...DEMO_ADMIN_STATS, _demo: true } : normalized
  } catch (error) {
    if (isDashboardDemo()) return { ...DEMO_ADMIN_STATS, _demo: true }
    throw error
  }
}

/**
 * Récupère les statistiques payeur
 * Endpoint: GET /api/billing/stats/payeur/
 */
export const getStatsPayeur = async () => {
  try {
    const response = await api.get('/billing/stats/payeur/')
    const data = response.data
    const stats = data.statistiques || {}
    const contrat = data.contrat || null
    const normalized = {
      ...data,
      numeroContrat: contrat?.compte || null,
      raisonSociale: contrat?.raison_sociale || null,
      categorieClient: contrat?.categorie || null,
      nombreEntreprises: contrat?.nombre_entreprises || 0,
      nombreLignesActives: stats.nombre_lignes_actives || 0,
      nombreLignesTotal: stats.nombre_lignes || 0,
      lignesDetail: (data.lignes_a_surveiller || []).map(ligne => ({
        msisdn: ligne.msisdn,
        utilisateur: ligne.utilisateur || '—',
        forfait: ligne.cycle || '—',
        montant: ligne.montant_facture || 0,
        statut: 'ACTIF',
      })),
      lignesASurveiller: [],
      dernieresSimulations: [],
    }
    return isDashboardDemo() ? { ...normalized, ...DEMO_PAYEUR_STATS, _demo: true } : normalized
  } catch (error) {
    if (isDashboardDemo()) return { ...DEMO_PAYEUR_STATS, _demo: true }
    throw error
  }
}

/**
 * Récupère les statistiques employé
 * Endpoint: GET /api/billing/stats/employe/
 */
export const getStatsEmploye = async () => {
  try {
    const response = await api.get('/billing/stats/employe/')
    const data = response.data
    const normalized = {
      ...data,
      dernieresSimulations: (data.simulations?.dernieres || []).map(simulation => ({
        date: simulation.date_simulation, montant: simulation.montant_estime
      }))
    }
    return isDashboardDemo() ? { ...normalized, ...DEMO_EMPLOYE_STATS, _demo: true } : normalized
  } catch (error) {
    if (isDashboardDemo()) return { ...DEMO_EMPLOYE_STATS, _demo: true }
    throw error
  }
}

/**
 * Récupère les statistiques de l'agent de facturation connecté.
 * Endpoint: GET /api/billing/stats/agent/
 */
export const getStatsAgentFacturation = async () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isChef = user.role === 'CHEF_FACTURATION'
  try {
    const response = await api.get(isChef ? '/billing/stats/chef/' : '/billing/stats/agent/')
    let normalized
    if (isChef) {
      const performance = response.data.performance_equipe || {}
      normalized = {
        ...response.data,
        facturesNonPubliees: 0,
        erreursDecoupage: 0,
        lignesSansForfait: 0,
        servicesActifs: [],
        historiquePublications: (response.data.dernieres_publications || []).map(publication => ({
          date: publication.date_publication ? new Date(publication.date_publication).toLocaleDateString('fr-FR') : '-',
          periode: `${publication.periode_debut || '—'} - ${publication.periode_fin || '—'}`,
          nbFactures: publication.nombre_lignes_traitees || 0,
          statut: publication.statut || 'VALIDEE',
        })),
        statistiques: {
          total_publications: performance.total_publications || 0,
          montant_total: performance.montant_total || 0,
          lignes_traitees: 0,
        },
        evolution_quotidienne: response.data.publications_periode || [],
        dernieres_publications: response.data.dernieres_publications || [],
      }
    } else {
      const data = response.data
      normalized = {
        ...data,
        facturesNonPubliees: 0,
        erreursDecoupage: 0,
        lignesSansForfait: 0,
        servicesActifs: [],
        historiquePublications: (data.dernieres_publications || []).map(publication => ({ date: publication.date_publication ? new Date(publication.date_publication).toLocaleDateString('fr-FR') : '-', periode: `${publication.periode_debut || ''} - ${publication.periode_fin || ''}`, nbFactures: publication.nombre_lignes_traitees || 0, statut: publication.statut || 'VALIDEE' })),
      }
    }
    return isDashboardDemo() ? { ...normalized, ...DEMO_AGENT_STATS, _demo: true } : normalized
  } catch (error) {
    if (isDashboardDemo()) return { ...DEMO_AGENT_STATS, _demo: true }
    throw error
  }
}
