import { useState, useEffect, useRef } from 'react'
import { uploadBlocPdf, getHistoriquePublications, getStatutTraitementPdf } from '../../services/adminService'
import '../admin/Admin.css'

const ACTIVE_PDF_JOB_KEY = 'moov_active_pdf_job'

export default function PublicationPdf() {
  const [fichier, setFichier] = useState(null)
  // Un fichier mensuel peut regrouper des lignes OP et HYB : aucun filtre cycle.
  const cycle = ''
  const [typeFacture, setTypeFacture] = useState('SOM')
  const [periodeDebut, setPeriodeDebut] = useState('')
  const [periodeFin, setPeriodeFin] = useState('')
  const [progression, setProgression] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState(null)
  const [historique, setHistorique] = useState([])
  const [dragOver, setDragOver] = useState(false)
  const [rapportTraitement, setRapportTraitement] = useState(null)
  const [traitement, setTraitement] = useState(null)
  const fileInputRef = useRef()

  useEffect(() => { 
    chargerHistorique()
    // Remplir automatiquement avec le mois actuel
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const debut = `${year}-${month}-01`
    const fin = new Date(year, now.getMonth() + 1, 0).toISOString().split('T')[0] // Dernier jour du mois
    setPeriodeDebut(debut)
    setPeriodeFin(fin)

    // Si la page est rechargée pendant un long découpage, reprendre le suivi
    // au lieu de laisser l'utilisateur sans information.
    try {
      const jobEnCours = JSON.parse(sessionStorage.getItem(ACTIVE_PDF_JOB_KEY) || 'null')
      if (jobEnCours?.id && !['TERMINE', 'ECHEC'].includes(jobEnCours.statut)) {
        setTraitement(jobEnCours)
      }
    } catch {
      sessionStorage.removeItem(ACTIVE_PDF_JOB_KEY)
    }
  }, [])

  const chargerHistorique = () => {
    getHistoriquePublications().then(setHistorique).catch(console.error)
  }

  const terminerTraitement = (resultat) => {
    const summary = resultat.summary || resultat
    const matching = resultat.matching || resultat.auto_match || {}
    const nbFichiers = summary.files_created || summary.total_blocks || 0
    const nbMatches = matching.successfully_matched ?? matching.matched ?? 0
    const nbAlreadyProcessed = matching.skipped_already_processed
      ?? matching.skipped?.length
      ?? matching.details?.skipped?.length
      ?? 0
    const nbErrors = matching.details?.errors?.length ?? matching.errors?.length ?? 0

    setMessage({
      type: nbErrors > 0 ? 'danger' : (nbAlreadyProcessed > 0 ? 'warning' : 'success'),
      texte: nbErrors > 0
        ? `Traitement termine avec ${nbErrors} erreur(s) : ${nbFichiers} PDF crees, ${nbMatches} factures mises a jour.`
        : nbAlreadyProcessed > 0
          ? `Attention : ${nbAlreadyProcessed} facture(s) etaient deja traitees. Aucun PDF n'a ete rattache a nouveau pour ces factures.`
          : `Traitement termine ! ${nbFichiers} PDF crees, ${nbMatches} factures mises a jour.`,
    })
    setRapportTraitement({
      ok: nbErrors === 0,
      warning: nbAlreadyProcessed > 0,
      summary,
      matching,
      warnings: resultat.warnings || [],
      split_errors: resultat.split_errors || [],
      errors_per_page: resultat.errors_per_page || [],
    })
    sessionStorage.removeItem(ACTIVE_PDF_JOB_KEY)
    chargerHistorique()
  }

  useEffect(() => {
    if (!traitement?.id || ['TERMINE', 'ECHEC'].includes(traitement.statut)) return undefined
    let annule = false
    const verifier = async () => {
      try {
        const etat = await getStatutTraitementPdf(traitement.id)
        if (annule) return
        setTraitement(etat)
        setProgression(etat.progression || 0)
        if (etat.statut === 'TERMINE') {
          terminerTraitement(etat.resultat || {})
        } else if (etat.statut === 'ECHEC') {
          const resultat = etat.resultat || {}
          const erreur = etat.erreur || resultat.error || 'Erreur lors du traitement du PDF.'
          setMessage({ type: 'danger', texte: `Erreur : ${erreur}` })
          setRapportTraitement({
            ok: false,
            warnings: resultat.warnings || [],
            split_errors: resultat.split_errors || [],
            errors_per_page: resultat.errors_per_page || [],
            error: erreur,
          })
          sessionStorage.removeItem(ACTIVE_PDF_JOB_KEY)
        }
      } catch (error) {
        if (!annule) {
          console.error('Impossible de suivre le traitement PDF :', error)
          setMessage({ type: 'danger', texte: 'Impossible de récupérer l’état du traitement. Actualisez la page : le traitement continue côté serveur.' })
        }
      }
    }
    verifier()
    const intervalle = window.setInterval(verifier, 2000)
    return () => { annule = true; window.clearInterval(intervalle) }
  }, [traitement?.id, traitement?.statut])

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file?.type === 'application/pdf') setFichier(file)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!fichier || !periodeDebut || !periodeFin) {
      setMessage({ type: 'danger', texte: 'Veuillez sélectionner un fichier PDF et définir la période.' })
      return
    }
    
    setUploading(true)
    setProgression(0)
    setMessage(null)
    
    try {
      const resultat = await uploadBlocPdf(fichier, cycle, periodeDebut, periodeFin, setProgression, typeFacture)
      if (resultat.job?.id) {
        setTraitement(resultat.job)
        sessionStorage.setItem(ACTIVE_PDF_JOB_KEY, JSON.stringify(resultat.job))
        setMessage({ type: 'info', texte: 'PDF envoyÃ©. DÃ©coupage et rapprochement en attente du worker...' })
        setRapportTraitement(null)
        setFichier(null)
        return
      }
      
      // Adapter le message selon la réponse du backend Django
      // Le backend retourne les compteurs dans `summary` et `matching`.
      // L'ancien code lisait uniquement des clés à la racine, d'où les 0 affichés.
      const summary = resultat.summary || resultat
      const matching = resultat.matching || resultat.auto_match || {}
      const nbFichiers = summary.files_created || summary.total_blocks || 0
      const nbMatches = matching.successfully_matched ?? matching.matched ?? 0
      const nbAlreadyProcessed = matching.skipped_already_processed
        ?? matching.skipped?.length
        ?? matching.details?.skipped?.length
        ?? 0
      const nbErrors = matching.details?.errors?.length
        ?? matching.errors?.length
        ?? 0
      
      setMessage({ 
        type: 'success', 
        texte: `✅ Traitement terminé ! ${nbFichiers} PDF créés, ${nbMatches} factures mises à jour${nbAlreadyProcessed > 0 ? `, ${nbAlreadyProcessed} déjà traitées` : ''}${nbErrors > 0 ? `, ${nbErrors} erreurs` : ''}.` 
      })

      setRapportTraitement({
        ok: true,
        summary: summary,
        matching: matching,
        warnings: resultat.warnings || [],
        split_errors: resultat.split_errors || [],
        errors_per_page: resultat.errors_per_page || []
      })
      
      setFichier(null)
      chargerHistorique()
      
    } catch (error) {
      console.error('Erreur upload:', error)
      const errorMsg = error.response?.data?.error
        || (error.response?.status === 401
          ? 'Votre session a expiré. Veuillez vous reconnecter avant de publier.'
          : null)
        || (error.response?.status === 403
          ? 'Votre compte ne possède pas les droits de publication.'
          : null)
        || (error.code === 'ERR_NETWORK'
          ? 'Le serveur Django est inaccessible. Vérifiez qu’il est démarré sur le port 8000.'
          : null)
        || error.message
        || "Erreur lors de l'upload"
      setMessage({ type: 'danger', texte: `❌ ${errorMsg}` })
      setRapportTraitement({
        ok: false,
        warnings: error.response?.data?.warnings || [],
        split_errors: error.response?.data?.split_errors || [],
        errors_per_page: error.response?.data?.errors_per_page || [],
        error: errorMsg
      })
    } finally {
      setUploading(false)
      setProgression(0)
    }
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1 className="page-title">Publication des factures PDF</h1>
        <p className="text-muted">Uploadez les gros PDFs mensuels pour découpage automatique et matching avec les factures.</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Nouveau bloc PDF</h2>
        </div>

        {message && <div className={`alert alert-${message.type}`}>{message.texte}</div>}

        {rapportTraitement?.ok && !rapportTraitement?.warning && (
          <div className="alert" style={{ background: '#dcfce7', border: '1px solid #86efac', color: '#166534' }}>
            <strong>🟢 Découpage réussi.</strong>
            <span style={{ marginLeft: 8 }}>
              {rapportTraitement.summary?.files_created || 0} fichiers générés, {rapportTraitement.matching?.successfully_matched || 0} factures mises à jour.
            </span>
          </div>
        )}

        {rapportTraitement?.ok && rapportTraitement?.warning && (
          <div className="alert alert-warning">
            <strong>Attention : certaines factures etaient deja traitees.</strong>
            <span style={{ marginLeft: 8 }}>Elles ont ete ignorees afin d'eviter une double publication.</span>
          </div>
        )}

        {!rapportTraitement?.ok && rapportTraitement && (
          <div className="alert" style={{ background: '#fef2f2', border: '1px solid #fca5a5', color: '#b91c1c' }}>
            <strong>⚠️ Problème pendant le découpage/matching.</strong>
            <p style={{ marginTop: 6 }}>{rapportTraitement.error || 'Certaines factures n\'ont pas pu être traitées automatiquement.'}</p>
          </div>
        )}

        {(rapportTraitement?.warnings?.length > 0 || rapportTraitement?.split_errors?.length > 0 || rapportTraitement?.errors_per_page?.length > 0) && (
          <div className="alert" style={{ background: '#fef2f2', border: '1px solid #fca5a5', color: '#b91c1c' }}>
            <strong>⚠️ Détails des avertissements</strong>
            <ul style={{ marginTop: 8, paddingLeft: 18 }}>
              {rapportTraitement.warnings?.slice(0, 5).map((w, i) => <li key={`w-${i}`}>{String(w)}</li>)}
              {rapportTraitement.split_errors?.slice(0, 5).map((w, i) => <li key={`s-${i}`}>{String(w)}</li>)}
              {rapportTraitement.errors_per_page?.slice(0, 5).map((w, i) => <li key={`p-${i}`}>{typeof w === 'string' ? w : JSON.stringify(w)}</li>)}
            </ul>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="filtres-grid" style={{ marginBottom: 20 }}>
            <div className="form-group">
              <label className="form-label">Type de facture</label>
              <select className="form-control" value={typeFacture} onChange={e => setTypeFacture(e.target.value)}>
                <option value="SOM">Sommaire (SOM) — une facture par ligne</option>
                <option value="GLO">Globale (GLO) — une facture par entreprise</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Période - Début</label>
              <input 
                type="date" 
                className="form-control" 
                value={periodeDebut} 
                onChange={e => setPeriodeDebut(e.target.value)} 
                required 
              />
            </div>
            <div className="form-group">
              <label className="form-label">Période - Fin</label>
              <input 
                type="date" 
                className="form-control" 
                value={periodeFin} 
                onChange={e => setPeriodeFin(e.target.value)} 
                required 
              />
            </div>
          </div>

          <div
            className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
            onClick={() => fileInputRef.current.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            <div className="upload-icon">📄</div>
            {fichier ? (
              <>
                <h3>✅ {fichier.name}</h3>
                <p>{(fichier.size / 1024 / 1024).toFixed(2)} MB</p>
                <p className="text-muted">Le système va automatiquement découper ce PDF et matcher avec les factures</p>
              </>
            ) : (
              <>
                <h3>Glissez-déposez votre gros PDF ici</h3>
                <p>ou cliquez pour sélectionner un fichier</p>
                <p className="text-muted">Format accepté : PDF jusqu'à 200 MB</p>
              </>
            )}
          </div>
          <input ref={fileInputRef} type="file" accept="application/pdf" style={{ display: 'none' }} onChange={e => setFichier(e.target.files[0])} />

          {(uploading || (traitement && !['TERMINE', 'ECHEC'].includes(traitement.statut))) && (
            <div style={{ marginTop: 16 }}>
              {!uploading && (
                <p className="text-muted" style={{ marginBottom: 8, fontSize: 12 }}>
                  Analyse du PDF en arrière-plan : cette étape peut prendre plusieurs minutes pour un gros fichier. Vous pouvez actualiser cette page, le suivi reprendra automatiquement.
                </p>
              )}
              <div className="flex-between" style={{ marginBottom: 4 }}>
                <span className="text-muted">
                  {progression < 100 ? 'Upload en cours...' : 'Découpage et matching en cours...'}
                </span>
                <span className="text-orange"><strong>{progression}%</strong></span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progression}%` }}></div>
              </div>
              <p className="text-muted" style={{ marginTop: 8, fontSize: 12 }}>
                {progression < 100 
                  ? 'Le découpage automatique démarrera après l\'upload.'
                  : 'Analyse du PDF et matching avec les factures existantes...'
                }
              </p>
            </div>
          )}

          <div style={{ marginTop: 20 }}>
            <button type="submit" className="btn btn-primary" disabled={uploading || (traitement && !['TERMINE', 'ECHEC'].includes(traitement.statut)) || !fichier}>
              {uploading || (traitement && !['TERMINE', 'ECHEC'].includes(traitement.statut))
                ? <><div className="spinner" style={{ width: 16, height: 16 }}></div> Traitement...</>
                : '🚀 Publier et découper automatiquement'}
            </button>
          </div>
        </form>
      </div>

      <div className="card publication-history-card">
        <div className="card-header publication-history-header">
          <h2 className="card-title">Historique des publications</h2>
        </div>
        {historique.length === 0 ? (
          <div className="empty-state"><p>Aucune publication enregistrée.</p></div>
        ) : (
          <div className="table-container publication-history-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Cycle</th>
                  <th>Période</th>
                  <th>Agent</th>
                  <th>Lignes traitées</th>
                  <th>Statut</th>
                </tr>
              </thead>
              <tbody>
                {historique.map((pub) => (
                  <tr key={pub.id}>
                    <td>{new Date(pub.date_publication || pub.date_creation).toLocaleDateString('fr-FR')}</td>
                    <td>
                      <span className={`badge ${pub.cycle_facturation === 'HYB' ? 'badge-info' : 'badge-success'}`}>
                        {pub.cycle_facturation}
                      </span>
                    </td>
                    <td>{pub.periode_debut} - {pub.periode_fin}</td>
                    <td>{pub.agent_name || 'Système'}</td>
                    <td><strong>{pub.nombre_lignes_traitees || 0}</strong></td>
                    <td>
                      <span className={`badge ${pub.statut === 'PUBLIEE' ? 'badge-success' : 'badge-warning'}`}>
                        {pub.statut === 'PUBLIEE' ? 'Publié' : pub.statut}
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
