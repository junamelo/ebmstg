import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import api from '../../services/api'
import {
  genererBlocPdfTest,
  getStatutTraitementPdf,
  telechargerBlocPdfTest,
} from '../../services/adminService'
import './GenerateurBlocTest.css'

const toLocalIsoDate = (date) => [
  date.getFullYear(),
  String(date.getMonth() + 1).padStart(2, '0'),
  String(date.getDate()).padStart(2, '0'),
].join('-')
const today = new Date()
const initialStart = toLocalIsoDate(new Date(today.getFullYear(), today.getMonth(), 1))
const initialEnd = toLocalIsoDate(new Date(today.getFullYear(), today.getMonth() + 1, 0))

const listFromResponse = (response) => response.data?.results || response.data || []
const formatAmount = (value) => new Intl.NumberFormat('fr-FR').format(Number(value || 0))

export default function GenerateurBlocTest() {
  const location = useLocation()
  const basePath = location.pathname.startsWith('/chef') ? '/chef' : '/agent'
  const [typeFacture, setTypeFacture] = useState('SOM')
  const [lignes, setLignes] = useState([])
  const [entreprises, setEntreprises] = useState([])
  const [selected, setSelected] = useState({})
  const [periodeDebut, setPeriodeDebut] = useState(initialStart)
  const [periodeFin, setPeriodeFin] = useState(initialEnd)
  const [dateEmission, setDateEmission] = useState(toLocalIsoDate(today))
  const [tauxTva, setTauxTva] = useState('18')
  const [libelle, setLibelle] = useState('Services postpayés de test')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [message, setMessage] = useState(null)
  const [job, setJob] = useState(null)
  const [testBlock, setTestBlock] = useState(null)

  useEffect(() => {
    let cancelled = false
    const loadData = async () => {
      setLoading(true)
      try {
        const [linesResponse, companiesResponse] = await Promise.all([
          api.get('/billing/lines/'),
          api.get('/billing/companies/'),
        ])
        if (cancelled) return
        setLignes(listFromResponse(linesResponse).filter((line) => line.statut === 'ACTIF'))
        setEntreprises(listFromResponse(companiesResponse).filter((company) => !company.est_resilie))
      } catch (error) {
        if (!cancelled) {
          setMessage({ type: 'danger', text: "Impossible de charger les contrats et les lignes disponibles." })
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadData()
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    setSelected({})
    setSearch('')
  }, [typeFacture])

  useEffect(() => {
    if (!job?.id || ['TERMINE', 'ECHEC'].includes(job.statut)) return undefined
    let cancelled = false
    const refresh = async () => {
      try {
        const status = await getStatutTraitementPdf(job.id)
        if (!cancelled) setJob(status)
      } catch {
        // Le bloc reste traité côté serveur même si la vérification est temporairement indisponible.
      }
    }
    refresh()
    const interval = window.setInterval(refresh, 2000)
    return () => { cancelled = true; window.clearInterval(interval) }
  }, [job?.id, job?.statut])

  const records = useMemo(() => {
    const term = search.trim().toLowerCase()
    const source = typeFacture === 'SOM' ? lignes : entreprises
    if (!term) return source
    return source.filter((item) => {
      const haystack = typeFacture === 'SOM'
        ? `${item.msisdn} ${item.utilisateur || ''} ${item.company_name || ''}`
        : `${item.compte} ${item.raison_sociale}`
      return haystack.toLowerCase().includes(term)
    })
  }, [typeFacture, lignes, entreprises, search])

  const toggleRecord = (record) => {
    const id = String(record.id)
    setSelected((current) => {
      if (current[id]) {
        const { [id]: ignored, ...remaining } = current
        return remaining
      }
      const defaultAmount = typeFacture === 'SOM'
        ? Number(record.forfait || 0) || 10000
        : 25000
      return { ...current, [id]: String(defaultAmount) }
    })
  }

  const setAmount = (id, amount) => {
    setSelected((current) => ({ ...current, [String(id)]: amount }))
  }

  const selectedEntries = Object.entries(selected)
  const total = selectedEntries.reduce((sum, [, amount]) => sum + (Number(amount) || 0), 0)

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!selectedEntries.length) {
      setMessage({ type: 'danger', text: 'Sélectionnez au moins une ligne ou une entreprise.' })
      return
    }
    if (!periodeDebut || !periodeFin || periodeDebut > periodeFin) {
      setMessage({ type: 'danger', text: 'La période de facturation est invalide.' })
      return
    }

    const source = typeFacture === 'SOM' ? lignes : entreprises
    const items = selectedEntries.map(([id, amount]) => {
      const record = source.find((item) => String(item.id) === id)
      return typeFacture === 'SOM'
        ? { company_id: record.company, line_id: record.id, montant_ttc: amount }
        : { company_id: record.id, montant_ttc: amount }
    })

    setSubmitting(true)
    setMessage(null)
    try {
      const result = await genererBlocPdfTest({
        type_facture: typeFacture,
        periode_debut: periodeDebut,
        periode_fin: periodeFin,
        date_emission: dateEmission,
        taux_tva: tauxTva,
        libelle,
        items,
      })
      setJob(result.job)
      setTestBlock(result.test_block)
      setSelected({})
      setMessage({ type: 'success', text: result.message })
    } catch (error) {
      const data = error.response?.data
      const details = typeof data?.details === 'string' ? ` ${data.details}` : ''
      const errorText = data?.error || data?.items?.[0] || error.message || 'La génération du bloc a échoué.'
      setMessage({ type: 'danger', text: `${errorText}${details}` })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="admin-page test-block-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Générer un bloc PDF de test</h1>
          <p className="text-muted">Créez un unique PDF multi-pages, puis faites-le découper par le traitement habituel.</p>
        </div>
        <Link to={`${basePath}/publication`} className="btn btn-outline">Retour à la publication</Link>
      </div>

      <div className="test-warning">
        <i className="ti ti-flask" />
        <div><strong>Mode démonstration.</strong> Chaque page porte la mention « Facture de test » et les factures créées restent en attente de publication.</div>
      </div>

      {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}

      {job && (
        <div className={`test-job-card ${job.statut === 'ECHEC' ? 'is-error' : ''}`}>
          <div>
            <strong>Traitement du bloc : {job.statut?.replace('_', ' ')}</strong>
            <p>{job.statut === 'TERMINE' ? 'Le découpage est terminé. Les factures correspondantes peuvent être publiées.' : job.statut === 'ECHEC' ? (job.erreur || 'Le traitement a échoué.') : `Découpage en arrière-plan : ${job.progression || 0} %`}</p>
          </div>
          <div className="test-job-actions">
            {testBlock && <button type="button" className="btn btn-outline" onClick={() => telechargerBlocPdfTest(job.id, testBlock.filename)}>Télécharger le bloc</button>}
            {job.statut === 'TERMINE' && <Link className="btn btn-primary" to={`${basePath}/factures-a-publier`}>Voir les factures à publier</Link>}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="test-block-layout">
        <section className="card test-block-settings">
          <div className="card-header"><h2 className="card-title">1. Paramètres du bloc</h2></div>
          <div className="test-form-grid">
            <div className="form-group">
              <label className="form-label">Type de facture</label>
              <select className="form-control" value={typeFacture} onChange={(event) => setTypeFacture(event.target.value)} disabled={submitting}>
                <option value="SOM">Sommaire - une facture par ligne</option>
                <option value="GLO">Globale - une facture par entreprise</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Date d’émission</label>
              <input className="form-control" type="date" value={dateEmission} onChange={(event) => setDateEmission(event.target.value)} required disabled={submitting} />
            </div>
            <div className="form-group">
              <label className="form-label">Début de période</label>
              <input className="form-control" type="date" value={periodeDebut} onChange={(event) => setPeriodeDebut(event.target.value)} required disabled={submitting} />
            </div>
            <div className="form-group">
              <label className="form-label">Fin de période</label>
              <input className="form-control" type="date" value={periodeFin} onChange={(event) => setPeriodeFin(event.target.value)} required disabled={submitting} />
            </div>
            <div className="form-group">
              <label className="form-label">Taux de TVA (%)</label>
              <input className="form-control" type="number" min="0" max="100" step="0.01" value={tauxTva} onChange={(event) => setTauxTva(event.target.value)} disabled={submitting} />
            </div>
            <div className="form-group test-libelle-field">
              <label className="form-label">Libellé affiché</label>
              <input className="form-control" value={libelle} onChange={(event) => setLibelle(event.target.value)} maxLength="120" required disabled={submitting} />
            </div>
          </div>
        </section>

        <section className="card test-block-selection">
          <div className="card-header test-selection-header">
            <div>
              <h2 className="card-title">2. Sélectionner les {typeFacture === 'SOM' ? 'lignes' : 'entreprises'}</h2>
              <p className="text-muted">Maximum 100 factures par bloc de test.</p>
            </div>
            <input className="form-control test-search" placeholder="Rechercher…" value={search} onChange={(event) => setSearch(event.target.value)} />
          </div>

          {loading ? <div className="empty-state"><p>Chargement des données…</p></div> : records.length === 0 ? (
            <div className="empty-state"><p>Aucune donnée disponible pour ce type de bloc.</p></div>
          ) : (
            <div className="test-selection-list">
              {records.map((record) => {
                const id = String(record.id)
                const checked = Object.prototype.hasOwnProperty.call(selected, id)
                const label = typeFacture === 'SOM'
                  ? `${record.msisdn} - ${record.utilisateur || 'Utilisateur non renseigné'}`
                  : `${record.compte} - ${record.raison_sociale}`
                const detail = typeFacture === 'SOM'
                  ? record.company_name
                  : `${record.nombre_lignes || 0} ligne(s) active(s)`
                return (
                  <div className={`test-selection-row ${checked ? 'selected' : ''}`} key={id}>
                    <label>
                      <input type="checkbox" checked={checked} onChange={() => toggleRecord(record)} disabled={submitting || (!checked && selectedEntries.length >= 100)} />
                      <span><strong>{label}</strong><small>{detail}</small></span>
                    </label>
                    {checked && <label className="test-amount"><span>Montant TTC</span><input type="number" min="1" step="1" value={selected[id]} onChange={(event) => setAmount(id, event.target.value)} disabled={submitting} /><em>FCFA</em></label>}
                  </div>
                )
              })}
            </div>
          )}
        </section>

        <section className="test-block-footer">
          <div><strong>{selectedEntries.length}</strong> facture(s) sélectionnée(s) · Montant TTC total : <strong>{formatAmount(total)} FCFA</strong></div>
          <button type="submit" className="btn btn-primary" disabled={submitting || !selectedEntries.length}>
            {submitting ? 'Génération et envoi…' : 'Générer et lancer le découpage'}
          </button>
        </section>
      </form>
    </div>
  )
}
