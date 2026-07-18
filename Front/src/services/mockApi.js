// ============================================================
//  MOCK API — Simule le backend .NET avec un délai réseau
//  Remplace temporairement tous les appels Axios
// ============================================================
import {
  MOCK_USERS,
  MOCK_TARIFS,
  MOCK_FACTURES,
  MOCK_COMPTES,
  MOCK_PUBLICATIONS,
  MOCK_STATS_ADMIN,
  MOCK_STATS_PAYEUR,
  MOCK_STATS_EMPLOYE,
  MOCK_SERVICES,
} from './mockData'

// Simule un délai réseau réaliste (300-600ms)
const delay = (ms = 400) => new Promise(resolve => setTimeout(resolve, ms))

// ─── AUTH ─────────────────────────────────────────────────────
export const mockLogin = async (login, motDePasse, _typeLogin) => {
  await delay()
  const loginNorm = login?.trim()
  const mdpNorm   = motDePasse?.trim()
  const user = MOCK_USERS.find(
    u => u.login === loginNorm && u.motDePasse === mdpNorm
  )
  if (!user) throw { response: { data: { message: 'Identifiant ou mot de passe incorrect.' } } }
  if (!user.estActif) throw { response: { data: { message: 'Compte suspendu. Contactez votre administrateur.' } } }
  return {
    token: `mock-token-${user.id}-${Date.now()}`,
    user: {
      id: user.id,
      nom: user.nom,
      prenom: user.prenom,
      email: user.email,
      role: user.role,
      raisonSociale: user.raisonSociale,
      numeroContrat: user.numeroContrat,
      numeroLigne: user.numeroLigne,
    },
  }
}

export const mockDemanderReinitialisationMdp = async (email) => {
  await delay(600)
  return { message: 'Email envoyé.' }
}

// ─── FACTURES ─────────────────────────────────────────────────
export const mockGetFactures = async (user, filtres = {}) => {
  await delay()
  let factures = []

  if (user.role === 'EMPLOYE') {
    // L'employé voit seulement ses factures sommaires
    factures = MOCK_FACTURES.filter(f => f.type === 'SOMMAIRE' && f.lineId === user.id)
  } else if (user.role === 'PAYEUR') {
    // Le payeur voit globales + toutes sommaires de son entreprise
    factures = MOCK_FACTURES.filter(f => f.companyId === user.id)
  } else {
    factures = MOCK_FACTURES
  }

  // Filtres
  if (filtres.periode) factures = factures.filter(f => f.periode === filtres.periode)
  if (filtres.type) factures = factures.filter(f => f.type === filtres.type)
  if (filtres.statut) factures = factures.filter(f => f.statut === filtres.statut)

  return factures
}

export const mockGetFactureById = async (id) => {
  await delay(300)
  return MOCK_FACTURES.find(f => f.id === id) || null
}

// ─── SIMULATION ───────────────────────────────────────────────
export const mockGetTarifsActifs = async () => {
  await delay(300)
  return MOCK_TARIFS.find(t => t.estActif)
}

export const mockSimuler = async (donnees) => {
  await delay(600)
  const tarif = MOCK_TARIFS.find(t => t.estActif)
  const montantAppels = (donnees.minutesAppel || 0) * tarif.prixParMinute
  const montantSms    = (donnees.nombreSms || 0) * tarif.prixParSms
  const montantData   = (donnees.volumeDataGo || 0) * tarif.prixParGo
  const montantTotal  = montantAppels + montantSms + montantData
  return { montantAppels, montantSms, montantData, montantTotal }
}

// ─── ADMIN ────────────────────────────────────────────────────
export const mockGetStatistiques = async () => {
  await delay(400)
  return MOCK_STATS_ADMIN
}

export const mockGetStatsPayeur = async () => {
  await delay(400)
  return MOCK_STATS_PAYEUR
}

export const mockGetStatsEmploye = async () => {
  await delay(400)
  return MOCK_STATS_EMPLOYE
}

export const mockGetStatsAgentFacturation = async () => {
  await delay(400)
  return {
    statutPublication: 'TRAITEE',
    nbFacturesGenerees: 1247,
    datePublication: '05/07/2026',
    facturesNonPubliees: 0,
    erreursDecoupage: 2,
    lignesSansForfait: 5,
    servicesActifs: [
      { nom: 'No Limit AI50', tarif: 5000, nbLignes: 342 },
      { nom: 'BlackBerry BB15_6', tarif: 3500, nbLignes: 128 },
      { nom: 'Incognito', tarif: 1000, nbLignes: 89 },
      { nom: 'Forfait Standard', tarif: 15000, nbLignes: 658 },
    ],
    historiquePublications: [
      { date: '05/07/2026', periode: 'Juin 2026', nbFactures: 1247, statut: 'TRAITEE' },
      { date: '03/06/2026', periode: 'Mai 2026', nbFactures: 1238, statut: 'TRAITEE' },
      { date: '05/05/2026', periode: 'Avril 2026', nbFactures: 1251, statut: 'TRAITEE' },
      { date: '02/04/2026', periode: 'Mars 2026', nbFactures: 1242, statut: 'TRAITEE' },
    ],
  }
}

