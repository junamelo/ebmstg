import api from './api'
import {
  mockGetStatistiques,
  mockGetStatsPayeur,
  mockGetStatsEmploye,
  mockGetStatsAgentFacturation,
  mockGetTarifs,
  mockCreerTarif,
  mockDesactiverTarif,
  mockActiverTarif,
  mockGetUtilisateurs,
  mockActiverCompte,
  mockSuspendreCompte,
  mockResetMdp,
  mockUploadBlocPdf,
  mockGetHistoriquePublications,
} from './mockApi'

// ⚠️ Mettre à false quand le backend .NET sera prêt
const USE_MOCK = true

// ─── PUBLICATION PDF ─────────────────────────────────────────
export const uploadBlocPdf = async (fichier, type, periode, onProgress) => {
  if (USE_MOCK) return mockUploadBlocPdf(fichier, type, periode, onProgress)
  const formData = new FormData()
  formData.append('fichier', fichier)
  formData.append('type', type)
  formData.append('periode', periode)
  const response = await api.post('/admin/pdf/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) onProgress(Math.round((e.loaded * 100) / e.total))
    },
  })
  return response.data
}

export const getHistoriquePublications = async () => {
  if (USE_MOCK) return mockGetHistoriquePublications()
  const response = await api.get('/admin/pdf/historique')
  return response.data
}

// ─── TARIFS ──────────────────────────────────────────────────
export const getTarifs = async () => {
  if (USE_MOCK) return mockGetTarifs()
  const response = await api.get('/tarifs')
  return response.data
}

export const creerTarif = async (tarif) => {
  if (USE_MOCK) return mockCreerTarif(tarif)
  const response = await api.post('/tarifs', tarif)
  return response.data
}

export const modifierTarif = async (id, tarif) => {
  const response = await api.put(`/tarifs/${id}`, tarif)
  return response.data
}

export const desactiverTarif = async (id) => {
  if (USE_MOCK) return mockDesactiverTarif(id)
  const response = await api.patch(`/tarifs/${id}/desactiver`)
  return response.data
}

export const activerTarif = async (id) => {
  if (USE_MOCK) return mockActiverTarif(id)
  const response = await api.patch(`/tarifs/${id}/activer`)
  return response.data
}

// ─── COMPTES ─────────────────────────────────────────────────
export const getUtilisateurs = async (filtres = {}) => {
  if (USE_MOCK) return mockGetUtilisateurs()
  const params = new URLSearchParams(filtres)
  const response = await api.get(`/admin/utilisateurs?${params.toString()}`)
  return response.data
}

export const activerCompte = async (id) => {
  if (USE_MOCK) return mockActiverCompte(id)
  const response = await api.patch(`/admin/utilisateurs/${id}/activer`)
  return response.data
}

export const suspendreCompte = async (id) => {
  if (USE_MOCK) return mockSuspendreCompte(id)
  const response = await api.patch(`/admin/utilisateurs/${id}/suspendre`)
  return response.data
}

export const reinitialiserMotDePasseAdmin = async (id) => {
  if (USE_MOCK) return mockResetMdp(id)
  const response = await api.post(`/admin/utilisateurs/${id}/reset-password`)
  return response.data
}

// ─── STATISTIQUES ────────────────────────────────────────────
export const getStatistiques = async () => {
  if (USE_MOCK) return mockGetStatistiques()
  const response = await api.get('/admin/statistiques')
  return response.data
}

export const getStatsPayeur = async () => {
  if (USE_MOCK) return mockGetStatsPayeur()
  const response = await api.get('/payeur/statistiques')
  return response.data
}

export const getStatsEmploye = async () => {
  if (USE_MOCK) return mockGetStatsEmploye()
  const response = await api.get('/employe/statistiques')
  return response.data
}

export const getStatsAgentFacturation = async () => {
  if (USE_MOCK) return mockGetStatsAgentFacturation()
  const response = await api.get('/agent-facturation/statistiques')
  return response.data
}
