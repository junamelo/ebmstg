import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getHistoriqueSimulations } from '../../services/simulationService'
import DateRangePicker from '../../components/DateRangePicker'
import './Simulation.css'

export default function HistoriqueSimulations() {
  const [simulations, setSimulations] = useState([])
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState(null)
  const [dateRange, setDateRange] = useState({ start: null, end: null })

  useEffect(() => {
    chargerHistorique()
  }, [])

  const chargerHistorique = async () => {
    try {
      setChargement(true)
      setErreur(null)
      const data = await getHistoriqueSimulations()
      setSimulations(data)
    } catch (e) {
      console.error('Erreur chargement simulations:', e)
      setErreur('Impossible de charger l\'historique.')
      setSimulations([])
    } finally {
      setChargement(false)
    }
  }

  const parseDate = (dateStr) => {
    if (!dateStr) return null
    // Supporte "DD/MM/YYYY HH:MM", "YYYY-MM-DDTHH:MM:SS", ISO
    if (dateStr.includes('/')) {
      const [datePart] = dateStr.split(' ')
      const [day, month, year] = datePart.split('/')
      return new Date(year, month - 1, day)
    }
    return new Date(dateStr)
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '—'
    const d = parseDate(dateStr)
    if (!d || isNaN(d)) return dateStr
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  }

  const simulationsFiltrees = dateRange.start && dateRange.end
    ? simulations.filter(sim => {
        const simDate = parseDate(sim.date_simulation)
        if (!simDate) return false
        return simDate >= dateRange.start && simDate <= dateRange.end
      })
    : simulations

  if (chargement) {
    return (
      <div className="loading-overlay">
        <div className="spinner"></div>
        <span>Chargement de l'historique...</span>
      </div>
    )
  }

  return (
    <div className="simulation-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Historique de mes simulations</h1>
          <p className="text-muted">Consultez toutes vos simulations de facturation effectuées</p>
        </div>
        <Link to="/simulation" className="btn btn-primary">+ Nouvelle simulation</Link>
      </div>

      {erreur && (
        <div className="alert alert-danger" style={{ marginBottom: '16px' }}>
          {erreur}
          <button className="btn btn-outline btn-sm" style={{ marginLeft: '12px' }} onClick={chargerHistorique}>
            Réessayer
          </button>
        </div>
      )}

      {/* Filtres */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ padding: '16px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ fontSize: '14px', fontWeight: 500, color: '#555', whiteSpace: 'nowrap' }}>Période :</label>
          <DateRangePicker value={dateRange} onChange={setDateRange} placeholder="Sélectionner une période"/>
          {(dateRange.start || dateRange.end) && (
            <button className="btn btn-outline btn-sm" onClick={() => setDateRange({ start: null, end: null })}>
              Réinitialiser
            </button>
          )}
          <span style={{ marginLeft: 'auto', fontSize: '13px', color: '#6b7280' }}>
            {simulationsFiltrees.length} résultat(s)
          </span>
        </div>
      </div>

      {simulationsFiltrees.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#ccc" strokeWidth="1.5">
              <path d="M9 11l3 3L22 4"/>
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
            </svg>
            <p style={{ marginTop: '16px', fontSize: '15px', color: '#888' }}>
              {dateRange.start || dateRange.end
                ? 'Aucune simulation sur cette période.'
                : 'Vous n\'avez pas encore effectué de simulation.'}
            </p>
            <Link to="/simulation" className="btn btn-primary btn-sm" style={{ marginTop: '12px' }}>
              Faire ma première simulation
            </Link>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">{simulationsFiltrees.length} simulation(s)</h2>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Services sélectionnés</th>
                  <th>Montant estimé</th>
                </tr>
              </thead>
              <tbody>
                {simulationsFiltrees.map((sim, idx) => {
                  const services = sim.services_selectionnes || []
                  const typeClient = sim.resultat_detaille?.typeClient || '—'
                  return (
                    <tr key={sim.id || idx}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#888" strokeWidth="2">
                            <rect x="3" y="4" width="18" height="18" rx="2"/>
                            <line x1="16" y1="2" x2="16" y2="6"/>
                            <line x1="8" y1="2" x2="8" y2="6"/>
                            <line x1="3" y1="10" x2="21" y2="10"/>
                          </svg>
                          <span style={{ fontSize: '13px' }}>{formatDate(sim.date_simulation)}</span>
                          {idx === 0 && (
                            <span className="badge badge-info" style={{ fontSize: '11px' }}>Récente</span>
                          )}
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${typeClient === 'HYB' ? 'badge-info' : 'badge-success'}`}>
                          {typeClient === 'HYB' ? 'Hybride' : typeClient === 'OP' ? 'Open' : typeClient}
                        </span>
                      </td>
                      <td style={{ fontSize: '12px', color: '#6b7280' }}>
                        {services.length === 0
                          ? <span style={{ color: '#d1d5db', fontStyle: 'italic' }}>Aucun</span>
                          : services.map((s, i) => (
                            <span key={i} style={{ display: 'inline-block', marginRight: '4px', marginBottom: '2px', padding: '1px 6px', background: '#e8edf8', borderRadius: '4px', color: '#002a7a', fontSize: '11px' }}>
                              {s.nom || s}
                            </span>
                          ))
                        }
                      </td>
                      <td className="text-orange">
                        <strong style={{ fontSize: '15px' }}>
                          {Number(sim.montant_estime || 0).toLocaleString('fr-FR')} FCFA
                        </strong>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
