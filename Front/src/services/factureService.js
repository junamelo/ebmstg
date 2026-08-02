import api from './api'
const API_ORIGIN = 'http://localhost:8000'

const formatDate = (date) => date ? new Date(date).toLocaleDateString('fr-FR') : ''

const adapterFacture = (facture) => ({
  ...facture,
  numero: facture.numero_facture,
  periode: facture.periode_debut?.slice(0, 7),
  type: facture.line ? 'SOMMAIRE' : 'GLOBALE',
  ligneOuFlotte: facture.line_msisdn || facture.company_name,
  montantTTC: Number(facture.montant_ttc),
  dateEmission: formatDate(facture.date_emission),
  dateEcheance: formatDate(facture.date_echeance),
  pdfUrl: facture.fichier_pdf
    ? (facture.fichier_pdf.startsWith('http') ? facture.fichier_pdf : `${API_ORIGIN}${facture.fichier_pdf}`)
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

export const getFacturePdfUrl = (id) => {
  return `${API_ORIGIN}/api/billing/invoices/${id}/`
}

export const telechargerFacture = async (id, numeroFacture) => {
  const facture = await getFactureById(id)
  if (!facture.pdfUrl) throw new Error(`Aucun PDF associé à la facture ${numeroFacture}`)
  const link = document.createElement('a')
  link.href = facture.pdfUrl
  link.setAttribute('download', `facture_${numeroFacture}.pdf`)
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  link.remove()
}
