import { useEffect, useMemo, useState } from 'react'
import api from '../../services/api'
import ModalNouveauContrat from '../agent/components/ModalNouveauContrat'

const LABELS_STATUT = {
  PENDING: 'En attente de validation',
  APPROVED: 'Validée',
  REJECTED: 'Rejetée',
}

const COULEURS_STATUT = {
  PENDING: 'bg-amber-100 text-amber-800',
  APPROVED: 'bg-emerald-100 text-emerald-800',
  REJECTED: 'bg-red-100 text-red-800',
}

export default function CommercialDemandes() {
  const [demandes, setDemandes] = useState([])
  const [chargement, setChargement] = useState(true)
  const [modalOuvert, setModalOuvert] = useState(false)
  const [erreur, setErreur] = useState('')
  const [message, setMessage] = useState('')

  const chargerDemandes = async () => {
    setChargement(true)
    setErreur('')
    try {
      const response = await api.get('/billing/contract-requests/')
      const data = response.data?.results || response.data || []
      setDemandes(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Erreur chargement demandes commerciales:', error)
      setErreur("Impossible de charger vos demandes de contrats.")
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => { chargerDemandes() }, [])

  const soumettreDemande = async (payload) => {
    try {
      await api.post('/billing/contract-requests/', payload)
      setModalOuvert(false)
      setMessage('Demande envoyée. Le contrat sera créé après validation par un agent de facturation.')
      await chargerDemandes()
    } catch (error) {
      const data = error.response?.data || {}
      const detail = data.detail || data.error || data.payeur?.telephone?.[0] || data.contrat?.compte?.[0] || 'Impossible de soumettre la demande.'
      throw new Error(detail)
    }
  }

  const compteurs = useMemo(() => ({
    total: demandes.length,
    attente: demandes.filter(d => d.statut === 'PENDING').length,
    rejetees: demandes.filter(d => d.statut === 'REJECTED').length,
  }), [demandes])

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">Mes demandes de contrats</h1>
          <p className="text-sm text-zinc-600">Soumettez vos dossiers et suivez la décision de l’agent de facturation.</p>
        </div>
        <button onClick={() => setModalOuvert(true)} className="rounded-lg bg-[#002a7a] px-4 py-2 text-sm font-semibold text-white hover:bg-[#003d9e]">
          + Nouvelle demande
        </button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-zinc-200 bg-white p-4"><p className="text-xs text-zinc-500">Demandes soumises</p><p className="text-2xl font-bold">{compteurs.total}</p></div>
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4"><p className="text-xs text-amber-700">En attente</p><p className="text-2xl font-bold text-amber-900">{compteurs.attente}</p></div>
        <div className="rounded-xl border border-red-200 bg-red-50 p-4"><p className="text-xs text-red-700">Rejetées</p><p className="text-2xl font-bold text-red-900">{compteurs.rejetees}</p></div>
      </div>

      {message && <div className="rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{message}</div>}
      {erreur && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-800">{erreur}</div>}

      <div className="overflow-hidden rounded-xl border border-zinc-200 bg-white">
        {chargement ? <div className="py-14 text-center text-sm text-zinc-500">Chargement…</div> : demandes.length === 0 ? (
          <div className="py-14 text-center text-sm text-zinc-500">Aucune demande soumise.</div>
        ) : (
          <div className="overflow-x-auto"><table className="w-full min-w-[760px] text-sm">
            <thead className="border-b border-zinc-200 bg-zinc-50 text-left text-xs uppercase tracking-wide text-zinc-500"><tr><th className="px-5 py-3">Code contrat</th><th className="px-5 py-3">Client</th><th className="px-5 py-3">Date</th><th className="px-5 py-3">Statut</th><th className="px-5 py-3">Motif / commentaire agent</th></tr></thead>
            <tbody className="divide-y divide-zinc-100">
              {demandes.map(demande => <tr key={demande.id} className="hover:bg-zinc-50"><td className="px-5 py-3 font-semibold">{demande.compte_propose}</td><td className="px-5 py-3">{demande.raison_sociale || '—'}</td><td className="px-5 py-3">{demande.date_soumission ? new Date(demande.date_soumission).toLocaleDateString('fr-FR') : '—'}</td><td className="px-5 py-3"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${COULEURS_STATUT[demande.statut] || 'bg-zinc-100 text-zinc-700'}`}>{LABELS_STATUT[demande.statut] || demande.statut}</span></td><td className="max-w-sm px-5 py-3 text-zinc-600">{demande.decision_comment || '—'}</td></tr>)}
            </tbody>
          </table></div>
        )}
      </div>

      {modalOuvert && <ModalNouveauContrat commercialMode onClose={() => setModalOuvert(false)} onCreate={soumettreDemande} />}
    </div>
  )
}
