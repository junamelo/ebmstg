import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { getFactures } from '../../services/factureService'
import { getStatsEmploye } from '../../services/adminService'
import './Dashboard.css'

function JaugeCirculaire({ pourcentage, couleur, label, detail }) {
  const rayon = 32
  const circ = 2 * Math.PI * rayon
  const pct = Math.min(pourcentage, 100)
  const rempli = (pct / 100) * circ

  const getCouleur = () => {
    if (pct >= 90) return 'var(--moov-danger)'
    if (pct >= 70) return 'var(--moov-warning)'
    return couleur
  }

  return (
    <div className="jauge-employe">
      <svg width="80" height="80" viewBox="0 0 80 80">
        <circle cx="40" cy="40" r={rayon} fill="none" stroke="#e0e0e0" strokeWidth="7" />
        <circle
          cx="40" cy="40" r={rayon} fill="none"
          stroke={getCouleur()} strokeWidth="7"
          strokeDasharray={`${rempli} ${circ - rempli}`}
          strokeLinecap="round"
          transform="rotate(-90 40 40)"
        />
        <text x="40" y="50" textAnchor="middle" fontSize="13" fontWeight="700" fill="#1a1a1a">
          {pct.toFixed(0)}%
        </text>
      </svg>
      <span className="jauge-employe-label">{label}</span>
      <span className="jauge-employe-detail">{detail}</span>
    </div>
  )
}

function SoldeCard({ montant, joursRestants, dateFinCycle }) {
  const urgence = joursRestants <= 5
  return (
    <div className="solde-card">
      <div className="solde-montant-wrap">
        <span className="solde-label">Solde facture — mois en cours</span>
        <span className="solde-montant">{montant.toLocaleString('fr-FR')} FCFA</span>
        <span className="solde-source">Source : Table Invoice (type = SOMMAIRE)</span>
      </div>
      <div className={`cycle-badge ${urgence ? 'cycle-urgence' : ''}`}>
        <div>
          <strong>{joursRestants} jours</strong>
          <span>avant fin de cycle</span>
          <small>Clôture le {dateFinCycle}</small>
        </div>
      </div>
    </div>
  )
}

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

  const pctData  = (stats.dataConsomme / stats.dataInclus) * 100
  const pctAppel = (stats.minutesConsommees / stats.minutesIncluses) * 100
  const pctSms   = (stats.smsConsommes / stats.smsInclus) * 100

  return (
    <div className="dashboard">
      {/* Hero card Employé — accent bleu */}
      <div className="hero-card hero-card--employe">
        <div className="hero-card__left">
          <div className="hero-card__role">Espace Employé</div>
          <h1 className="hero-card__greeting">Bonjour, {user?.prenom} 👋</h1>
          <p className="hero-card__sub">
            Ligne <strong>{user?.numeroLigne}</strong> · {stats.forfaitSouscrit}
          </p>
          <div className="hero-card__badges">
            <span className={`hero-card__badge ${stats.statutLigne === 'ACTIF' ? 'hero-card__badge--success' : 'hero-card__badge--danger'}`}>
              {stats.statutLigne === 'ACTIF' ? '● Ligne active' : '● Ligne suspendue'}
            </span>
            <span className="hero-card__badge hero-card__badge--info">
              Cycle se termine le {stats.dateFinCycle}
            </span>
          </div>
        </div>
      </div>

      <div className="section-title">Ma ligne</div>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Informations de ma ligne</h2>
        </div>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Numéro MSISDN</span>
            <span className="info-value">{user?.numeroLigne}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Forfait souscrit</span>
            <span className="info-value">{stats.forfaitSouscrit}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Statut</span>
            <span className={`badge ${stats.statutLigne === 'ACTIF' ? 'badge-success' : 'badge-danger'}`}>
              {stats.statutLigne === 'ACTIF' ? 'Actif' : 'Suspendu'}
            </span>
          </div>
        </div>
        {stats.servicesActifs && stats.servicesActifs.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <strong style={{ fontSize: 14, color: '#555' }}>Services actifs :</strong>
            <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
              {stats.servicesActifs.map((service, idx) => (
                <span key={idx} className="badge badge-info">{service}</span>
              ))}
            </div>
          </div>
        )}
      </div>


      <div className="card">
        <div className="card-header flex-between">
          <h2 className="card-title">Historique de mes simulations</h2>
          <div className="card-header-actions">
            <Link to="/simulation/historique" className="btn btn-outline btn-sm">Voir tout</Link>
            <Link to="/simulation" className="btn btn-primary btn-sm">Nouvelle simulation</Link>
          </div>
        </div>
        {stats.dernieresSimulations && stats.dernieresSimulations.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Montant estimé</th>
                  <th>Taux consommation</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {stats.dernieresSimulations.map((sim, idx) => (
                  <tr key={idx}>
                    <td>{sim.date}</td>
                    <td className="text-orange"><strong>{sim.montant.toLocaleString('fr-FR')} FCFA</strong></td>
                    <td>{sim.tauxConsommation}%</td>
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
