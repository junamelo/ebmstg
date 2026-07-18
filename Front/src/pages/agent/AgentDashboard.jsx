import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'motion/react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { getStatsAgentFacturation } from '../../services/adminService'

// Design moderne avec Geist-inspired layout + glassmorphism subtil
// DESIGN_VARIANCE: 6 | MOTION_INTENSITY: 4 | VISUAL_DENSITY: 6

// ── Tooltip personnalisé pour le graphique ─────────────────────
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-zinc-200 rounded-lg shadow-lg p-3 text-sm">
      <p className="font-semibold text-zinc-700 mb-2">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ background: p.color }} />
          <span className="text-zinc-600">{p.name} :</span>
          <span className="font-bold text-zinc-900">{p.value}</span>
        </div>
      ))}
    </div>
  )
}

function StatutPublicationHero({ statut, nbFactures, date }) {
  const variants = {
    TRAITEE: { bg: 'from-emerald-500/10 to-emerald-600/5', badge: 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300', icon: '✓' },
    EN_COURS: { bg: 'from-amber-500/10 to-amber-600/5', badge: 'bg-amber-500/20 text-amber-700 dark:text-amber-300', icon: '⏳' },
    ERREUR: { bg: 'from-rose-500/10 to-rose-600/5', badge: 'bg-rose-500/20 text-rose-700 dark:text-rose-300', icon: '✕' }
  }
  const v = variants[statut] || variants.ERREUR

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${v.bg} border border-zinc-200/50 dark:border-zinc-800/50 p-8`}
    >
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-6">
          <div>
            <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-2">Publication du mois</p>
            <h2 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white">
              {nbFactures.toLocaleString('fr-FR')} factures
            </h2>
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${v.badge} backdrop-blur-sm font-semibold text-sm`}>
            <span>{v.icon}</span>
            <span>{statut === 'TRAITEE' ? 'Traitée' : statut === 'EN_COURS' ? 'En cours' : 'Erreur'}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-400">
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" width="16" height="16">
            <rect x="3" y="4" width="18" height="18" rx="2" />
            <path d="M16 2v4M8 2v4M3 10h18" />
          </svg>
          <span>Publiée le {date}</span>
        </div>
      </div>
    </motion.div>
  )
}

function AlerteMetric({ titre, count, type, delay }) {
  const colors = {
    danger: 'border-rose-200 dark:border-rose-900/30 bg-rose-50/50 dark:bg-rose-950/20',
    warning: 'border-amber-200 dark:border-amber-900/30 bg-amber-50/50 dark:bg-amber-950/20',
    info: 'border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900'
  }

  const textColors = {
    danger: 'text-rose-600 dark:text-rose-400',
    warning: 'text-amber-600 dark:text-amber-400',
    info: 'text-zinc-600 dark:text-zinc-400'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.16, 1, 0.3, 1] }}
      className={`rounded-xl border p-5 backdrop-blur-sm ${colors[type]}`}
    >
      <div className={`text-4xl font-bold tracking-tight mb-2 ${textColors[type]}`}>
        {count}
      </div>
      <p className="text-sm font-medium text-zinc-700 dark:text-zinc-300">{titre}</p>
    </motion.div>
  )
}

