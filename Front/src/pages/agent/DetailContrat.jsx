import { useState } from 'react'
import { motion } from 'motion/react'
import { useParams, useNavigate } from 'react-router-dom'

export default function DetailContrat() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [ongletActif, setOngletActif] = useState('infos')

  // Mock data - à remplacer par un appel API
  const [contrat] = useState({
    id: '1',
    numeroContrat: 'A2600001',
    typePayeur: 'ENTREPRISE',
    raisonSociale: 'BIOSPARTNERS',
    email: 'contact@biospartners.com',
    telephone: '+228 22 00 00 00',
    adresse: 'Lomé, Togo',
    dateCreation: '2020-01-15',
    statut: 'ACTIF',
    typeContrat: 'Professionnel',
    dureeEngagement: 24,
    modeFacturation: 'Mensuel',
    agentResponsable: 'agent@moov.tg',
    lignes: [
      {
        id: '1',
        numero: '79 34 27 35',
        employe: { nom: 'TOTSOVI', prenom: 'Eyram', email: 'e.totsovi@biospartners.com' },
        statut: 'ACTIF',
        dateActivation: '2020-03-20',
        forfaits: ['No Limit AI50', 'Facture Détaillée'],
        consommation: { voix: 450, sms: 120, data: 15.5 },
        montantEstime: 45000
      },
      {
        id: '2',
        numero: '79 34 27 36',
        employe: { nom: 'AGBEKO', prenom: 'Koffi', email: 'k.agbeko@biospartners.com' },
        statut: 'ACTIF',
        dateActivation: '2020-06-15',
        forfaits: ['BlackBerry BB15_6'],
        consommation: { voix: 320, sms: 85, data: 8.2 },
        montantEstime: 38000
      },
      {
        id: '3',
        numero: '79 34 27 37',
        employe: { nom: 'MENSAH', prenom: 'Divine', email: 'd.mensah@biospartners.com' },
        statut: 'SUSPENDU',
        dateActivation: '2021-08-10',
        forfaits: ['No Limit AI70'],
        consommation: { voix: 0, sms: 0, data: 0 },
        montantEstime: 0
      }
    ],
    historiqueFacturation: [
      { mois: 'Juillet 2026', montant: 135000, statut: 'Payée', datePaiement: '2026-08-05' },
      { mois: 'Juin 2026', montant: 132000, statut: 'Payée', datePaiement: '2026-07-03' },
      { mois: 'Mai 2026', montant: 128000, statut: 'Payée', datePaiement: '2026-06-02' }
    ]
  })

  const lignesActives = contrat.lignes.filter(l => l.statut === 'ACTIF').length
  const caMensuel = contrat.lignes.reduce((sum, l) => sum + l.montantEstime, 0)

  const getStatutStyle = (statut) => {
    return statut === 'ACTIF'
      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
      : statut === 'SUSPENDU'
      ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header avec retour */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <button onClick={() => navigate('/agent/contrats')}
          className="inline-flex items-center gap-2 text-[#002a7a] hover:text-[#003d9e] font-semibold mb-4">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <path d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Retour aux contrats
        </button>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-zinc-900 dark:text-white">
                {contrat.typePayeur === 'ENTREPRISE' ? contrat.raisonSociale : `${contrat.prenom} ${contrat.nom}`}
              </h1>
              <span className={`px-3 py-1 rounded-full text-sm font-bold ${getStatutStyle(contrat.statut)}`}>
                {contrat.statut}
              </span>
            </div>
            <p className="text-zinc-600 dark:text-zinc-400 font-mono text-lg">{contrat.numeroContrat}</p>
          </div>
          <button className="px-4 py-2.5 bg-gradient-to-br from-[#e05500] to-[#c2410c] text-white font-semibold rounded-lg hover:shadow-lg transition-all">
            + Nouvelle Ligne
          </button>
        </div>
      </motion.div>

      {/* Stats rapides */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#002a7a]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{contrat.lignes.length}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Total lignes</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{lignesActives}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Lignes actives</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-[#e05500]/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-[#e05500]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{caMensuel.toLocaleString()}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">CA mensuel (F)</p>
            </div>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
          className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-zinc-900 dark:text-white">{contrat.dureeEngagement}</p>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">Mois engagement</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Onglets */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden">
        <div className="border-b border-zinc-200 dark:border-zinc-800">
          <div className="flex">
            {['infos', 'lignes', 'historique'].map((onglet) => (
              <button key={onglet} onClick={() => setOngletActif(onglet)}
                className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                  ongletActif === onglet
                    ? 'text-[#002a7a] border-b-2 border-[#002a7a] bg-[#002a7a]/5'
                    : 'text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300'
                }`}>
                {onglet === 'infos' && 'Informations'}
                {onglet === 'lignes' && `Lignes (${contrat.lignes.length})`}
                {onglet === 'historique' && 'Historique'}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {/* Onglet Infos */}
          {ongletActif === 'infos' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-bold text-zinc-500 uppercase mb-4">Informations Client</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Email</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">{contrat.email}</p>
                    </div>
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Téléphone</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">{contrat.telephone}</p>
                    </div>
                    {contrat.adresse && (
                      <div>
                        <p className="text-xs text-zinc-500 mb-1">Adresse</p>
                        <p className="text-zinc-900 dark:text-white font-semibold">{contrat.adresse}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-zinc-500 uppercase mb-4">Détails Contrat</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Type de contrat</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">{contrat.typeContrat}</p>
                    </div>
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Mode de facturation</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">{contrat.modeFacturation}</p>
                    </div>
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Date de création</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">
                        {new Date(contrat.dateCreation).toLocaleDateString('fr-FR')}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-zinc-500 mb-1">Agent responsable</p>
                      <p className="text-zinc-900 dark:text-white font-semibold">{contrat.agentResponsable}</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Onglet Lignes */}
          {ongletActif === 'lignes' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-zinc-50 dark:bg-zinc-900/50 border-b border-zinc-200 dark:border-zinc-800">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Numéro</th>
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Employé</th>
                      <th className="px-4 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Forfaits</th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Consommation</th>
                      <th className="px-4 py-3 text-center text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Statut</th>
                      <th className="px-4 py-3 text-right text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Montant</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                    {contrat.lignes.map((ligne, idx) => (
                      <tr key={ligne.id} className="hover:bg-zinc-50/80 dark:hover:bg-zinc-800/40">
                        <td className="px-4 py-4 font-mono font-semibold text-zinc-900 dark:text-white">{ligne.numero}</td>
                        <td className="px-4 py-4">
                          <p className="font-semibold text-zinc-900 dark:text-white">{ligne.employe.prenom} {ligne.employe.nom}</p>
                          <p className="text-sm text-zinc-500">{ligne.employe.email}</p>
                        </td>
                        <td className="px-4 py-4">
                          <div className="flex flex-wrap gap-1">
                            {ligne.forfaits.map((forfait, i) => (
                              <span key={i} className="px-2 py-0.5 rounded text-xs font-medium bg-[#002a7a]/10 text-[#002a7a]">
                                {forfait}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="px-4 py-4 text-right text-sm">
                          <p>{ligne.consommation.voix} min</p>
                          <p>{ligne.consommation.sms} SMS</p>
                          <p>{ligne.consommation.data} Go</p>
                        </td>
                        <td className="px-4 py-4 text-center">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getStatutStyle(ligne.statut)}`}>
                            {ligne.statut}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-right font-bold text-zinc-900 dark:text-white">
                          {ligne.montantEstime.toLocaleString()} F
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {/* Onglet Historique */}
          {ongletActif === 'historique' && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="space-y-3">
                {contrat.historiqueFacturation.map((facture, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
                    <div>
                      <p className="font-semibold text-zinc-900 dark:text-white">{facture.mois}</p>
                      <p className="text-sm text-zinc-500">Payée le {new Date(facture.datePaiement).toLocaleDateString('fr-FR')}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-zinc-900 dark:text-white">{facture.montant.toLocaleString()} F CFA</p>
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-700">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                        </svg>
                        {facture.statut}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
