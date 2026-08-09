import { useEffect, useMemo, useState } from 'react'
import api from '../../services/api'
import ModalNouveauContrat from '../agent/components/ModalNouveauContrat'

function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl border border-zinc-200 p-4">
      <p className="text-xs text-zinc-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-zinc-900">{value}</p>
    </div>
  )
}

export default function CommercialDashboard() {
  const [contrats, setContrats] = useState([])
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState('')
  const [recherche, setRecherche] = useState('')
  const [selected, setSelected] = useState(null)
  const [modalOuvert, setModalOuvert] = useState(false)
  const [demandeEnvoyee, setDemandeEnvoyee] = useState('')
  const [demandes, setDemandes] = useState([])

  const chargerContrats = async () => {
    setChargement(true)
    setErreur('')
    try {
      const response = await api.get('/billing/companies/', {
        params: recherche ? { search: recherche } : undefined,
      })
      const data = response.data?.results || response.data || []
      setContrats(Array.isArray(data) ? data : [])
      const demandesResponse = await api.get('/billing/contract-requests/')
      const demandesData = demandesResponse.data?.results || demandesResponse.data || []
      setDemandes(Array.isArray(demandesData) ? demandesData : [])
    } catch (e) {
      console.error('Erreur chargement contrats commercial:', e)
      setErreur("Impossible de charger vos contrats pour l'instant.")
    } finally {
      setChargement(false)
    }
  }

  useEffect(() => {
    chargerContrats()
  }, [])

  const payeursUniques = useMemo(() => {
    const ids = new Set()
    contrats.forEach(c => {
      if (c.payeur) ids.add(c.payeur)
    })
    return ids.size
  }, [contrats])

  const contratsActifs = useMemo(() => {
    return contrats.filter(c => c.statut === 'ACTIF' && !c.est_resilie).length
  }, [contrats])

  const ouvrirDetail = async (id) => {
    try {
      const res = await api.get(`/billing/companies/${id}/`)
      setSelected(res.data)
    } catch (e) {
      console.error('Erreur détail contrat commercial:', e)
      setErreur("Impossible d'ouvrir le détail du contrat.")
    }
  }

  const soumettreDemande = async (payload) => {
    try {
      await api.post('/billing/contract-requests/', payload)
      setModalOuvert(false)
      setDemandeEnvoyee('Demande envoyée. Le contrat sera créé après validation par un agent de facturation.')
      await chargerContrats()
    } catch (e) {
      const data = e.response?.data || {}
      const message = data.detail || data.error || data.payeur?.telephone?.[0] || data.contrat?.compte?.[0] || 'Impossible de soumettre la demande de contrat.'
      setErreur(message)
      throw new Error(message)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
        <h1 className="text-2xl font-bold text-zinc-900">Espace Commercial</h1>
        <p className="text-zinc-600 text-sm">Consultez les contrats que vous avez prospectés et les informations des payeurs associés.</p>
        </div>
        <button
          onClick={() => { setErreur(''); setDemandeEnvoyee(''); setModalOuvert(true) }}
          className="rounded-lg bg-[#002a7a] px-4 py-2 text-sm font-semibold text-white hover:bg-[#003d9e]"
        >
          + Soumettre un contrat
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard label="Contrats" value={contrats.length} />
        <StatCard label="Contrats actifs" value={contratsActifs} />
        <StatCard label="Payeurs associés" value={payeursUniques} />
      </div>

      <div className="bg-white rounded-xl border border-zinc-200 p-4">
        <h2 className="mb-3 font-semibold text-zinc-900">Mes demandes de contrats</h2>
        {demandes.length === 0 ? (
          <p className="text-sm text-zinc-500">Aucune demande soumise.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] text-sm">
              <thead className="bg-zinc-50 text-left text-zinc-600">
                <tr><th className="p-3">Code</th><th className="p-3">Client</th><th className="p-3">Soumise le</th><th className="p-3">Statut</th><th className="p-3">Commentaire</th></tr>
              </thead>
              <tbody>
                {demandes.map(demande => (
                  <tr key={demande.id} className="border-t border-zinc-100">
                    <td className="p-3 font-medium">{demande.compte_propose}</td>
                    <td className="p-3">{demande.raison_sociale || '—'}</td>
                    <td className="p-3">{demande.date_soumission ? new Date(demande.date_soumission).toLocaleDateString('fr-FR') : '—'}</td>
                    <td className="p-3">{demande.statut === 'PENDING' ? 'En attente' : demande.statut === 'APPROVED' ? 'Validée' : 'Rejetée'}</td>
                    <td className="p-3">{demande.decision_comment || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-zinc-200 p-4">
        <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between mb-4">
          <h2 className="font-semibold text-zinc-900">Mes contrats</h2>
          <div className="flex gap-2">
            <input
              className="border border-zinc-300 rounded-lg px-3 py-2 text-sm"
              placeholder="Rechercher (compte, raison sociale...)"
              value={recherche}
              onChange={(e) => setRecherche(e.target.value)}
            />
            <button
              onClick={chargerContrats}
              className="px-3 py-2 rounded-lg bg-[#002a7a] text-white text-sm font-medium hover:bg-[#003d9e]"
            >
              Rechercher
            </button>
          </div>
        </div>

        {erreur && <div className="mb-3 text-sm text-red-600">{erreur}</div>}
        {demandeEnvoyee && <div className="mb-3 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800">{demandeEnvoyee}</div>}

        {chargement ? (
          <div className="py-12 text-center text-zinc-500 text-sm">Chargement...</div>
        ) : contrats.length === 0 ? (
          <div className="py-12 text-center text-zinc-500 text-sm">Aucun contrat trouvé.</div>
        ) : (
          <div className="overflow-auto">
            <table className="w-full text-sm">
              <thead className="bg-zinc-50">
                <tr>
                  <th className="text-left p-3">N° Contrat</th>
                  <th className="text-left p-3">Raison sociale</th>
                  <th className="text-left p-3">Catégorie</th>
                  <th className="text-left p-3">Payeur</th>
                  <th className="text-left p-3">Statut</th>
                  <th className="text-right p-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {contrats.map((c) => (
                  <tr key={c.id} className="border-t border-zinc-100">
                    <td className="p-3 font-medium">{c.compte || '—'}</td>
                    <td className="p-3">{c.raison_sociale || '—'}</td>
                    <td className="p-3">{c.categorie || '—'}</td>
                    <td className="p-3">{c.payeur_name || 'Non renseigné'}</td>
                    <td className="p-3">{c.est_resilie ? 'Résilié' : (c.statut || '—')}</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => ouvrirDetail(c.id)}
                        className="px-3 py-1.5 rounded-md border border-zinc-300 hover:bg-zinc-50"
                      >
                        Voir payeur
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selected && (
        <div className="fixed inset-0 z-[1100] bg-black/45 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="font-semibold text-zinc-900">Détail du payeur</h3>
              <button onClick={() => setSelected(null)} className="text-zinc-500 hover:text-zinc-800">✕</button>
            </div>
            <div className="p-4 space-y-4 text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <p className="text-zinc-500">Contrat</p>
                  <p className="font-medium">{selected.compte || '—'}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Raison sociale</p>
                  <p className="font-medium">{selected.raison_sociale || '—'}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Nom payeur</p>
                  <p className="font-medium">{selected.payeur_info?.nom || 'Non renseigné'}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Téléphone</p>
                  <p className="font-medium">{selected.payeur_info?.telephone || 'Non renseigné'}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Email</p>
                  <p className="font-medium">{selected.payeur_info?.email || 'Non renseigné'}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Identifiant</p>
                  <p className="font-medium">{selected.payeur_info?.username || 'Non renseigné'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {modalOuvert && (
        <ModalNouveauContrat
          commercialMode
          onClose={() => setModalOuvert(false)}
          onCreate={soumettreDemande}
        />
      )}
    </div>
  )
}
