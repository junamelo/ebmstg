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
  const [filtres, setFiltres] = useState({ cycle: '', periode: '' })
  const navigate = useNavigate()

  useEffect(() => {
    chargerFactures()
  }, [filtres])

  const chargerFactures = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (filtres.cycle) params.append('cycle', filtres.cycle)
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
          <label>Cycle</label>
          <select
            value={filtres.cycle}
            onChange={(e) => setFiltres({ ...filtres, cycle: e.target.value })}
          >
            <option value="">Tous les cycles</option>
            <option value="HYB">HYBRIDE</option>
            <option value="OP">OPEN (Postpayé)</option>
          </select>
        </div>

        <div className="filtre-group">
          <label>Période</label>
          <input
            type="month"
            value={filtres.periode}
            onChange={(e) => setFiltres({ ...filtres, periode: e.target.value })}
          />
        </div>

        <button className="btn-secondary" onClick={() => setFiltres({ cycle: '', periode: '' })}>
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
              {factures.map((facture) => (
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
      )}
    </div>
  )
}
