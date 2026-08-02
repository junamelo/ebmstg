import api from './api'

/**
 * Service pour la gestion des services et tarifs
 */

// ============ SERVICES ============

export const getServices = async () => {
  const response = await api.get('/billing/services/')
  return response.data
}

export const creerService = async (serviceData) => {
  const response = await api.post('/billing/services/', serviceData)
  return response.data
}

export const updateService = async (id, serviceData) => {
  const response = await api.put(`/billing/services/${id}/`, serviceData)
  return response.data
}

export const deleteService = async (id) => {
  await api.delete(`/billing/services/${id}/`)
}

export const toggleService = async (id) => {
  const response = await api.post(`/billing/services/${id}/toggle_actif/`)
  return response.data
}

// ============ TARIFS ============

export const getTarifs = async (serviceId = null) => {
  const params = serviceId ? { service: serviceId } : {}
  const response = await api.get('/billing/tarifs/', { params })
  return response.data
}

export const getTarifsActifs = async () => {
  const response = await api.get('/billing/tarifs/', { params: { actif_only: true } })
  return response.data
}

export const creerTarifService = async (tarifData) => {
  const response = await api.post('/billing/tarifs/', tarifData)
  return response.data
}

export const updateTarif = async (id, tarifData) => {
  const response = await api.put(`/billing/tarifs/${id}/`, tarifData)
  return response.data
}

export const deleteTarif = async (id) => {
  await api.delete(`/billing/tarifs/${id}/`)
}

export const toggleTarifService = async (id) => {
  const response = await api.post(`/billing/tarifs/${id}/toggle_actif/`)
  return response.data
}

