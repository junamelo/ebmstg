import api from './api'
import { mockGetTarifsActifs, mockSimuler } from './mockApi'

// ⚠️ Mettre à false quand le backend .NET sera prêt
const USE_MOCK = true

export const getTarifsActifs = async () => {
  if (USE_MOCK) return mockGetTarifsActifs()
  const response = await api.get('/tarifs/actifs')
  return response.data
}

export const simulerFacturation = async (donnees) => {
  if (USE_MOCK) return mockSimuler(donnees)
  const response = await api.post('/simulations', donnees)
  return response.data
}

export const getHistoriqueSimulations = async () => {
  if (USE_MOCK) return []
  const response = await api.get('/simulations/historique')
  return response.data
}
