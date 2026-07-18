import { useState } from 'react'
import './PdfViewer.css'

/**
 * Composant d'aperçu PDF avant téléchargement
 * Utilise l'iframe natif du navigateur pour afficher le PDF
 * @param {string} url - URL du PDF à afficher
 * @param {string} numeroFacture - Numéro de la facture pour le bouton télécharger
 * @param {function} onClose - Fermer la modale
 * @param {function} onTelecharger - Déclencher le téléchargement
 */
export default function PdfViewer({ url, numeroFacture, onClose, onTelecharger }) {
  const [chargement, setChargement] = useState(true)

  return (
    <div className="pdf-modal-overlay" onClick={onClose}>
      <div className="pdf-modal" onClick={(e) => e.stopPropagation()}>
        {/* En-tête */}
        <div className="pdf-modal-header">
          <div className="pdf-modal-title">
            <span>📄</span>
            <span>Facture N° {numeroFacture}</span>
          </div>
          <div className="pdf-modal-actions">
            <button
              className="btn btn-primary btn-sm"
              onClick={onTelecharger}
            >
              ⬇ Télécharger
            </button>
            <button
              className="btn btn-outline btn-sm"
              onClick={onClose}
            >
              ✕ Fermer
            </button>
          </div>
        </div>

        {/* Contenu PDF */}
        <div className="pdf-modal-body">
          {chargement && (
            <div className="pdf-loading">
              <div className="spinner"></div>
              <span>Chargement du PDF...</span>
            </div>
          )}
          <iframe
            src={url}
            title={`Facture ${numeroFacture}`}
            className="pdf-iframe"
            onLoad={() => setChargement(false)}
            style={{ display: chargement ? 'none' : 'block' }}
          />
        </div>
      </div>
    </div>
  )
}
