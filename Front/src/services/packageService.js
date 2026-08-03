import api from './api'

/**
 * Service pour la gestion des forfaits (packages)
 */

export const getPackages = async (params = {}) => {
  const response = await api.get('/billing/packages/', { params })
  return response.data.results || response.data
}

export const getPackage = async (id) => {
  const response = await api.get(`/billing/packages/${id}/`)
  return response.data
}

export const createPackage = async (data) => {
  const response = await api.post('/billing/packages/', data)
  return response.data
}

export const updatePackage = async (id, data) => {
  const response = await api.put(`/billing/packages/${id}/`, data)
  return response.data
}

export const togglePackageActif = async (id) => {
  const response = await api.post(`/billing/packages/${id}/toggle_actif/`)
  return response.data
}

export const deletePackage = async (id) => {
  const response = await api.delete(`/billing/packages/${id}/`)
  return response.data
}
