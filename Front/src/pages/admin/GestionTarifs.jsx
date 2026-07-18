import { useState, useEffect } from 'react'
import { getTarifs, creerTarif, desactiverTarif } from '../../services/adminService'
import './Admin.css'

export default function GestionTarifs() {
  const [tarifs, setTarifs] = useState([])
  const [chargement, setChargement] = useState(true)
  const [formOuvert, setFormOuvert] = useState(false)
  const [message, setMessage] = useState(null)
  const [form, setForm] = useState({ nom: '', prixParMinute: '', prixParSms: '', prixParGo: '' })

  useEffect(() => { chargerTarifs() }, [])

  const chargerTarifs = () => {
    getTarifs().then(setTarifs).catch(console.error).finally(() => setChargement(false))
  }

  const tarifActif = tarifs.find(t => t.estActif)

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await creerTarif({
        nom: form.nom,
        prixParMinute: parseFloat(form.prixParMinute),
        prixParSms: parseFloat(form.prixParSms),
        prixParGo: parseFloat(form.prixParGo),
      })
      setMessage({ type: 'success', texte: 'Nouvelle grille tarifaire créée et activée.' })
      setForm({ nom: '', prixParMinute: '', prixParSms: '', prixParGo: '' })
      setFormOuvert(false)
      chargerTarifs()
    } catch {
      setMessage({ type: 'danger', texte: 'Erreur lors de la création. Réessayez.' })
    }
  }

  const handleDesactiver = async (id) => {
    if (!window.confirm('Désactiver ce tarif ?')) return
    try {
      await desactiverTarif(id)
      chargerTarifs()
    } catch {
      setMessage({ type: 'danger', texte: 'Erreur lors de la désactivation.' })
    }
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1 className="page-title">Gestion des tarifs</h1>
        <p className="text-muted">Définissez les grilles tarifaires utilisées pour la simulation de facturation.</p>
      </div>

      {tarifActif && (
        <div className="tarif-actif-card">
          <div>
            <p style={{ opacity: 0.8, fontSize: 13, marginBottom: 4 }}>Tarif actif actuellement</p>
            <h2 style={{ fontSize: 20, fontWeight: 700 }}>{tarifActif.nom}</h2>
          </div>
          <div className="tarif-actif-values">
            <div className="tarif-value-item">
              <span>Appels</span>
              <strong>{tarifActif.prixParMinute?.toLocaleString('fr-FR')} F/min</strong>
            </div>
            <div className="tarif-value-item">
              <span>SMS</span>
              <strong>{tarifActif.prixParSms?.toLocaleString('fr-FR')} F/SMS</strong>
            </div>
            <div className="tarif-value-item">
              <span>Data</span>
              <strong>{tarifActif.prixParGo?.toLocaleString('fr-FR')} F/Go</strong>
            </div>
          </div>
        </div>
      )}

      {message && <div className={`alert alert-${message.type}`}>{message.texte}</div>}

      <div className="flex-between">
        <h2 style={{ fontSize: 18, color: 'var(--moov-blue)' }}>Historique des grilles</h2>
        <button className="btn btn-primary" onClick={() => setFormOuvert(!formOuvert)}>
          {formOuvert ? 'Annuler' : '+ Nouvelle grille tarifaire'}
        </button>
      </div>

      {formOuvert && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Nouvelle grille tarifaire</h3>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="filtres-grid">
              <div className="form-group">
                <label className="form-label">Nom de la grille</label>
                <input type="text" className="form-control" placeholder="Ex: Tarif Juin 2026"
                  value={form.nom} onChange={e => setForm({ ...form, nom: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Prix par minute d'appel (FCFA)</label>
                <input type="number" className="form-control" placeholder="Ex: 25" min="0" step="0.01"
                  value={form.prixParMinute} onChange={e => setForm({ ...form, prixParMinute: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Prix par SMS (FCFA)</label>
                <input type="number" className="form-control" placeholder="Ex: 10" min="0" step="0.01"
                  value={form.prixParSms} onChange={e => setForm({ ...form, prixParSms: e.target.value })} required />
              </div>
              <div className="form-group">
                <label className="form-label">Prix par Go de data (FCFA)</label>
                <input type="number" className="form-control" placeholder="Ex: 2000" min="0" step="1"
                  value={form.prixParGo} onChange={e => setForm({ ...form, prixParGo: e.target.value })} required />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" style={{ marginTop: 8 }}>
              Créer et activer cette grille
            </button>
          </form>
        </div>
      )}

      <div className="card">
        {chargement ? (
          <div className="loading-overlay"><div className="spinner"></div></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Nom</th><th>Prix/min appel</th><th>Prix/SMS</th><th>Prix/Go</th>
                  <th>Date application</th><th>Statut</th><th>Action</th>
                </tr>
              </thead>
              <tbody>
                {tarifs.map((tarif) => (
                  <tr key={tarif.id}>
                    <td><strong>{tarif.nom}</strong></td>
                    <td>{tarif.prixParMinute?.toLocaleString('fr-FR')} F</td>
                    <td>{tarif.prixParSms?.toLocaleString('fr-FR')} F</td>
                    <td>{tarif.prixParGo?.toLocaleString('fr-FR')} F</td>
                    <td>{tarif.dateApplication}</td>
                    <td>
                      {tarif.estActif
                        ? <span className="badge badge-success">Actif</span>
                        : <span className="badge">Inactif</span>}
                    </td>
                    <td>
                      {tarif.estActif && (
                        <button className="btn btn-danger btn-sm" onClick={() => handleDesactiver(tarif.id)}>
                          Désactiver
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
