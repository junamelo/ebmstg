import api from './api'

/**
 * Service pour la gestion des publications de factures
 */

// ============ PUBLICATIONS ============

export const getPublications = async (params = {}) => {
  const response = await api.get('/billing/publications/', { params })
  return response.data
}

export const getPublicationById = async (id) => {
  const response = await api.get(`/billing/publications/${id}/`)
  return response.data
}

// ============ FACTURES À PUBLIER ============

export const getFacturesAPublier = async (params = {}) => {
  const response = await api.get('/billing/invoices/factures_a_publier/', { params })
  return response.data
}

// ============ PUBLICATION EN MASSE ============

export const publierFacturesEnMasse = async (invoiceIds) => {
  const response = await api.post('/billing/invoices/publier_masse/', {
    invoice_ids: invoiceIds
  })
  return response.data
}

// ============ UPLOAD PDF ============

export const uploadBulkPdf = async (file, options = {}, onProgress = null) => {
  const formData = new FormData()
  formData.append('fichier', file)
  
  if (options.cycle) formData.append('cycle', options.cycle)
  if (options.periode_debut) formData.append('periode_debut', options.periode_debut)
  if (options.periode_fin) formData.append('periode_fin', options.periode_fin)
  if (options.auto_match !== undefined) formData.append('auto_match', options.auto_match)

  const config = {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }

  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      onProgress(percentCompleted)
    }
  }

  const response = await api.post('/billing/invoices/upload_bulk_pdf/', formData, config)
  return response.data
}
