// ============================================================
//  DEVICE SERVICE — Détection et tracking du type d'appareil
// ============================================================

/**
 * Détecte le type d'appareil à partir du User-Agent
 * @returns {'MOBILE' | 'TABLET' | 'DESKTOP'}
 */
export function detecterAppareil() {
  const ua = navigator.userAgent

  if (/iPad|Android(?!.*Mobile)|Tablet/i.test(ua)) return 'TABLET'
  if (/Android|iPhone|iPod|BlackBerry|IEMobile|Opera Mini|Mobile/i.test(ua)) return 'MOBILE'
  return 'DESKTOP'
}

/**
 * Détecte le navigateur
 */
export function detecterNavigateur() {
  const ua = navigator.userAgent
  if (ua.includes('Chrome') && !ua.includes('Edg')) return 'Chrome'
  if (ua.includes('Firefox')) return 'Firefox'
  if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Safari'
  if (ua.includes('Edg')) return 'Edge'
  return 'Autre'
}

/**
 * Enregistre une visite dans le localStorage (simulation backend)
 */
export function enregistrerVisite(userId, role) {
  const visite = {
    userId,
    role,
    appareil: detecterAppareil(),
    navigateur: detecterNavigateur(),
    date: new Date().toISOString(),
    timestamp: Date.now(),
  }

  const historique = JSON.parse(localStorage.getItem('visites_historique') || '[]')
  historique.unshift(visite)
  // Garder seulement les 500 dernières visites
  localStorage.setItem('visites_historique', JSON.stringify(historique.slice(0, 500)))
}

/**
 * Récupère les statistiques d'appareils depuis le localStorage
 */
export function getStatsAppareils() {
  const historique = JSON.parse(localStorage.getItem('visites_historique') || '[]')

  // Données de base si pas encore de visites réelles
  const defaults = { MOBILE: 38, TABLET: 12, DESKTOP: 50 }

  if (historique.length === 0) return {
    repartition: defaults,
    total: 100,
    historique: [],
  }

  const repartition = { MOBILE: 0, TABLET: 0, DESKTOP: 0 }
  historique.forEach(v => {
    if (repartition[v.appareil] !== undefined) repartition[v.appareil]++
  })

  // Stats des 30 derniers jours par jour
  const parJour = {}
  const maintenant = Date.now()
  const trente_jours = 30 * 24 * 60 * 60 * 1000

  historique
    .filter(v => maintenant - v.timestamp < trente_jours)
    .forEach(v => {
      const date = new Date(v.date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })
      if (!parJour[date]) parJour[date] = { MOBILE: 0, TABLET: 0, DESKTOP: 0 }
      parJour[date][v.appareil]++
    })

  return {
    repartition,
    total: historique.length,
    historique: Object.entries(parJour).map(([date, counts]) => ({ date, ...counts })),
  }
}
