/**
 * Données de présentation destinées aux captures d'écran.
 * Elles ne sont utilisées que lorsque l'URL contient ?demo=1.
 * Aucun enregistrement n'est ajouté à la base de données.
 */

export const isDashboardDemo = () => {
  if (typeof window === 'undefined') return false
  return new URLSearchParams(window.location.search).get('demo') === '1'
}

const publications = [
  { date: '05/08/2026', periode: '01/07/2026 - 31/07/2026', nbFactures: 128, nbFacturesTraitees: 128, statut: 'TRAITEE' },
  { date: '20/07/2026', periode: '01/06/2026 - 30/06/2026', nbFactures: 116, nbFacturesTraitees: 114, statut: 'TRAITEE' },
  { date: '05/07/2026', periode: '01/05/2026 - 31/05/2026', nbFactures: 103, nbFacturesTraitees: 101, statut: 'TRAITEE' },
  { date: '20/06/2026', periode: '01/04/2026 - 30/04/2026', nbFactures: 96, nbFacturesTraitees: 96, statut: 'TRAITEE' },
]

export const DEMO_ADMIN_STATS = {
  totalContrats: 24,
  totalLignesActives: 118,
  totalUtilisateursActifs: 156,
  evolutionContrats: 8.4,
  evolutionLignes: 5.7,
  evolutionUtilisateurs: 11.2,
  historiquePublications: [
    { mois: 'Mars', globales: 18, sommaires: 420 },
    { mois: 'Avril', globales: 22, sommaires: 510 },
    { mois: 'Mai', globales: 25, sommaires: 580 },
    { mois: 'Juin', globales: 28, sommaires: 640 },
    { mois: 'Juillet', globales: 31, sommaires: 710 },
    { mois: 'Août', globales: 34, sommaires: 780 },
  ],
  dernieresConnexions: [
    { nom: 'Afi Kossi', role: 'AGENT_FACTURATION', date: '12/08/2026 09:42', ip: '192.168.1.21' },
    { nom: 'Société Démo Africa', role: 'PAYEUR', date: '12/08/2026 09:18', ip: '192.168.1.34' },
    { nom: 'Benoît Banlepo', role: 'SUPER_ADMIN', date: '12/08/2026 08:56', ip: '192.168.1.10' },
  ],
}

export const DEMO_AGENT_STATS = {
  facturesNonPubliees: 12,
  erreursDecoupage: 2,
  lignesSansForfait: 4,
  servicesActifs: [
    { nom: 'Voix', tarif: 79, nbLignes: 64 },
    { nom: 'SMS', tarif: 30, nbLignes: 86 },
    { nom: 'Data Local', tarif: 5000, nbLignes: 72 },
  ],
  historiquePublications: publications,
  statistiques: {
    total_publications: 18,
    montant_total: 8450000,
    lignes_traitees: 1240,
  },
  evolution_quotidienne: [
    { date: '2026-08-05', nombre: 128, montant: 920000, lignes: 128 },
    { date: '2026-07-20', nombre: 116, montant: 840000, lignes: 114 },
    { date: '2026-07-05', nombre: 103, montant: 760000, lignes: 101 },
  ],
}

export const DEMO_PAYEUR_STATS = {
  numeroContrat: 'CTR-DEMO-2026',
  raisonSociale: 'Société Démo Africa',
  categorieClient: 'Grande Entreprise',
  nombreEntreprises: 1,
  nombreLignesActives: 8,
  nombreLignesTotal: 10,
  lignesDetail: [
    { msisdn: '99475555', utilisateur: 'Kossi Afi', forfait: 'HYB', montant: 48500, statut: 'ACTIF' },
    { msisdn: '90112233', utilisateur: 'Ama Mensah', forfait: 'OP', montant: 32750, statut: 'ACTIF' },
    { msisdn: '90887766', utilisateur: 'David Tété', forfait: 'HYB', montant: 56400, statut: 'ACTIF' },
    { msisdn: '92774411', utilisateur: 'Léa Assiba', forfait: 'OP', montant: 28900, statut: 'ACTIF' },
  ],
  lignesASurveiller: [
    { msisdn: '93665544', utilisateur: 'Nadia Koffi', probleme: 'Consommation élevée' },
  ],
  dernieresSimulations: [
    { date: '12/08/2026 09:12', montant: 178500, tauxConsommation: 76 },
    { date: '05/08/2026 14:36', montant: 165200, tauxConsommation: 68 },
    { date: '28/07/2026 10:05', montant: 152900, tauxConsommation: 61 },
  ],
  statistiques: {
    nombre_entreprises: 1,
    nombre_lignes: 10,
    nombre_lignes_actives: 8,
    total_factures: 24,
    montant_total: 3850000,
    montant_paye: 2675000,
    montant_en_attente: 1175000,
  },
}

export const DEMO_EMPLOYE_STATS = {
  ma_ligne: {
    msisdn: '99475555',
    utilisateur: 'Kossi Afi',
    cycle: 'HYB',
    forfait: 25000,
    entreprise: 'Société Démo Africa',
  },
  statistiques: {
    total_factures: 6,
    montant_total: 214500,
    moyenne_mensuelle: 35750,
  },
  dernieresSimulations: [
    { date: '12/08/2026 09:12', montant: 48500 },
    { date: '05/08/2026 14:36', montant: 46200 },
    { date: '28/07/2026 10:05', montant: 41750 },
  ],
  historique_factures: [
    { numero_facture: 'FAC-DEMO-2026-07', periode_debut: '2026-07-01', periode_fin: '2026-07-31', montant_ttc: 48500, statut: 'PUBLIEE' },
    { numero_facture: 'FAC-DEMO-2026-06', periode_debut: '2026-06-01', periode_fin: '2026-06-30', montant_ttc: 46200, statut: 'PAYEE' },
  ],
}

export const DEMO_COMMERCIAL_CONTRATS = [
  { id: 'demo-company-1', compte: 'CTR-DEMO-2026', raison_sociale: 'Société Démo Africa', categorie: 'GE', payeur_name: 'Société Démo Africa', statut: 'ACTIF', est_resilie: false },
  { id: 'demo-company-2', compte: 'CTR-DEMO-2025', raison_sociale: 'Kpalimé Services', categorie: 'PE', payeur_name: 'Kpalimé Services', statut: 'ACTIF', est_resilie: false },
  { id: 'demo-company-3', compte: 'CTR-DEMO-2024', raison_sociale: 'Togo Logistique', categorie: 'EP', payeur_name: 'Togo Logistique', statut: 'ACTIF', est_resilie: false },
]

