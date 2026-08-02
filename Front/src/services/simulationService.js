import api from './api'
import { calculerMontantData, calculerMontantVoixMinutes, calculerMontantSms } from './tarifsService'

/**
 * Récupère les tarifs actifs depuis l'API Django
 * Endpoint: GET /api/billing/tarifs/?is_active=true
 */
export const getTarifsActifs = async () => {
  const response = await api.get('/billing/tarifs/', { params: { is_active: true } })
  const tarifs = response.data.results || response.data
  // Retourner le premier tarif actif trouvé (ou null)
  return tarifs.length > 0 ? tarifs[0] : null
}

/**
 * Simule une facturation avec calcul local des tarifs
 * Note: pas d'endpoint backend pour la simulation, calcul côté client
 */
export const simulerFacturation = async (donnees) => {
  // Calculs locaux avec tarifsService
  const montantAppels = calculerMontantVoixMinutes(donnees.minutesAppel || 0)
  const montantSms = calculerMontantSms(donnees.nombreSms || 0)
  const montantData = calculerMontantData(donnees.volumeDataGo || 0)
  const montantTotal = montantAppels + montantSms + montantData
  
  return {
    montantAppels,
    montantSms,
    montantData,
    montantTotal
  }
}

/**
 * Récupère l'historique des simulations de l'utilisateur connecté
 * Utilise les stats employé pour afficher la consommation
 * Endpoint: GET /api/billing/stats/employe/
 */
export const getHistoriqueSimulations = async () => {
  try {
    const response = await api.get('/billing/stats/employe/')
    // Retourner un tableau vide si pas de stats, sinon formater les données
    return response.data?.simulations || []
  } catch (error) {
    console.warn('Historique simulations non disponible:', error)
    return []
  }
}