export default function AgentDashboard() {
  const [stats, setStats] = useState(null)
  const [chargement, setChargement] = useState(true)
  const [anneeGraphique, setAnneeGraphique] = useState('2026')

  useEffect(() => {
    getStatsAgentFacturation()
      .then(setStats)
      .catch(console.error)
      .finally(() => setChargement(false))
  }, [])

  if (chargement) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-zinc-300 border-t-[#002a7a] rounded-full animate-spin" />
          <span className="text-sm text-zinc-600 dark:text-zinc-400">Chargement...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white mb-2">
          Facturation
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Gestion des publications et opérations de facturation
        </p>
      </motion.div>

      {/* Statut Hero */}
      <StatutPublicationHero
        statut={stats.statutPublication}
        nbFactures={stats.nbFacturesGenerees}
        date={stats.datePublication}
      />

      {/* Graphique des publications */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Évolution des publications</h2>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">Factures publiées par mois</p>
          </div>
          {/* Filtre années */}
          <div className="flex gap-1 bg-zinc-100 dark:bg-zinc-800 rounded-lg p-1">
            {['2024', '2025', '2026'].map(a => (
              <button
                key={a}
                onClick={() => setAnneeGraphique(a)}
                className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                  anneeGraphique === a
                    ? 'bg-white dark:bg-zinc-700 text-[#002a7a] dark:text-[#78b4dc] shadow-sm'
                    : 'text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-300'
                }`}
              >
                {a}
              </button>
            ))}
          </div>
        </div>

        <ResponsiveContainer width="100%" height={260}>
          <LineChart
            data={stats.historiquePublications}
            margin={{ top: 5, right: 10, left: -20, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="periode" tick={{ fontSize: 12, fill: '#888' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 12, fill: '#888' }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(value) => <span style={{ fontSize: 12, color: '#666' }}>{value}</span>}
            />
            <Line
              type="monotone"
              dataKey="nbFactures"
              name="Factures publiées"
              stroke="#002a7a"
              strokeWidth={2.5}
              dot={{ fill: '#002a7a', r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="nbFacturesTraitees"
              name="Factures traitées"
              stroke="#e05500"
              strokeWidth={2.5}
              dot={{ fill: '#e05500', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Alertes Grid */}
      <div>
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-white mb-4">Alertes</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <AlerteMetric
            titre="Factures non publiées"
            count={stats.facturesNonPubliees}
            type={stats.facturesNonPubliees > 0 ? 'danger' : 'info'}
            delay={0.1}
          />
          <AlerteMetric
            titre="Erreurs de découpage PDF"
            count={stats.erreursDecoupage}
            type={stats.erreursDecoupage > 0 ? 'danger' : 'info'}
            delay={0.15}
          />
          <AlerteMetric
            titre="Lignes sans forfait"
            count={stats.lignesSansForfait}
            type={stats.lignesSansForfait > 0 ? 'warning' : 'info'}
            delay={0.2}
          />
        </div>
      </div>

      {/* Services actifs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden"
      >
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Services et tarifs actifs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-zinc-50 dark:bg-zinc-900/50 text-xs uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">Service</th>
                <th className="px-6 py-3 text-right font-semibold">Tarif</th>
                <th className="px-6 py-3 text-right font-semibold">Lignes</th>
                <th className="px-6 py-3 text-center font-semibold">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {stats.servicesActifs.map((service, idx) => (
                <motion.tr
                  key={idx}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.35 + idx * 0.05 }}
                  className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
                >
                  <td className="px-6 py-4 font-medium text-zinc-900 dark:text-white">{service.nom}</td>
                  <td className="px-6 py-4 text-right font-mono text-zinc-700 dark:text-zinc-300">
                    {service.tarif.toLocaleString('fr-FR')} FCFA
                  </td>
                  <td className="px-6 py-4 text-right text-zinc-600 dark:text-zinc-400">
                    {service.nbLignes.toLocaleString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-700 dark:text-emerald-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                      Actif
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Actions rapides */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="grid grid-cols-1 md:grid-cols-2 gap-4"
      >
        <Link
          to="/agent/publication"
          className="group relative overflow-hidden rounded-xl bg-gradient-to-br from-[#002a7a] to-[#003087] p-6 text-white transition-transform hover:scale-[1.02] active:scale-[0.98]"
        >
          <div className="relative z-10">
            <h3 className="text-lg font-semibold mb-1">Nouvelle publication</h3>
            <p className="text-sm text-white/80">Uploader et traiter un bloc PDF</p>
          </div>
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500" />
        </Link>

        <Link
          to="/agent/forfaits"
          className="group relative overflow-hidden rounded-xl bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 p-6 transition-all hover:border-[#e05500] hover:shadow-lg hover:shadow-[#e05500]/10"
        >
          <div className="relative z-10">
            <h3 className="text-lg font-semibold text-zinc-900 dark:text-white mb-1">Gérer les forfaits</h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">Créer et modifier les forfaits</p>
          </div>
        </Link>
      </motion.div>

      {/* Historique */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden"
      >
        <div className="p-6 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Historique des publications</h2>
          <Link to="/agent/publication" className="text-sm font-medium text-[#002a7a] hover:text-[#003087] dark:text-[#78b4dc] transition-colors">
            Voir tout →
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-zinc-50 dark:bg-zinc-900/50 text-xs uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">Date</th>
                <th className="px-6 py-3 text-left font-semibold">Période</th>
                <th className="px-6 py-3 text-right font-semibold">Factures</th>
                <th className="px-6 py-3 text-center font-semibold">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {stats.historiquePublications.map((pub, idx) => (
                <tr key={idx} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors">
                  <td className="px-6 py-4 text-sm text-zinc-600 dark:text-zinc-400">{pub.date}</td>
                  <td className="px-6 py-4 font-medium text-zinc-900 dark:text-white">{pub.periode}</td>
                  <td className="px-6 py-4 text-right font-mono text-zinc-700 dark:text-zinc-300">
                    {pub.nbFactures.toLocaleString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                      pub.statut === 'TRAITEE' ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' : 'bg-zinc-500/10 text-zinc-700 dark:text-zinc-400'
                    }`}>
                      {pub.statut === 'TRAITEE' ? 'Traitée' : pub.statut}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  )
}
