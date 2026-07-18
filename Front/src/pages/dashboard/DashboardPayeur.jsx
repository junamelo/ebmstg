import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { getFactures } from '../../services/factureService'
import { getStatsPayeur } from '../../services/adminService'
import illustrationPayeur from '../../assets/illustration-payeur.png'
import './Dashboard.css'

function BarreProgression({ valeur, couleur = 'var(--moov-orange)', label, detail }) {
  const pct = Math.min(valeur, 100)
  return (
    <div className="barre-kpi">
      <div className="barre-kpi-header">
        <span>{label}</span>
        <strong style={{ color: couleur }}>{valeur.toFixed(1)} %</strong>
      </div>
      <div className="barre-kpi-track">
        <div className="barre-kpi-fill" style={{ width: `${pct}%`, backgroundColor: couleur }} />
      </div>
      {detail && <span className="barre-kpi-detail">{detail}</span>}
    </div>
  )
}

function KpiCard({ label, value, tendance, sub, couleur }) {
  const positif = tendance >= 0
  return (
    <div className="kpi-card" style={{ borderLeftColor: couleur }}>
      <div className="kpi-body">
        <span className="kpi-label">{label}</span>
        <span className="kpi-value">{value}</span>
        {tendance !== undefined && (
          <span className="kpi-sub" style={{ color: positif ? 'var(--moov-danger)' : 'var(--moov-success)' }}>
            {positif ? '▲' : '▼'} {Math.abs(tendance).toFixed(1)} % vs mois précédent
          </span>
        )}
        {sub && <span className="kpi-sub">{sub}</span>}
      </div>
    </div>
  )
}

export default function DashboardPayeur() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [factures, setFactures] = useState([])
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    Promise.all([getStatsPayeur(), getFactures({})])
      .then(([s, f]) => { setStats(s); setFactures(f.slice(0, 5)) })
      .catch(console.error)
      .finally(() => setChargement(false))
  }, [])

  if (chargement) {
    return <div className="loading-overlay"><div className="spinner"></div><span>Chargement...</span></div>
  }

  return (
    <div className="dashboard">
      {/* Hero card Payeur — accent orange */}
      <div className="hero-card hero-card--payeur">
        <div className="hero-card__left">
          <div className="hero-card__role">Espace Entreprise</div>
          <h1 className="hero-card__greeting">Bonjour, {user?.prenom} 👋</h1>
          <p className="hero-card__sub">
            <strong>{user?.raisonSociale}</strong> · Contrat {user?.numeroContrat}
          </p>
          <div className="hero-card__badges">
            <span className="hero-card__badge hero-card__badge--success">
              ● {stats.nombreLignesActives} lignes actives
            </span>
          </div>
          <div className="hero-card__montant-inline">
            <Link to="/factures" className="hero-card__cta">Voir mes factures →</Link>
          </div>
        </div>
        {/* Illustration */}
        <div className="hero-card__illustration">
          <img
            src={illustrationPayeur}
            alt="Illustration espace entreprise"
            className="hero-card__illustration-img"
          />
        </div>
      </div>

      <div className="section-title">Résumé du contrat</div>
      <div className="card">
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Numéro de contrat</span>
            <span className="info-value">{user?.numeroContrat}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Lignes actives</span>
            <span className="info-value">{stats.nombreLignesActives}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Catégorie</span>
            <span className="info-value">{stats.categorieClient || 'Non définie'}</span>
          </div>
        </div>
      </div>

      {/* Actions rapides — au-dessus de la consommation */}
      <div className="dashboard-actions">
        <Link to="/factures" className="action-card action-primary">
          <div>
            <strong>Factures sommaires</strong>
            <p>Consultez les factures individuelles par ligne</p>
          </div>
          <span className="action-arrow">→</span>
        </Link>
        <Link to="/simulation" className="action-card action-secondary">
          <div>
            <strong>Simuler</strong>
            <p>Estimez le montant prévisionnel de votre flotte</p>
          </div>
          <span className="action-arrow">→</span>
        </Link>
      </div>

      <div className="section-title">Répartition par ligne</div>
      <div className="card">
        <div className="card-header flex-between">
          <h2 className="card-title">Consommation des lignes</h2>
          <Link to="/factures" className="btn btn-outline btn-sm">Voir les factures sommaires</Link>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Ligne</th>
                <th>Utilisateur</th>
                <th>Forfait</th>
                <th>Montant TTC</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {stats.lignesDetail && stats.lignesDetail.slice(0, 5).map((ligne, idx) => (
                <tr key={idx}>
                  <td><strong>{ligne.msisdn}</strong></td>
                  <td>{ligne.utilisateur}</td>
                  <td>{ligne.forfait}</td>
                  <td className="text-orange"><strong>{ligne.montant.toLocaleString('fr-FR')} FCFA</strong></td>
                  <td>
                    <span className={`badge ${ligne.statut === 'ACTIF' ? 'badge-success' : 'badge-danger'}`}>
                      {ligne.statut}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {stats.lignesASurveiller && stats.lignesASurveiller.length > 0 && (
        <>
          <div className="section-title">Lignes à surveiller</div>
          <div className="card">
            <div className="alert alert-warning">
              <strong>{stats.lignesASurveiller.length} ligne(s)</strong> suspendue(s) ou en retard de paiement
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Ligne</th>
                    <th>Utilisateur</th>
                    <th>Problème</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.lignesASurveiller.map((ligne, idx) => (
                    <tr key={idx}>
                      <td><strong>{ligne.msisdn}</strong></td>
                      <td>{ligne.utilisateur}</td>
                      <td>
                        <span className="badge badge-danger">{ligne.probleme}</span>
                      </td>
                      <td>
                        <button className="btn btn-secondary btn-sm">Voir détails</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}



    </div>
  )
}