export const mockGetTarifs = async () => {
  await delay()
  return MOCK_TARIFS
}

export const mockCreerTarif = async (tarif) => {
  await delay(500)
  const nouveau = { id: String(Date.now()), ...tarif, dateApplication: new Date().toLocaleDateString('fr-FR'), estActif: true }
  MOCK_TARIFS.forEach(t => t.estActif = false)
  MOCK_TARIFS.unshift(nouveau)
  return nouveau
}

export const mockDesactiverTarif = async (id) => {
  await delay()
  const tarif = MOCK_TARIFS.find(t => t.id === id)
  if (tarif) tarif.estActif = false
  return tarif
}

export const mockActiverTarif = async (id) => {
  await delay()
  const tarif = MOCK_TARIFS.find(t => t.id === id)
  if (tarif) {
    MOCK_TARIFS.forEach(t => t.estActif = false)
    tarif.estActif = true
  }
  return tarif
}

export const mockGetUtilisateurs = async () => {
  await delay()
  return MOCK_COMPTES
}

export const mockActiverCompte = async (id) => {
  await delay()
  const compte = MOCK_COMPTES.find(c => c.id === id)
  if (compte) compte.estActif = true
  return compte
}

export const mockSuspendreCompte = async (id) => {
  await delay()
  const compte = MOCK_COMPTES.find(c => c.id === id)
  if (compte) compte.estActif = false
  return compte
}

export const mockResetMdp = async (id) => {
  await delay(500)
  return { message: 'Mot de passe réinitialisé.' }
}

export const mockUploadBlocPdf = async (fichier, type, periode, onProgress) => {
  // Simule une progression d'upload
  for (let i = 10; i <= 100; i += 10) {
    await delay(200)
    if (onProgress) onProgress(i)
  }
  const nbFactures = type === 'GLOBALE' ? 1247 : 23418
  const publication = {
    id: String(Date.now()),
    datePublication: new Date().toLocaleDateString('fr-FR'),
    type,
    periode,
    nomFichier: fichier.name,
    facturesCreees: nbFactures,
    statut: 'SUCCES',
  }
  MOCK_PUBLICATIONS.unshift(publication)
  return { facturesCreees: nbFactures, pages: type === 'GLOBALE' ? 1500 : 23000 }
}

export const mockGetHistoriquePublications = async () => {
  await delay()
  return MOCK_PUBLICATIONS
}

// ─── SERVICES ─────────────────────────────────────────────────
export const mockGetServices = async () => {
  await delay(300)
  return MOCK_SERVICES
}

export const mockCreerService = async ({ nom, description }) => {
  await delay(500)
  const nouveau = { id: `srv-${Date.now()}`, nom, description, actif: true, nbLignes: 0, options: [] }
  MOCK_SERVICES.unshift(nouveau)
  return nouveau
}

export const mockToggleService = async (id) => {
  await delay(300)
  const srv = MOCK_SERVICES.find(s => s.id === id)
  if (srv) srv.actif = !srv.actif
  return srv
}

export const mockAjouterOption = async (serviceId, { nom, tarif }) => {
  await delay(400)
  const srv = MOCK_SERVICES.find(s => s.id === serviceId)
  if (!srv) throw new Error('Service introuvable')
  const option = { id: `opt-${Date.now()}`, nom, tarif: parseFloat(tarif), actif: true }
  srv.options.push(option)
  return option
}

export const mockToggleOption = async (serviceId, optionId) => {
  await delay(300)
  const srv = MOCK_SERVICES.find(s => s.id === serviceId)
  if (!srv) throw new Error('Service introuvable')
  const opt = srv.options.find(o => o.id === optionId)
  if (opt) opt.actif = !opt.actif
  return opt
}

export const mockCreerUtilisateur = async (form) => {
  await delay(500)
  const nouveau = {
    id: String(Date.now()),
    nom: form.nom,
    prenom: form.prenom,
    email: form.email || '',
    role: form.role,
    login: form.login,
    motDePasse: form.motDePasse,
    estActif: true,
    raisonSociale: form.raisonSociale || null,
    numeroContrat: form.role === 'PAYEUR' ? form.login : null,
    numeroLigne: form.role === 'EMPLOYE' ? form.login : null,
  }
  MOCK_USERS.push(nouveau)
  MOCK_COMPTES.push({
    id: nouveau.id,
    nom: nouveau.nom,
    prenom: nouveau.prenom,
    login: nouveau.login,
    role: nouveau.role,
    raisonSociale: nouveau.raisonSociale,
    estActif: true,
  })
  return nouveau
}
