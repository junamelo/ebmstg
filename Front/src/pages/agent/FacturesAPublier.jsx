import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'
import './FacturesAPublier.css'

export default function FacturesAPublier() {
  const [factures, setFactures] = useState([])
  const [selection, setSelection] = useState([])
  const [stats, setStats] = useState({ total_factures: 0, montant_total: 0 })
  const [loading, setLoading] = useState(true)
  const [publishing, setPublishing] = useState(false)
  const [message, setMessage] = useState(null)
  const [filtres, setFiltres] = useState({ periode: '' })
  const [pageCourante, setPageCourante] = useState(1)
  const ITEMS_PAR_PAGE = 10
  const [notifMessage, setNotifMessage] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    chargerFactures()
  }, [filtres])

  const chargerFactures = async () => {
    try {
      setLoading(true)
      setPageCourante(1)
      const params = new URLSearchParams()
      if (filtres.periode) params.append('periode', filtres.periode)
      
      const response = await api.get(`/billing/invoices/factures_a_publier/?${params}`)
      setFactures(response.data.factures || [])
      setStats(response.data.stats || { total_factures: 0, montant_total: 0 })
      setSelection([])
    } catch (error) {
      console.error('Erreur chargement factures:', error)
      setMessage({ type: 'error', texte: 'Erreur lors du chargement des factures' })
    } finally {
      setLoading(false)
    }
  }

  const toggleSelection = (id) => {
    setSelection(prev =>
      prev.includes(id) ? prev.filter(fid => fid !== id) : [...prev, id]
    )
  }

  const toggleTout = () => {
    if (selection.length === factures.length) {
      setSelection([])
    } else {
      setSelection(factures.map(f => f.id))
    }
  }

  const publierSelection = async () => {
    if (selection.length === 0) {
      setMessage({ type: 'error', texte: 'Aucune facture sélectionnée' })
      return
    }

    const montantSelection = factures
      .filter(f => selection.includes(f.id))
      .reduce((sum, f) => sum + parseFloat(f.montant_ttc), 0)

    if (!window.confirm(
      `Publier ${selection.length} facture(s) pour un montant total de ${montantSelection.toLocaleString('fr-FR')} FCFA ?`
    )) {
      return
    }

    try {
      setPublishing(true)
      const response = await api.post('/billing/invoices/publier_masse/', {
        invoice_ids: selection
      })
      
      setMessage({
        type: 'success',
        texte: `✅ ${response.data.factures_publiees} facture(s) publiée(s) avec succès !`
      })
      
      // Recharger la liste
      setTimeout(() => {
        chargerFactures()
        setMessage(null)
      }, 2000)
      
    } catch (error) {
      console.error('Erreur publication:', error)
      setMessage({
        type: 'error',
        texte: error.response?.data?.error || 'Erreur lors de la publication'
      })
    } finally {
      setPublishing(false)
    }
  }

  const montantSelection = factures
    .filter(f => selection.includes(f.id))
    .reduce((sum, f) => sum + parseFloat(f.montant_ttc), 0)

  const nbPages = Math.ceil(factures.length / ITEMS_PAR_PAGE)
  const facturesPage = factures.slice(
    (pageCourante - 1) * ITEMS_PAR_PAGE,
    pageCourante * ITEMS_PAR_PAGE
  )

  const notifierSelection = () => {
    if (selection.length === 0) {
      setMessage({ type: 'error', texte: 'Sélectionnez au moins une facture.' })
      return
    }
    setNotifMessage(`📧 Notification (mail/SMS) prévue pour ${selection.length} facture(s) — fonctionnalité à implémenter.`)
    setTimeout(() => setNotifMessage(null), 4000)
  }

  return (
    <div className="factures-a-publier">
      <div className="page-header">
        <div className="header-left">
          <button className="btn-back" onClick={() => navigate('/agent/dashboard')}>
            <i className="ti ti-arrow-left"></i>
          </button>
          <div>
            <h1>Factures à publier</h1>
            <p className="subtitle">Factures validées prêtes pour publication</p>
          </div>
        </div>
      </div>

      {/* Filtres */}
      <div className="filtres-card">
        <div className="filtre-group">
          <label>Période</label>
          <input
            type="month"
            value={filtres.periode}
            onChange={(e) => setFiltres({ ...filtres, periode: e.target.value })}
          />
        </div>
        <button className="btn-secondary" onClick={() => setFiltres({ periode: '' })}>
          <i className="ti ti-x"></i>
          Réinitialiser
        </button>
      </div>

      {/* Statistiques */}
      <div className="stats-grid">
        <div className="stat-card">
          <i className="ti ti-file-invoice"></i>
          <div>
            <div className="stat-value">{stats.total_factures}</div>
            <div className="stat-label">Factures à publier</div>
          </div>
        </div>

        <div className="stat-card">
          <i className="ti ti-coin"></i>
          <div>
            <div className="stat-value">{stats.montant_total.toLocaleString('fr-FR')} FCFA</div>
            <div className="stat-label">Montant total</div>
          </div>
        </div>

        {selection.length > 0 && (
          <div className="stat-card stat-selection">
            <i className="ti ti-checkbox"></i>
            <div>
              <div className="stat-value">{selection.length} sélectionnée(s)</div>
              <div className="stat-label">{montantSelection.toLocaleString('fr-FR')} FCFA</div>
            </div>
          </div>
        )}
      </div>

      {/* Message */}
      {message && (
        <div className={`alert alert-${message.type}`}>
          {message.texte}
        </div>
      )}

      {/* Message notification */}
      {notifMessage && (
        <div className="alert alert-info">
          <i className="ti ti-mail"></i>
          {notifMessage}
        </div>
      )}

      {/* Actions */}
      {factures.length > 0 && (
        <div className="actions-bar">
          <label className="checkbox-wrapper">
            <input
              type="checkbox"
              checked={selection.length === factures.length}
              onChange={toggleTout}
            />
            <span>Tout sélectionner ({factures.length})</span>
          </label>

          <div className="actions-buttons">
            <button
              className="btn-secondary btn-notif"
              onClick={notifierSelection}
              disabled={selection.length === 0}
              title="Notifier par mail/SMS (bientôt disponible)"
            >
              <i className="ti ti-mail"></i>
              Notifier ({selection.length})
            </button>

            <button
              className="btn-primary btn-publish"
              onClick={publierSelection}
              disabled={selection.length === 0 || publishing}
            >
              {publishing ? (
                <>
                  <span className="spinner"></span>
                  Publication en cours...
                </>
              ) : (
                <>
                  <i className="ti ti-send"></i>
                  Publier la sélection ({selection.length})
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Liste des factures */}
      {loading ? (
        <div className="loading-state">
          <div className="spinner-large"></div>
          <p>Chargement des factures...</p>
        </div>
      ) : factures.length === 0 ? (
        <div className="empty-state">
          <i className="ti ti-inbox"></i>
          <h3>Aucune facture à publier</h3>
          <p>Toutes les factures validées ont déjà été publiées.</p>
        </div>
      ) : (
        <>
          <div className="factures-table">
            <table>
              <thead>
                <tr>
                  <th width="50">
                    <input
                      type="checkbox"
                      checked={selection.length === factures.length}
                      onChange={toggleTout}
                    />
                  </th>
                  <th>Numéro</th>
                  <th>Entreprise</th>
                  <th>Ligne</th>
                  <th>Période</th>
                  <th>Montant TTC</th>
                  <th>PDF</th>
                </tr>
              </thead>
              <tbody>
                {facturesPage.map((facture) => (
                  <tr
                    key={facture.id}
                    className={selection.includes(facture.id) ? 'selected' : ''}
                  >
                    <td>
                      <input
                        type="checkbox"
                        checked={selection.includes(facture.id)}
                        onChange={() => toggleSelection(facture.id)}
                      />
                    </td>
                    <td className="numero">{facture.numero_facture}</td>
                    <td>{facture.company_name}</td>
                    <td>
                      {facture.line_msisdn ? (
                        <span className="badge badge-som">{facture.line_msisdn}</span>
                      ) : (
                        <span className="badge badge-globale">Globale</span>
                      )}
                    </td>
                    <td>
                      {new Date(facture.periode_debut).toLocaleDateString('fr-FR', {
                        month: 'short',
                        year: 'numeric'
                      })}
                    </td>
                    <td className="montant">
                      {parseFloat(facture.montant_ttc).toLocaleString('fr-FR')} FCFA
                    </td>
                    <td>
                      {facture.fichier_pdf ? (
                        <span className="badge badge-success">
                          <i className="ti ti-file-check"></i>
                          Attaché
                        </span>
                      ) : (
                        <span className="badge badge-warning">
                          <i className="ti ti-file-off"></i>
                          Manquant
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {nbPages > 1 && (
            <div className="pagination-bar">
              <span className="pagination-info">
                Affichage {(pageCourante - 1) * ITEMS_PAR_PAGE + 1}–{Math.min(pageCourante * ITEMS_PAR_PAGE, factures.length)} sur <strong>{factures.length}</strong> facture(s)
              </span>
              <div className="pagination-controls">
                <button className="pagination-btn" disabled={pageCourante === 1} onClick={() => setPageCourante(p => p - 1)}>
                  ← Préc.
                </button>
                {Array.from({ length: nbPages }, (_, i) => i + 1).map(p => (
                  <button key={p} onClick={() => setPageCourante(p)}
                    className={`pagination-btn ${p === pageCourante ? 'active' : ''}`}>
                    {p}
                  </button>
                ))}
                <button className="pagination-btn" disabled={pageCourante === nbPages} onClick={() => setPageCourante(p => p + 1)}>
                  Suiv. →
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
