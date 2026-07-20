import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'motion/react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { getStatistiques } from '../../services/adminService'
import { getStatsAppareils } from '../../services/deviceService'

// ── KPI Card avec badge % ──────────────────────────────────────
function KpiCard({ label, value, evolution, sub, icon, couleur, delay }) {
  const positif = evolution >= 0
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.16, 1, 0.3, 1] }}
      className="bg-white rounded-xl border border-zinc-200 p-6 flex flex-col gap-3"
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-zinc-500">{label}</span>
        <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: couleur + '18' }}>
          {icon}
        </div>
      </div>
      <div>
        <p className="text-3xl font-bold tracking-tight text-zinc-900">{value}</p>
        {sub && <p className="text-xs text-zinc-400 mt-1">{sub}</p>}
      </div>
      {evolution !== undefined && (
        <div className="flex items-center gap-1.5">
          <span
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold"
            style={{
              background: positif ? '#dcfce7' : '#fde8e8',
              color: positif ? '#15803d' : '#b91c1c'
            }}
          >
            {positif ? '▲' : '▼'} {Math.abs(evolution).toFixed(1)}%
          </span>
          <span className="text-xs text-zinc-400">vs mois précédent</span>
        </div>
      )}
    </motion.div>
  )
}

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

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [statsAppareils, setStatsAppareils] = useState(null)
  const [chargement, setChargement] = useState(true)
  const [anneeGraphique, setAnneeGraphique] = useState('2026')

  useEffect(() => {
    getStatistiques()
      .then(setStats)
      .catch(console.error)
      .finally(() => setChargement(false))
    setStatsAppareils(getStatsAppareils())
  }, [])

  if (chargement) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-zinc-300 border-t-[#002a7a] rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

      {/* Header */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 mb-1">Administration</h1>
        <p className="text-zinc-500">Vue globale de la plateforme Moov Africa e-Billings</p>
      </motion.div>

      {/* ── 3 KPI cards avec badge % ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KpiCard
          label="Contrats actifs"
          value={stats.totalContrats.toLocaleString('fr-FR')}
          evolution={stats.evolutionContrats}
          sub="Entreprises clientes postpayées"
          couleur="#e05500"
          delay={0.1}
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e05500" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          }
        />
        <KpiCard
          label="Lignes postpayées"
          value={stats.totalLignesActives.toLocaleString('fr-FR')}
          evolution={stats.evolutionLignes}
          sub="Numéros actifs sur le réseau"
          couleur="#002a7a"
          delay={0.15}
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#002a7a" strokeWidth="2">
              <rect x="5" y="2" width="14" height="20" rx="2"/>
              <line x1="12" y1="18" x2="12.01" y2="18"/>
            </svg>
          }
        />
        <KpiCard
          label="Utilisateurs connectés"
          value={stats.totalUtilisateursActifs.toLocaleString('fr-FR')}
          evolution={stats.evolutionUtilisateurs}
          sub="Comptes actifs sur le portail"
          couleur="#059669"
          delay={0.2}
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          }
        />
      </div>

      {/* ── Layout 2 colonnes : graphique + appareils ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Graphique Statistics — 2/3 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="lg:col-span-2 bg-white rounded-xl border border-zinc-200 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold text-zinc-900">Publications de factures</h2>
              <p className="text-sm text-zinc-400 mt-0.5">Factures globales et sommaires publiées par mois</p>
            </div>
            {/* Filtre années */}
            <div className="flex gap-1 bg-zinc-100 rounded-lg p-1">
              {['2024', '2025', '2026'].map(a => (
                <button
                  key={a}
                  onClick={() => setAnneeGraphique(a)}
                  className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                    anneeGraphique === a
                      ? 'bg-white text-[#002a7a] shadow-sm'
                      : 'text-zinc-500 hover:text-zinc-700'
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
              <XAxis dataKey="mois" tick={{ fontSize: 12, fill: '#888' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#888' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                formatter={(value) => <span style={{ fontSize: 12, color: '#666' }}>{value}</span>}
              />
              <Line
                type="monotone"
                dataKey="globales"
                name="Factures Globales"
                stroke="#002a7a"
                strokeWidth={2.5}
                dot={{ fill: '#002a7a', r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="sommaires"
                name="Factures Sommaires"
                stroke="#e05500"
                strokeWidth={2.5}
                dot={{ fill: '#e05500', r: 4 }}
                activeDot={{ r: 6 }}
                // Les valeurs sommaires sont très grandes — on les divise par 1000 pour l'affichage
                // Note: en production, utiliser un axe Y secondaire
              />
            </LineChart>
          </ResponsiveContainer>

          <p className="text-xs text-zinc-400 mt-2 text-center">
            * Les factures sommaires sont affichées en milliers
          </p>
        </motion.div>

        {/* Widget Appareils — 1/3 */}
        {statsAppareils && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.35 }}
            className="bg-white rounded-xl border border-zinc-200 p-6 flex flex-col"
          >
            <h2 className="text-lg font-semibold text-zinc-900 mb-1">Visiteurs actifs</h2>
            <p className="text-sm text-zinc-400 mb-6">Par type d'appareil</p>

            {/* Icône + chiffre central */}
            <div className="flex flex-col items-center mb-6">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#002a7a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mb-3">
                <circle cx="10" cy="7" r="4"/>
                <path d="M6 21v-2a4 4 0 0 1 4-4h1"/>
                <path d="M16 19l2 2 4-4"/>
              </svg>
              <p className="text-5xl font-bold text-zinc-900 tracking-tight">
                {statsAppareils.total.toLocaleString('fr-FR')}
              </p>
              <p className="text-sm text-zinc-400 mt-1">Connexions enregistrées</p>
            </div>

            {/* Barre dégradée */}
            <div className="w-full h-2 bg-zinc-100 rounded-full overflow-hidden mb-6">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: '82%' }}
                transition={{ duration: 1, delay: 0.6, ease: 'easeOut' }}
                className="h-full rounded-full"
                style={{ background: 'linear-gradient(90deg, #002a7a, #e05500)' }}
              />
            </div>

            {/* 3 colonnes */}
            <div className="grid grid-cols-3 divide-x divide-zinc-100 mt-auto">
              {[
                { label: 'Desktop',  key: 'DESKTOP', couleur: '#002a7a' },
                { label: 'Mobile',   key: 'MOBILE',  couleur: '#e05500' },
                { label: 'Tablette', key: 'TABLET',  couleur: '#2d6ea8' },
              ].map(item => {
                const pct = statsAppareils.total > 0
                  ? Math.round((statsAppareils.repartition[item.key] / statsAppareils.total) * 100)
                  : 0
                return (
                  <div key={item.key} className="flex flex-col items-center py-2">
                    <span className="text-2xl font-bold" style={{ color: item.couleur }}>{pct}%</span>
                    <span className="text-xs text-zinc-400 mt-1">{item.label}</span>
                    {/* Mini barre indicateur */}
                    <div className="w-8 h-1 rounded-full mt-2 bg-zinc-100 overflow-hidden">
                      <div className="h-full rounded-full" style={{ width: `${pct}%`, background: item.couleur }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>
        )}
      </div>

      {/* ── Actions rapides ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { to: '/admin/comptes?action=nouveau', titre: 'Créer un compte',     desc: 'Ajouter un utilisateur',        couleur: '#002a7a' },
          { to: '/admin/comptes?recherche=contrat', titre: 'Rechercher un contrat', desc: 'Par numéro de contrat',    couleur: '#e05500' },
          { to: '/admin/comptes?recherche=ligne',   titre: 'Rechercher une ligne',  desc: 'Par numéro de ligne MSISDN', couleur: '#002a7a' },
        ].map((action, idx) => (
          <Link
            key={idx}
            to={action.to}
            className="group relative overflow-hidden rounded-xl bg-white border border-zinc-200 p-6 transition-all hover:shadow-md"
            style={{ '--hover-color': action.couleur }}
          >
            <h3 className="text-base font-semibold text-zinc-900 mb-1">{action.titre}</h3>
            <p className="text-sm text-zinc-400">{action.desc}</p>
            <div
              className="absolute bottom-0 right-0 w-20 h-20 rounded-full -mr-10 -mb-10 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:scale-150"
              style={{ background: action.couleur + '12' }}
            />
          </Link>
        ))}
      </div>

      {/* ── Historique des simulations ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.35 }}
        className="bg-white rounded-xl border border-zinc-200 overflow-hidden"
      >
        <div className="p-6 border-b border-zinc-100 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-zinc-900">Historique des simulations</h2>
            <p className="text-sm text-zinc-400 mt-0.5">Simulations récentes de tous les utilisateurs</p>
          </div>
          <div className="flex items-center gap-2">
            {/* Filtre par rôle */}
            <select className="px-3 py-1.5 text-xs border border-zinc-200 rounded-lg bg-white text-zinc-600">
              <option value="">Tous les rôles</option>
              <option value="EMPLOYE">Employés</option>
              <option value="PAYEUR">Payeurs</option>
            </select>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-zinc-50 text-xs uppercase tracking-wider text-zinc-500">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">Utilisateur</th>
                <th className="px-6 py-3 text-left font-semibold">Rôle</th>
                <th className="px-6 py-3 text-left font-semibold">Entreprise</th>
                <th className="px-6 py-3 text-left font-semibold">Date</th>
                <th className="px-6 py-3 text-left font-semibold">Montant</th>
                <th className="px-6 py-3 text-left font-semibold">Taux conso.</th>
                <th className="px-6 py-3 text-left font-semibold">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-50">
              {stats.simulationsGlobales?.slice(0, 8).map((sim, idx) => (
                <tr key={idx} className="hover:bg-zinc-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-zinc-900">{sim.utilisateur}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                      sim.role === 'EMPLOYE' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {sim.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-zinc-600">{sim.entreprise}</td>
                  <td className="px-6 py-4 text-sm text-zinc-500">{sim.date}</td>
                  <td className="px-6 py-4 text-sm font-semibold text-zinc-900">{sim.montant}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-2 bg-zinc-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            sim.tauxConsommation >= 80 ? 'bg-red-500' :
                            sim.tauxConsommation >= 60 ? 'bg-orange-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(sim.tauxConsommation, 100)}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-zinc-600 w-8">{sim.tauxConsommation}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                      sim.tauxConsommation >= 80 ? 'bg-red-100 text-red-700' :
                      sim.tauxConsommation >= 60 ? 'bg-orange-100 text-orange-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {sim.tauxConsommation >= 80 ? 'Critique' :
                       sim.tauxConsommation >= 60 ? 'Modéré' : 'Optimal'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {stats.simulationsGlobales?.length > 8 && (
          <div className="p-4 border-t border-zinc-100 bg-zinc-50 text-center">
            <button className="text-sm text-[#002a7a] hover:text-[#e05500] font-medium transition-colors">
              Voir toutes les simulations ({stats.simulationsGlobales.length})
            </button>
          </div>
        )}
      </motion.div>

      {/* ── Dernières connexions ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-white rounded-xl border border-zinc-200 overflow-hidden"
      >
        <div className="p-6 border-b border-zinc-100">
          <h2 className="text-lg font-semibold text-zinc-900">Dernières connexions</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-zinc-50 text-xs uppercase tracking-wider text-zinc-500">
              <tr>
                <th className="px-6 py-3 text-left font-semibold">Utilisateur</th>
                <th className="px-6 py-3 text-left font-semibold">Rôle</th>
                <th className="px-6 py-3 text-left font-semibold">Date / Heure</th>
                <th className="px-6 py-3 text-left font-semibold">IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-50">
              {stats.dernieresConnexions?.map((conn, idx) => (
                <tr key={idx} className="hover:bg-zinc-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-zinc-900">{conn.nom}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                      conn.role === 'SUPER_ADMIN'       ? 'bg-rose-100 text-rose-700'    :
                      conn.role === 'AGENT_FACTURATION' ? 'bg-violet-100 text-violet-700' :
                      conn.role === 'PAYEUR'            ? 'bg-blue-100 text-blue-700'    :
                      'bg-zinc-100 text-zinc-600'
                    }`}>
                      {conn.role.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-zinc-500">{conn.date}</td>
                  <td className="px-6 py-4 text-sm font-mono text-zinc-400">{conn.ip}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

    </div>
  )
}
