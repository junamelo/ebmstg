import { motion } from 'motion/react'

export default function ContratCard({ contrat, delay, onVoirDetails }) {
  const lignesActives = contrat.lignes.filter(l => l.statut === 'ACTIF').length
  const lignesSuspendues = contrat.lignes.filter(l => l.statut === 'SUSPENDU').length

  const getStatutStyle = (statut) => {
    switch(statut) {
      case 'ACTIF':
        return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
      case 'SUSPENDU':
        return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400'
      case 'RESILIE':
        return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
      default:
        return 'bg-zinc-100 text-zinc-700'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden hover:shadow-lg transition-all cursor-pointer"
      onClick={() => onVoirDetails(contrat.id)}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-[#002a7a] to-[#003d9e] p-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-white/70 text-xs font-semibold mb-1">
              {contrat.typePayeur === 'ENTREPRISE' ? '🏢 Entreprise' : '👤 Particulier'}
            </p>
            <h3 className="text-white font-bold text-lg">
              {contrat.typePayeur === 'ENTREPRISE' ? contrat.raisonSociale : `${contrat.prenom} ${contrat.nom}`}
            </h3>
            <p className="text-white/90 text-sm font-mono">{contrat.numeroContrat}</p>
          </div>
          <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${getStatutStyle(contrat.statut)}`}>
            {contrat.statut}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Info contact */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            <span className="text-zinc-600 dark:text-zinc-400 truncate">{contrat.email}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
            </svg>
            <span className="text-zinc-600 dark:text-zinc-400">{contrat.telephone}</span>
          </div>
        </div>

        {/* Stats lignes */}
        <div className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg">
          <div className="text-center flex-1">
            <p className="text-2xl font-bold text-zinc-900 dark:text-white">{contrat.lignes.length}</p>
            <p className="text-xs text-zinc-500">Total</p>
          </div>
          <div className="w-px h-8 bg-zinc-200 dark:bg-zinc-700"></div>
          <div className="text-center flex-1">
            <p className="text-2xl font-bold text-emerald-600">{lignesActives}</p>
            <p className="text-xs text-zinc-500">Actives</p>
          </div>
          {lignesSuspendues > 0 && (
            <>
              <div className="w-px h-8 bg-zinc-200 dark:bg-zinc-700"></div>
              <div className="text-center flex-1">
                <p className="text-2xl font-bold text-orange-600">{lignesSuspendues}</p>
                <p className="text-xs text-zinc-500">Suspendues</p>
              </div>
            </>
          )}
        </div>

        {/* CA */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-zinc-500">CA mensuel</span>
          <span className="text-lg font-bold text-[#e05500]">{contrat.caMensuel.toLocaleString()} F</span>
        </div>

        {/* Date */}
        <div className="flex items-center justify-between text-xs text-zinc-500">
          <span>Créé le {new Date(contrat.dateCreation).toLocaleDateString('fr-FR')}</span>
          <span className="font-semibold">{contrat.typeContrat}</span>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-zinc-200 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/50">
        <button className="w-full text-center text-sm font-semibold text-[#002a7a] hover:text-[#003d9e] transition-colors">
          Voir les détails →
        </button>
      </div>
    </motion.div>
  )
}
