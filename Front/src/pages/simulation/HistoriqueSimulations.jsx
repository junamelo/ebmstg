import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getStatsEmploye } from '../../services/adminService'
import DateRangePicker from '../../components/DateRangePicker'
import './Simulation.css'

export default function HistoriqueSimulations() {
  const [simulations, setSimulations] = useState([])
  const [chargement, setChargement] = useState(true)
  const [dateRange, setDateRange] = useState({ start: null, end: null })

  useEffect(() => {
    getStatsEmploye()
      .then(stats => {
        // Ajouter plus de simulations mockées pour le test
        const simulationsEtendues = [
          ...(stats.dernieresSimulations || []),
          { date: '15/07/2026', montant: 89450, tauxConsommation: 58 },
          { date: '12/07/2026', montant: 134200, tauxConsommation: 85 },
          { date: '08/07/2026', montant: 76800, tauxConsommation: 49 },
          { date: '25/06/2026', montant: 102350, tauxConsommation: 71 },
          { date: '20/06/2026', montant: 95780, tauxConsommation: 63 },
          { date: '15/06/2026', montant: 118900, tauxConsommation: 79 },
          { date: '10/06/2026', montant: 87650, tauxConsommation: 56 },
          { date: '05/06/2026', montant: 145600, tauxConsommation: 92 },
        ]
        setSimulations(simulationsEtendues)
      })
      .catch(console.error)
      .finally(() => setChargement(false))
  }, [])

  const parseDate = (dateStr) => {
    const [day, month, year] = dateStr.split('/')
    return new Date(year, month - 1, day)
  }

  const simulationsFiltrees = dateRange.start && dateRange.end
    ? simulations.filter(sim => {
        const simDate = parseDate(sim.date)
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
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Historique de mes simulations</h1>
          <p className="text-muted">
            Consultez toutes vos simulations de facturation effectuées
          </p>
        </div>
        <Link to="/simulation" className="btn btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Nouvelle simulation
        </Link>
      </div>

      {/* Filtres */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="card-body" style={{ padding: '16px' }}>
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
            <label style={{ fontSize: '14px', fontWeight: 500, color: '#555', whiteSpace: 'nowrap' }}>
              Période :
            </label>
            <DateRangePicker 
              value={dateRange}
              onChange={setDateRange}
              placeholder="Sélectionner une période"
            />
            {(dateRange.start || dateRange.end) && (
              <button
                className="btn btn-outline btn-sm"
                onClick={() => setDateRange({ start: null, end: null })}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
                Réinitialiser
              </button>
            )}
            <div style={{ marginLeft: 'auto', fontSize: '13px', color: '#6b7280' }}>
              {simulationsFiltrees.length} résultat(s)
            </div>
          </div>
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
                ? 'Aucune simulation trouvée pour cette période.'
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
            <h2 className="card-title">
              {simulationsFiltrees.length} simulation(s)
            </h2>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Montant estimé</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {simulationsFiltrees.map((sim, idx) => {
                  const isRecent = idx === 0

                  return (
                    <tr key={idx}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#888" strokeWidth="2">
                            <rect x="3" y="4" width="18" height="18" rx="2"/>
                            <line x1="16" y1="2" x2="16" y2="6"/>
                            <line x1="8" y1="2" x2="8" y2="6"/>
                            <line x1="3" y1="10" x2="21" y2="10"/>
                          </svg>
                          {sim.date}
                          {isRecent && (
                            <span className="badge badge-info" style={{ fontSize: '11px' }}>
                              Récente
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="text-orange">
                        <strong style={{ fontSize: '15px' }}>
                          {sim.montant.toLocaleString('fr-FR')} FCFA
                        </strong>
                      </td>
                      <td>
                        <button className="btn btn-secondary btn-sm">
                          Voir détails
                        </button>
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
