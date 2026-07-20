import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getStatsEmploye } from '../../services/adminService'
import './Simulation.css'

export default function HistoriqueSimulations() {
  const [simulations, setSimulations] = useState([])
  const [chargement, setChargement] = useState(true)
  const [filtreDate, setFiltreDate] = useState('')

  useEffect(() => {
    getStatsEmploye()
      .then(stats => {
        setSimulations(stats.dernieresSimulations || [])
      })
      .catch(console.error)
      .finally(() => setChargement(false))
  }, [])

  const simulationsFiltrees = filtreDate
    ? simulations.filter(s => s.date.includes(filtreDate))
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
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <label style={{ fontSize: '14px', fontWeight: 500, color: '#555' }}>
              Filtrer par date :
            </label>
            <input
              type="text"
              placeholder="Ex: 10/07/2026"
              className="form-control"
              style={{ maxWidth: '200px' }}
              value={filtreDate}
              onChange={(e) => setFiltreDate(e.target.value)}
            />
            {filtreDate && (
              <button
                className="btn btn-outline btn-sm"
                onClick={() => setFiltreDate('')}
              >
                Réinitialiser
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Liste des simulations */}
      {simulationsFiltrees.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#ccc" strokeWidth="1.5">
              <path d="M9 11l3 3L22 4"/>
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
            </svg>
            <p style={{ marginTop: '16px', fontSize: '15px', color: '#888' }}>
              {filtreDate 
                ? 'Aucune simulation trouvée pour cette date.'
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
                  <th>Taux consommation</th>
                  <th>Statut</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {simulationsFiltrees.map((sim, idx) => {
                  const isRecent = idx === 0
                  const tauxCouleur = sim.tauxConsommation >= 90 
                    ? 'text-danger' 
                    : sim.tauxConsommation >= 70 
                    ? 'text-warning' 
                    : 'text-success'

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
                        <span className={tauxCouleur} style={{ fontWeight: 600 }}>
                          {sim.tauxConsommation}%
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${
                          sim.tauxConsommation >= 90 
                            ? 'badge-danger' 
                            : sim.tauxConsommation >= 70 
                            ? 'badge-warning' 
                            : 'badge-success'
                        }`}>
                          {sim.tauxConsommation >= 90 
                            ? 'Attention' 
                            : sim.tauxConsommation >= 70 
                            ? 'Modéré' 
                            : 'Normal'}
                        </span>
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

      {/* Info supplémentaire */}
      <div className="alert alert-info" style={{ marginTop: '20px' }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
        Les simulations sont des estimations basées sur votre consommation actuelle. 
        Le montant réel de votre facture peut varier.
      </div>
    </div>
  )
}
