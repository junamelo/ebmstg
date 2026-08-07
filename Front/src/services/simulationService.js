import api from './api'
import { calculerMontantData, calculerMontantVoixMinutes, calculerMontantSms } from './tarifsService'

/**
 * Récupère les tarifs actifs depuis l'API Django
 */
export const getTarifsActifs = async () => {
  const response = await api.get('/billing/tarifs/', { params: { is_active: true } })
  const tarifs = response.data.results || response.data
  return tarifs.length > 0 ? tarifs[0] : null
}

/**
 * Sauvegarde une simulation en base via l'API Django
 * Endpoint: POST /api/billing/simulations/
 */
export const sauvegarderSimulation = async ({ montantTotal, servicesChoisis, consommationPrevue, typeClient }) => {
  const resultatDetaille = {
    typeClient,
    consommationPrevue: consommationPrevue || null,
    servicesChoisis: servicesChoisis || [],
  }
  const response = await api.post('/billing/simulations/', {
    montant_estime: montantTotal,
    services_selectionnes: (servicesChoisis || []).map(s => ({ nom: s.nom, tarif: s.tarif })),
    resultat_detaille: resultatDetaille,
  })
  return response.data
}

/**
 * Récupère l'historique des simulations de l'utilisateur connecté
 * Endpoint: GET /api/billing/simulations/
 */
export const getHistoriqueSimulations = async () => {
  try {
    const response = await api.get('/billing/simulations/')
    return response.data.results || response.data
  } catch (error) {
    console.warn('Historique simulations non disponible:', error)
    return []
  }
}
