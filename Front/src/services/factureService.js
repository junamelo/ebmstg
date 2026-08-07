import api from './api'

const API_ORIGIN = 'http://localhost:8000'

const formatDate = (date) => date ? new Date(date).toLocaleDateString('fr-FR') : ''

const adapterFacture = (facture) => ({
  ...facture,
  numero: facture.numero_facture_pdf || facture.numero_facture,
  periode: facture.periode_debut?.slice(0, 7),
  type: facture.line ? 'SOMMAIRE' : 'GLOBALE',
  ligneOuFlotte: facture.line_msisdn || facture.company_name,
  montantTTC: Number(facture.montant_ttc),
  dateEmission: formatDate(facture.date_emission_pdf || facture.date_emission),
  dateEcheance: formatDate(facture.date_echeance),
  // L'URL n'est jamais appelée directement : elle indique seulement que le
  // PDF est disponible via l'endpoint authentifié.
  pdfUrl: (facture.has_pdf ?? Boolean(facture.fichier_pdf))
    ? `${API_ORIGIN}/api/billing/invoices/${facture.id}/pdf/`
    : null,
})

export const getFactures = async (filtres = {}) => {
  const params = new URLSearchParams()
  if (filtres.periode) params.append('periode', filtres.periode)
  if (filtres.type) params.append('type', filtres.type)
  if (filtres.statut) params.append('statut', filtres.statut)
  const response = await api.get(`/billing/invoices/?${params.toString()}`)
  const factures = response.data.results || response.data
  return factures.map(adapterFacture)
}

export const getFactureById = async (id) => {
  const response = await api.get(`/billing/invoices/${id}/`)
  return adapterFacture(response.data)
}

const base64VersBlobPdf = (contenuBase64) => {
  const caracteres = window.atob(contenuBase64)
  const octets = new Uint8Array(caracteres.length)
  for (let index = 0; index < caracteres.length; index += 1) {
    octets[index] = caracteres.charCodeAt(index)
  }
  return new Blob([octets], { type: 'application/pdf' })
}

/**
 * Passe par JSON afin que les extensions de gestion de téléchargement, comme
 * IDM, ne puissent pas intercepter une réponse application/pdf avant Axios.
 */
const recupererBlobPdf = async (id) => {
  const response = await api.get(`/billing/invoices/${id}/pdf-preview/`)
  return {
    blob: base64VersBlobPdf(response.data.content_base64),
    filename: response.data.filename,
  }
}

const afficherErreurPdf = (error, numeroFacture, action) => {
  if (error.response?.status === 404) {
    alert(`Aucun PDF disponible pour la facture ${numeroFacture}.`)
  } else if (error.response?.status === 403) {
    alert(`Accès refusé au PDF de la facture ${numeroFacture}.`)
  } else {
    alert(`Impossible de ${action} la facture ${numeroFacture}. Veuillez réessayer.`)
  }
  console.error(`Erreur PDF (${action}) :`, error)
}

export const telechargerFacture = async (id, numeroFacture) => {
  try {
    const { blob, filename } = await recupererBlobPdf(id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename || `facture_${numeroFacture}.pdf`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.setTimeout(() => window.URL.revokeObjectURL(url), 1_000)
  } catch (error) {
    afficherErreurPdf(error, numeroFacture, 'télécharger')
  }
}

export const ouvrirApercuFacture = async (id, numeroFacture) => {
  const apercu = window.open('', '_blank')
  if (!apercu) {
    alert("L'aperçu a été bloqué par le navigateur. Autorisez les fenêtres pop-up puis réessayez.")
    return
  }

  try {
    apercu.document.title = `Chargement facture ${numeroFacture}`
    apercu.document.body.innerHTML = '<p style="font-family:Arial;padding:24px">Chargement du PDF…</p>'
    const { blob } = await recupererBlobPdf(id)
    const blobUrl = window.URL.createObjectURL(blob)
    apercu.location.replace(blobUrl)
    window.setTimeout(() => window.URL.revokeObjectURL(blobUrl), 60_000)
  } catch (error) {
    apercu.close()
    afficherErreurPdf(error, numeroFacture, 'ouvrir')
  }
}
