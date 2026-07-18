import { useState, useEffect, useRef } from 'react'
import { uploadBlocPdf, getHistoriquePublications } from '../../services/adminService'
import '../admin/Admin.css'

export default function PublicationPdf() {
  const [fichier, setFichier] = useState(null)
  const [type, setType] = useState('GLOBALE')
  const [periode, setPeriode] = useState('')
  const [progression, setProgression] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState(null)
  const [historique, setHistorique] = useState([])
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef()

  useEffect(() => { chargerHistorique() }, [])

  const chargerHistorique = () => {
    getHistoriquePublications().then(setHistorique).catch(console.error)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file?.type === 'application/pdf') setFichier(file)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!fichier || !periode) {
      setMessage({ type: 'danger', texte: 'Veuillez sélectionner un fichier PDF et une période.' })
      return
    }
    setUploading(true)
    setProgression(0)
    setMessage(null)
    try {
      const resultat = await uploadBlocPdf(fichier, type, periode, setProgression)
      setMessage({ type: 'success', texte: `Traitement terminé : ${resultat.facturesCreees} factures créées depuis ${resultat.pages} pages.` })
      setFichier(null)
      setPeriode('')
      chargerHistorique()
    } catch {
      setMessage({ type: 'danger', texte: "Erreur lors de l'upload. Réessayez." })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1 className="page-title">Publication des factures PDF</h1>
        <p className="text-muted">Uploadez les blocs PDF mensuels pour les découper et les publier automatiquement.</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Nouveau bloc PDF</h2>
        </div>

        {message && <div className={`alert alert-${message.type}`}>{message.texte}</div>}

        <form onSubmit={handleSubmit}>
          <div className="filtres-grid" style={{ marginBottom: 20 }}>
            <div className="form-group">
              <label className="form-label">Type de facture</label>
              <select className="form-control" value={type} onChange={e => setType(e.target.value)}>
                <option value="GLOBALE">Factures globales</option>
                <option value="SOMMAIRE">Factures sommaires</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Période (mois de facturation)</label>
              <input type="month" className="form-control" value={periode} onChange={e => setPeriode(e.target.value)} required />
            </div>
          </div>

          <div
            className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
            onClick={() => fileInputRef.current.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            <div className="upload-icon">PDF</div>
            {fichier ? (
              <><h3>{fichier.name}</h3><p>{(fichier.size / 1024 / 1024).toFixed(2)} MB</p></>
            ) : (
              <><h3>Glissez-déposez votre fichier PDF ici</h3><p>ou cliquez pour sélectionner un fichier</p></>
            )}
          </div>
          <input ref={fileInputRef} type="file" accept="application/pdf" style={{ display: 'none' }} onChange={e => setFichier(e.target.files[0])} />

          {uploading && (
            <div style={{ marginTop: 16 }}>
              <div className="flex-between" style={{ marginBottom: 4 }}>
                <span className="text-muted">Upload en cours...</span>
                <span className="text-orange"><strong>{progression}%</strong></span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progression}%` }}></div>
              </div>
              <p className="text-muted" style={{ marginTop: 8, fontSize: 12 }}>
                Le découpage automatique des factures démarrera après l'upload.
              </p>
            </div>
          )}

          <div style={{ marginTop: 20 }}>
            <button type="submit" className="btn btn-primary" disabled={uploading || !fichier}>
              {uploading
                ? <><div className="spinner" style={{ width: 16, height: 16 }}></div> Traitement...</>
                : 'Publier et découper'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Historique des publications</h2>
        </div>
        {historique.length === 0 ? (
          <div className="empty-state"><p>Aucune publication enregistrée.</p></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr><th>Date</th><th>Type</th><th>Période</th><th>Fichier</th><th>Factures créées</th><th>Statut</th></tr>
              </thead>
              <tbody>
                {historique.map((pub) => (
                  <tr key={pub.id}>
                    <td>{pub.datePublication}</td>
                    <td><span className={`badge ${pub.type === 'GLOBALE' ? 'badge-info' : 'badge-success'}`}>{pub.type}</span></td>
                    <td>{pub.periode}</td>
                    <td>{pub.nomFichier}</td>
                    <td><strong>{pub.facturesCreees}</strong></td>
                    <td>
                      <span className={`badge ${pub.statut === 'SUCCES' ? 'badge-success' : 'badge-danger'}`}>
                        {pub.statut === 'SUCCES' ? 'Succès' : 'Erreur'}
                      </span>
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
