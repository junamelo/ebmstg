import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getStatsAgentFacturation } from '../../services/adminService'
import './Dashboard.css'

function AlerteCard({ titre, count, type }) {
  const couleurs = {
    danger: 'var(--moov-danger)',
    warning: 'var(--moov-warning)',
    info: 'var(--moov-blue)'
  }

  return (
    <div className="alerte-card" style={{ borderLeftColor: couleurs[type] }}>
      <div className="alerte-count" style={{ color: couleurs[type] }}>{count}</div>
      <div className="alerte-text">{titre}</div>
    </div>
  )
}

export default function DashboardAgentFacturation() {
  const [stats, setStats] = useState(null)
  const [chargement, setChargement] = useState(true)

  useEffect(() => {
    getStatsAgentFacturation()
      .then(setStats)
      .catch(console.error)
      .finally(() => setChargement(false))
  }, [])

  if (chargement) {
    return <div className="loading-overlay"><div className="spinner"></div><span>Chargement...</span></div>
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-greeting">Tableau de bord — Agent Facturation</h1>
          <p className="text-muted">Gestion des publications et suivi opérationnel</p>
        </div>
        <div className="header-date">
          {new Date().toLocaleDateString('fr-FR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </div>
      </div>

      <div className="section-title">Alertes et anomalies</div>
      <div className="alertes-grid">
        <AlerteCard
          titre="Factures non publiées"
          count={stats.facturesNonPubliees}
          type={stats.facturesNonPubliees > 0 ? 'danger' : 'info'}
        />
        <AlerteCard
          titre="Erreurs de découpage PDF"
          count={stats.erreursDecoupage}
          type={stats.erreursDecoupage > 0 ? 'danger' : 'info'}
        />
        <AlerteCard
          titre="Lignes sans forfait"
          count={stats.lignesSansForfait}
          type={stats.lignesSansForfait > 0 ? 'warning' : 'info'}
        />
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Services actifs et tarifs</h2>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Service</th>
                <th>Tarif unitaire</th>
                <th>Lignes actives</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {stats.servicesActifs.map((service, idx) => (
                <tr key={idx}>
                  <td><strong>{service.nom}</strong></td>
                  <td>{service.tarif.toLocaleString('fr-FR')} FCFA</td>
                  <td>{service.nbLignes.toLocaleString('fr-FR')}</td>
                  <td>
                    <span className="badge badge-success">Actif</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-muted" style={{ marginTop: 12, fontSize: 12 }}>
          Source : Table Tarif + Package
        </p>
      </div>

      <div className="card">
        <div className="card-header flex-between">
          <h2 className="card-title">Historique des publications</h2>
          <Link to="/admin/publication" className="btn btn-outline btn-sm">Voir tout</Link>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Période</th>
                <th>Factures générées</th>
                <th>Statut</th>
                <th>Rapport</th>
              </tr>
            </thead>
            <tbody>
              {stats.historiquePublications.map((pub, idx) => (
                <tr key={idx}>
                  <td>{pub.date}</td>
                  <td><strong>{pub.periode}</strong></td>
                  <td>{pub.nbFactures.toLocaleString('fr-FR')}</td>
                  <td>
                    <span className={`badge ${
                      pub.statut === 'TRAITEE' ? 'badge-success' :
                      pub.statut === 'EN_COURS' ? 'badge-warning' :
                      'badge-danger'
                    }`}>
                      {pub.statut === 'TRAITEE' ? 'Traitée' : pub.statut === 'EN_COURS' ? 'En cours' : 'Erreur'}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-secondary btn-sm">Voir le rapport</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="action-banner" style={{ background: 'linear-gradient(135deg, #002a7a, #003087)' }}>
        <div className="simulation-banner-content">
          <div>
            <strong style={{ color: 'white' }}>Publier une nouvelle facture</strong>
            <p style={{ color: 'rgba(255,255,255,0.8)' }}>Uploadez le bloc PDF et générez les factures individuelles</p>
          </div>
        </div>
        <Link to="/admin/publication" className="btn btn-primary">Nouvelle publication</Link>
      </div>
    </div>
  )
}
