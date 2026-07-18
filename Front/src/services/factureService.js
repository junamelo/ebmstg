import api from './api'
import { mockGetFactures, mockGetFactureById } from './mockApi'
import { MOCK_FACTURES } from './mockData'

// ⚠️ Mettre à false quand le backend .NET sera prêt
const USE_MOCK = true

const getUserFromStorage = () => {
  try { return JSON.parse(localStorage.getItem('user')) } catch { return null }
}

export const getFactures = async (filtres = {}) => {
  if (USE_MOCK) {
    const user = getUserFromStorage()
    return mockGetFactures(user, filtres)
  }
  const params = new URLSearchParams()
  if (filtres.periode) params.append('periode', filtres.periode)
  if (filtres.type) params.append('type', filtres.type)
  if (filtres.statut) params.append('statut', filtres.statut)
  const response = await api.get(`/factures?${params.toString()}`)
  return response.data
}

export const getFactureById = async (id) => {
  if (USE_MOCK) {
    return MOCK_FACTURES.find(f => f.id === id) || null
  }
  const response = await api.get(`/factures/${id}`)
  return response.data
}

export const getFacturePdfUrl = (id) => {
  if (USE_MOCK) return '/mock-facture.pdf'
  const token = localStorage.getItem('token')
  return `/api/factures/${id}/pdf?token=${token}`
}

export const telechargerFacture = async (id, numeroFacture) => {
  if (USE_MOCK) {
    alert(`[MOCK] Téléchargement de la facture ${numeroFacture} — sera disponible avec le backend .NET`)
    return
  }
  const response = await api.get(`/factures/${id}/pdf`, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `facture_${numeroFacture}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
