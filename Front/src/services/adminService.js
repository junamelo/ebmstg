import api from './api'

// Backend Django prêt - Plus besoin des mocks

// ─── PUBLICATION PDF ─────────────────────────────────────────
/**
 * Upload d'un bloc PDF de factures
 * Endpoint: POST /api/billing/invoices/upload_bulk_pdf/
 */
export const uploadBlocPdf = async (fichier, cycle, periodeDebut, periodeFin, onProgress) => {
  const formData = new FormData()
  formData.append('fichier', fichier)
  formData.append('auto_match', 'true')
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
  return response.data
}

/**
 * Récupère les statistiques payeur
 * Endpoint: GET /api/billing/stats/payeur/
 */
export const getStatsPayeur = async () => {
  const response = await api.get('/billing/stats/payeur/')
  return response.data
}

/**
 * Récupère les statistiques employé
 * Endpoint: GET /api/billing/stats/employe/
 */
export const getStatsEmploye = async () => {
  const response = await api.get('/billing/stats/employe/')
  return response.data
}

/**
 * Récupère les statistiques chef/agent facturation
 * Endpoint: GET /api/billing/stats/chef/ ou /api/billing/stats/agent/
 */
export const getStatsAgentFacturation = async () => {
  try {
    // Essayer d'abord avec l'endpoint chef
    const response = await api.get('/billing/stats/chef/')
    return response.data
  } catch (error) {
    // Fallback sur agent si chef échoue
    const response = await api.get('/billing/stats/agent/')
    return response.data
  }
}
