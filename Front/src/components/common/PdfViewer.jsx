/**
 * PdfViewer — Aperçu et téléchargement de facture PDF
 *
 * Cause du bug "localhost n'autorise pas la connexion" :
 *   - L'ancien code utilisait `getFacturePdfUrl(id)` qui pointait sur
 *     `/api/billing/invoices/{id}/` (endpoint JSON, pas le fichier PDF)
 *     dans une <iframe>. Le navigateur ne peut pas charger une URL d'API
 *     JWT dans une iframe (pas d'entête Authorization possible).
 *
 * Solution : l'interface récupère le PDF via Axios (avec JWT), puis ouvre
 * un Blob local dans un nouvel onglet. Ainsi, l'endpoint sécurisé reçoit bien
 * l'en-tête Authorization et l'utilisateur ne voit jamais une page 401/403.
 */
export default function PdfViewer({ url, numeroFacture, onClose, onTelecharger, onApercu }) {
  const hasPdf = !!url

  const ouvrirNouvelOnglet = () => {
    if (hasPdf) onApercu?.()
  }

  return (
    <div className="pdf-modal-overlay" onClick={onClose}>
      <div className="pdf-modal" onClick={e => e.stopPropagation()}>
        {/* En-tête */}
        <div className="pdf-modal-header">
          <div className="pdf-modal-title">
            <span>📄</span>
            <span>Facture N° {numeroFacture}</span>
          </div>
          <div className="pdf-modal-actions">
            {hasPdf && (
              <>
                <button className="btn btn-primary btn-sm" onClick={ouvrirNouvelOnglet}>
                  🔍 Ouvrir dans un onglet
                </button>
                <button className="btn btn-primary btn-sm" onClick={onTelecharger}>
                  ⬇ Télécharger
                </button>
              </>
            )}
            <button className="btn btn-outline btn-sm" onClick={onClose}>
              ✕ Fermer
            </button>
          </div>
        </div>

        {/* Corps */}
        <div className="pdf-modal-body" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', gap: '16px', padding: '32px' }}>
          {hasPdf ? (
            <>
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#e05500" strokeWidth="1.5">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
              <p style={{ fontSize: 16, fontWeight: 600, color: '#111827' }}>Facture N° {numeroFacture}</p>
              <p style={{ fontSize: 14, color: '#6b7280', textAlign: 'center' }}>
                L'aperçu PDF s'ouvre dans un nouvel onglet pour garantir un affichage correct.
              </p>
              <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
                <button
                  onClick={ouvrirNouvelOnglet}
                  style={{ padding: '10px 24px', background: '#002a7a', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, fontSize: '14px' }}
                >
                  🔍 Voir le PDF
                </button>
                <button
                  onClick={onTelecharger}
                  style={{ padding: '10px 24px', background: '#e05500', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, fontSize: '14px' }}
                >
                  ⬇ Télécharger
                </button>
              </div>
            </>
          ) : (
            <>
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#d1d5db" strokeWidth="1.5">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="8" y1="13" x2="16" y2="13"/>
                <line x1="8" y1="17" x2="12" y2="17"/>
              </svg>
              <p style={{ fontSize: 16, fontWeight: 600, color: '#374151' }}>Aucun PDF disponible</p>
              <p style={{ fontSize: 14, color: '#9ca3af', textAlign: 'center' }}>
                Le fichier PDF de cette facture n'a pas encore été attaché.<br/>
                Contactez votre agent de facturation.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
