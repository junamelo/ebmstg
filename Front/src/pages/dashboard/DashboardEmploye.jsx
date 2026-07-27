import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { getFactures } from '../../services/factureService'
import { getStatsEmploye } from '../../services/adminService'
import './Dashboard.css'

export default function DashboardEmploye() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [factures, setFactures] = useState([])
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    Promise.all([getStatsEmploye(), getFactures({})])
      .then(([s, f]) => { setStats(s); setFactures(f.slice(0, 3)) })
      .catch(console.error)
      .finally(() => setChargement(false))
  }, [])

  if (chargement) {
    return <div className="loading-overlay"><div className="spinner"></div><span>Chargement...</span></div>
  }

  if (!stats) {
    return <div className="loading-overlay"><div className="spinner"></div><span>Erreur de chargement des données...</span></div>
  }

  return (
    <div className="dashboard">
      {/* Hero card Employé — accent bleu */}
      <div className="hero-card hero-card--employe">
        <div className="hero-card__left">
          <div className="hero-card__role">Espace Employé</div>
          <h1 className="hero-card__greeting">Bonjour, {user?.prenom} 👋</h1>
        </div>
      </div>

      <div className="card">
        <div className="card-header flex-between">
          <h2 className="card-title">Historique de mes simulations</h2>
          <div className="card-header-actions">
            <Link to="/simulation/historique" className="btn btn-outline btn-sm">Voir tout</Link>
            <Link to="/simulation" className="btn btn-primary btn-sm">Nouvelle simulation</Link>
          </div>
        </div>
        {stats?.dernieresSimulations && stats.dernieresSimulations.length > 0 ? (
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
                {stats.dernieresSimulations.map((sim, idx) => (
                  <tr key={idx}>
                    <td>{sim.date}</td>
                    <td className="text-orange"><strong>{sim.montant.toLocaleString('fr-FR')} FCFA</strong></td>
                    <td><button className="btn btn-secondary btn-sm">Voir détails</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <p>Aucune simulation effectuée récemment.</p>
            <Link to="/simulation" className="btn btn-primary btn-sm">Faire ma première simulation</Link>
          </div>
        )}
      </div>

      <div className="dashboard-actions">
        <Link to="/factures" className="action-card action-primary">
          <div>
            <strong>Voir ma facture</strong>
            <p>Consultez et téléchargez votre dernière facture</p>
          </div>
          <span className="action-arrow">→</span>
        </Link>
        <Link to="/simulation" className="action-card action-secondary">
          <div>
            <strong>Simuler ma facturation</strong>
            <p>Estimez votre prochaine facture avant la fin du cycle</p>
          </div>
          <span className="action-arrow">→</span>
        </Link>
      </div>
    </div>
  )
}


