/**
 * Service de calcul des tarifs selon les paliers définis
 * Basé sur l'email de tarification reçu
 */

// Paliers de tarification DATA
const PALIERS_DATA = [
  { volumeMin: 0, volumeMax: 1, tarif: 0 },                    // 0-1 Go : Gratuit
  { volumeMin: 1, volumeMax: 7, tarif: 4500 },                 // 1-7 Go
  { volumeMin: 7, volumeMax: 15, tarif: 5000 },                // 7-15 Go
  { volumeMin: 15, volumeMax: 35, tarif: 9000 },               // 15-35 Go
  { volumeMin: 35, volumeMax: 85, tarif: 15000 },              // 35-85 Go
  { volumeMin: 85, volumeMax: 275, tarif: 50000 },             // 85-275 Go
  { volumeMin: 275, volumeMax: null, tarifParMo: 5, fixe: 50000 } // > 275 Go : 5F/Mo + 50000F
]

// Tarif VOIX
const TARIF_VOIX = {
  prixParMinute: 79,      // 79 F/min
  pasFacturation: 30       // Pas de 30 secondes
}

// Tarif SMS
const TARIF_SMS = {
  prixParSms: 30          // 30 F/unité
}

/**
 * Calcule le montant DATA selon les paliers
 * @param {number} volumeGo - Volume en Go
 * @returns {number} Montant en FCFA
 */
export function calculerMontantData(volumeGo) {
  if (volumeGo <= 0) return 0
  
  // Trouver le palier correspondant
  for (const palier of PALIERS_DATA) {
    if (palier.volumeMax === null) {
      // Palier > 275 Go : calcul spécial
      if (volumeGo > palier.volumeMin) {
        const volumeMo = volumeGo * 1000 // Convertir en Mo
        const depassementMo = volumeMo - (palier.volumeMin * 1000)
        return (depassementMo * palier.tarifParMo) + palier.fixe
      }
    } else {
      // Palier standard
      if (volumeGo > palier.volumeMin && volumeGo <= palier.volumeMax) {
        return palier.tarif
      }
    }
  }
  
  return 0
}

/**
 * Calcule le montant VOIX selon le pas de facturation
 * @param {number} dureeSecondes - Durée totale en secondes
 * @returns {number} Montant en FCFA
 */
export function calculerMontantVoix(dureeSecondes) {
  if (dureeSecondes <= 0) return 0
  
  const { prixParMinute, pasFacturation } = TARIF_VOIX
  
  // Calcul par pas de 30 secondes
  // 0-30s : demi-tarif (79/2)
  // 31-60s : tarif complet (79)
  // Etc.
  
  let montantTotal = 0
  let tempsRestant = dureeSecondes
  
  while (tempsRestant > 0) {
    if (tempsRestant <= pasFacturation) {
      // Première tranche ou dernière tranche <= 30s
      montantTotal += prixParMinute / 2
      tempsRestant = 0
    } else {
      // Tranche complète de 30s
      montantTotal += prixParMinute / 2
      tempsRestant -= pasFacturation
    }
  }
  
  return montantTotal
}

/**
 * Calcule le montant VOIX à partir de minutes
 * @param {number} minutes - Durée en minutes
 * @returns {number} Montant en FCFA
 */
export function calculerMontantVoixMinutes(minutes) {
  const dureeSecondes = minutes * 60
  return calculerMontantVoix(dureeSecondes)
}

/**
 * Calcule le montant SMS
 * @param {number} nombreSms - Nombre de SMS
 * @returns {number} Montant en FCFA
 */
export function calculerMontantSms(nombreSms) {
  if (nombreSms <= 0) return 0
  return nombreSms * TARIF_SMS.prixParSms
}

/**
 * Détaille le calcul DATA avec informations du palier
 * @param {number} volumeGo - Volume en Go
 * @returns {object} { montant, palier, details }
 */
export function detaillerCalculData(volumeGo) {
  if (volumeGo <= 0) {
    return { montant: 0, palier: null, details: 'Aucune consommation' }
  }
  
  for (const palier of PALIERS_DATA) {
    if (palier.volumeMax === null) {
      if (volumeGo > palier.volumeMin) {
        const volumeMo = volumeGo * 1000
        const depassementMo = volumeMo - (palier.volumeMin * 1000)
        const montant = (depassementMo * palier.tarifParMo) + palier.fixe
        
        return {
          montant,
          palier: `Plus de ${palier.volumeMin} Go`,
          details: `${volumeGo.toFixed(2)} Go = ${volumeMo.toFixed(0)} Mo\nDépassement: ${depassementMo.toFixed(0)} Mo × ${palier.tarifParMo} F/Mo + ${palier.fixe.toLocaleString()} F fixe`,
          formule: `(${depassementMo.toFixed(0)} × ${palier.tarifParMo}) + ${palier.fixe.toLocaleString()} = ${montant.toLocaleString()} F`
        }
      }
    } else {
      if (volumeGo > palier.volumeMin && volumeGo <= palier.volumeMax) {
        return {
          montant: palier.tarif,
          palier: `${palier.volumeMin} - ${palier.volumeMax} Go`,
          details: `Volume: ${volumeGo.toFixed(2)} Go\nPalier: ${palier.volumeMin} - ${palier.volumeMax} Go`,
          formule: `Tarif forfaitaire = ${palier.tarif.toLocaleString()} F`
        }
      }
    }
  }
  
  return { montant: 0, palier: null, details: 'Erreur de calcul' }
}

/**
 * Détaille le calcul VOIX
 * @param {number} dureeSecondes - Durée en secondes
 * @returns {object} { montant, details }
 */
export function detaillerCalculVoix(dureeSecondes) {
  if (dureeSecondes <= 0) {
    return { montant: 0, details: 'Aucune consommation' }
  }
  
  const montant = calculerMontantVoix(dureeSecondes)
  const minutes = Math.floor(dureeSecondes / 60)
  const secondes = dureeSecondes % 60
  
  let explication = `Durée: ${minutes}min ${secondes}s\n`
  explication += `Tarif: ${TARIF_VOIX.prixParMinute} F/min\n`
  explication += `Pas de facturation: ${TARIF_VOIX.pasFacturation}s (demi-tarif par tranche)`
  
  return {
    montant,
    details: explication,
    formule: `${montant.toLocaleString()} F`
  }
}

/**
 * Obtient les paliers DATA (pour affichage)
 * @returns {Array} Liste des paliers
 */
export function getPaliersData() {
  return PALIERS_DATA
}

/**
 * Obtient les tarifs VOIX et SMS
 * @returns {object} { voix, sms }
 */
export function getTarifsVoixSms() {
  return {
    voix: TARIF_VOIX,
    sms: TARIF_SMS
  }
}
