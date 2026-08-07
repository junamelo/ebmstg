import { useState, useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { getFactures, telechargerFacture, ouvrirApercuFacture } from '../../services/factureService'
import './Factures.css'

// ── Constantes ───────────────────────────────────────────────
const MOIS_NOMS = {
  '01': 'Janvier', '02': 'Février', '03': 'Mars',
  '04': 'Avril',   '05': 'Mai',     '06': 'Juin',
  '07': 'Juillet', '08': 'Août',    '09': 'Septembre',
  '10': 'Octobre', '11': 'Novembre','12': 'Décembre',
}

const TYPE_CONFIG = {
  GLOBALE:  { label: 'Globale',  icon: '📁', desc: 'Factures de toute la flotte', couleur: '#002a7a', bg: '#e8edf8' },
  SOMMAIRE: { label: 'Sommaire', icon: '📂', desc: 'Factures par ligne individuelle', couleur: '#e05500', bg: '#fff0e8' },
}

// ── Icônes ───────────────────────────────────────────────────
const IconFolder = ({ color = '#e05500', fill = 'none' }) => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
  </svg>
)

const IconChevron = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#bbb" strokeWidth="2.5">
    <polyline points="9 18 15 12 9 6"/>
  </svg>
)

const IconBack = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
    <path d="M19 12H5M12 5l-7 7 7 7"/>
  </svg>
)

// ── Breadcrumb ───────────────────────────────────────────────
function Breadcrumb({ items }) {
  return (
    <div className="explorer-breadcrumb">
      {items.map((item, idx) => (
        <span key={idx} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {idx > 0 && <span className="breadcrumb-sep">›</span>}
          {item.onClick ? (
            <button className="breadcrumb-item" onClick={item.onClick}>
              {item.label}
            </button>
          ) : (
            <span className="breadcrumb-item breadcrumb-item--active">{item.label}</span>
          )}
        </span>
      ))}
    </div>
  )
}

// ── Grille de dossiers ───────────────────────────────────────
function GrilleDossiers({ items }) {
  return (
    <div className="explorer-container">
      <div className="explorer-header">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#888" strokeWidth="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        <span>{items.length} élément{items.length > 1 ? 's' : ''}</span>
      </div>
      <div className="explorer-grid">
        {items.map((item, idx) => (
          <button key={idx} className="explorer-folder" onClick={item.onClick}>
            <div className="explorer-folder__icon" style={{ color: item.couleur || '#e05500' }}>
              <IconFolder color={item.couleur || '#e05500'} fill={item.bg || 'none'} />
            </div>
            <div className="explorer-folder__info">
              <span className="explorer-folder__name">{item.label}</span>
              {item.desc && <span className="explorer-folder__count">{item.desc}</span>}
            </div>
            <IconChevron />
          </button>
        ))}
      </div>
    </div>
  )
}

// ── Card facture ─────────────────────────────────────────────
function FactureCard({ facture }) {
  const isPaid = facture.statut === 'PAYEE'
  const isLate = facture.statut === 'EN_RETARD'
  const initiales = (facture.ligneOuFlotte || facture.numero).slice(0, 2).toUpperCase()
  const [jour, mois, annee] = (facture.dateEcheance || '').split('/')
  const echeance = annee ? new Date(`${annee}-${mois}-${jour}`) : null
  const diffJours = echeance ? Math.ceil((echeance - new Date()) / (1000 * 60 * 60 * 24)) : null

  return (
    <div className={`facture-card ${isLate ? 'facture-card--retard' : ''}`}>
      <div className="facture-card__header">
        <div className="facture-card__avatar"
          style={{ background: isPaid ? '#e8f5e9' : isLate ? '#fdecea' : '#e8edf8',
                   color:      isPaid ? '#2e7d32' : isLate ? '#c62828' : '#002a7a' }}>
          {initiales}
        </div>
        <span className="facture-card__nom">{facture.ligneOuFlotte || facture.numero}</span>
      </div>
      <div className="facture-card__divider" />
      <div className="facture-card__meta">
        <div className="facture-card__delai">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={diffJours < 0 ? '#e05500' : '#e09000'} strokeWidth="2">
            <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
          </svg>
          <span style={{ color: '#888', fontSize: 12 }}>
            {diffJours !== null
              ? diffJours < 0 ? `${Math.abs(diffJours)}j de retard`
              : diffJours === 0 ? "Aujourd'hui"
              : `${diffJours}j restants`
              : facture.dateEcheance}
          </span>
        </div>
        <div className="facture-card__montant">
          <strong>{facture.montantTTC?.toLocaleString('fr-FR')} FCFA</strong>
        </div>
      </div>
      <div className="facture-card__divider" />
      <div className="facture-card__details">
        <div className="facture-card__detail-row">
          <span className="facture-card__detail-label">N° :</span>
          <span className="facture-card__detail-val">{facture.numero}</span>
        </div>
        <div className="facture-card__detail-row">
          <span className="facture-card__detail-label">Émise :</span>
          <span className="facture-card__detail-val">{facture.dateEmission}</span>
        </div>
        <div className="facture-card__detail-row">
          <span className="facture-card__detail-label">Statut :</span>
          <span className={`facture-card__statut ${isPaid ? 'statut--paye' : isLate ? 'statut--retard' : 'statut--attente'}`}>
            {isPaid ? 'Payée' : isLate ? 'En retard' : 'En attente'}
          </span>
        </div>
      </div>
      <div className="facture-card__actions">
        <button className="facture-card__btn-view" onClick={() => ouvrirApercuFacture(facture.id, facture.numero)}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
          </svg>
          Aperçu
        </button>
        <button className="facture-card__btn-action" onClick={() => telechargerFacture(facture.id, facture.numero)}>
          Télécharger ▾
        </button>
      </div>
    </div>
  )
}

// ── Hook navigation explorateur ──────────────────────────────
function useExplorateur() {
  const [type, setType] = useState(null)       // 'GLOBALE' | 'SOMMAIRE' | null (payeur) | ignoré (employé)
  const [annee, setAnnee] = useState(null)
  const [mois, setMois] = useState(null)

  const reset = () => { setType(null); setAnnee(null); setMois(null) }
  const goType = (t) => { setType(t); setAnnee(null); setMois(null) }
  const goAnnee = (a) => { setAnnee(a); setMois(null) }
  const goMois = (m) => setMois(m)
  const backToType = () => { setAnnee(null); setMois(null) }
  const backToAnnee = () => setMois(null)

  return { type, annee, mois, reset, goType, goAnnee, goMois, backToType, backToAnnee }
}

// ── Page principale ──────────────────────────────────────────
export default function Factures() {
  const { isPayeur } = useAuth()
  const [toutesFactures, setToutesFactures] = useState([])
  const [chargement, setChargement] = useState(true)
  const nav = useExplorateur()
  
  // Pagination
  const [page, setPage] = useState(1)
  const ITEMS_PAR_PAGE = 12

  useEffect(() => {
    getFactures({})
      .then(setToutesFactures)
      .catch(console.error)
      .finally(() => setChargement(false))
  }, [])
  
  // Réinitialiser la page lors du changement de mois
  useEffect(() => {
    setPage(1)
  }, [nav.mois, nav.annee, nav.type])

  if (chargement) {
    return <div className="loading-overlay"><div className="spinner"></div><span>Chargement...</span></div>
  }

  // ── Données dérivées ─────────────────────────────────────────

  // Filtre selon le contexte de navigation
  const facturesFiltreesParType = isPayeur() && nav.type
    ? toutesFactures.filter(f => f.type === nav.type)
    : toutesFactures

  const anneesDisponibles = [...new Set(
    facturesFiltreesParType.map(f => f.periode?.split('-')[0]).filter(Boolean)
  )].sort((a, b) => b - a)

  const moisDisponibles = nav.annee
    ? [...new Set(
        facturesFiltreesParType
          .filter(f => f.periode?.startsWith(nav.annee))
          .map(f => f.periode?.split('-')[1])
          .filter(Boolean)
      )].sort()
    : []

  const facturesDuMois = (nav.annee && nav.mois)
    ? facturesFiltreesParType.filter(f => f.periode === `${nav.annee}-${nav.mois}`)
    : []
  
  // Pagination
  const totalFactures = facturesDuMois.length
  const totalPages = Math.ceil(totalFactures / ITEMS_PAR_PAGE)
  const indexDebut = (page - 1) * ITEMS_PAR_PAGE
  const indexFin = indexDebut + ITEMS_PAR_PAGE
  const facturesPaginees = facturesDuMois.slice(indexDebut, indexFin)

  const nbParType = (t) => toutesFactures.filter(f => f.type === t).length
  const nbParAnnee = (a) => facturesFiltreesParType.filter(f => f.periode?.startsWith(a)).length
  const nbParMois = (m) => facturesFiltreesParType.filter(f => f.periode === `${nav.annee}-${m}`).length

  // ── Breadcrumb dynamique ─────────────────────────────────────
  const breadcrumbItems = [
    { label: 'Mes factures', onClick: nav.reset },
    ...(isPayeur() && nav.type ? [{ label: TYPE_CONFIG[nav.type]?.label, onClick: nav.backToType }] : []),
    ...(nav.annee ? [{ label: nav.annee, onClick: nav.mois ? nav.backToAnnee : null }] : []),
    ...(nav.mois ? [{ label: MOIS_NOMS[nav.mois] }] : []),
  ]
  // Le dernier item n'est pas cliquable
  const breadcrumbFinal = breadcrumbItems.map((item, idx) => ({
    ...item,
    onClick: idx === breadcrumbItems.length - 1 ? null : item.onClick,
  }))

  // ── Niveau actuel ────────────────────────────────────────────
  const niveau =
    nav.mois ? 'factures'
    : nav.annee ? 'mois'
    : (isPayeur() && nav.type) ? 'annees'
    : isPayeur() ? 'type'
    : 'annees' // employé démarre aux années

  return (
    <div className="factures-page">
      <div className="page-header">
        <h1 className="page-title">Mes factures</h1>
        <p className="text-muted">{toutesFactures.length} facture(s) au total</p>
      </div>

      <Breadcrumb items={breadcrumbFinal} />

      {/* ── NIVEAU TYPE (Payeur seulement) ── */}
      {niveau === 'type' && (
        <GrilleDossiers items={[
          {
            label: 'Factures Globales',
            desc: `${nbParType('GLOBALE')} facture${nbParType('GLOBALE') > 1 ? 's' : ''} — flotte complète`,
            couleur: TYPE_CONFIG.GLOBALE.couleur,
            bg: TYPE_CONFIG.GLOBALE.bg,
            onClick: () => nav.goType('GLOBALE'),
          },
          {
            label: 'Factures Sommaires',
            desc: `${nbParType('SOMMAIRE')} facture${nbParType('SOMMAIRE') > 1 ? 's' : ''} — par ligne`,
            couleur: TYPE_CONFIG.SOMMAIRE.couleur,
            bg: TYPE_CONFIG.SOMMAIRE.bg,
            onClick: () => nav.goType('SOMMAIRE'),
          },
        ]} />
      )}

      {/* ── NIVEAU ANNÉES ── */}
      {niveau === 'annees' && (
        <>
          {isPayeur() && (
            <button className="explorer-back" onClick={nav.reset}>
              <IconBack /> Retour aux types
            </button>
          )}
          <GrilleDossiers items={anneesDisponibles.map(a => ({
            label: a,
            desc: `${nbParAnnee(a)} facture${nbParAnnee(a) > 1 ? 's' : ''}`,
            couleur: '#e05500',
            onClick: () => nav.goAnnee(a),
          }))} />
        </>
      )}

      {/* ── NIVEAU MOIS ── */}
      {niveau === 'mois' && (
        <>
          <button className="explorer-back" onClick={() => isPayeur() ? nav.backToType() : nav.reset()}>
            <IconBack /> Retour {isPayeur() ? `aux types` : 'aux années'}
          </button>
          {/* Si on vient d'une année, on affiche aussi le bouton retour aux années pour le payeur */}
          <GrilleDossiers items={moisDisponibles.map(m => ({
            label: MOIS_NOMS[m],
            desc: `${nbParMois(m)} facture${nbParMois(m) > 1 ? 's' : ''}`,
            couleur: '#002a7a',
            bg: '#e8edf8',
            onClick: () => nav.goMois(m),
          }))} />
        </>
      )}

      {/* ── NIVEAU FACTURES ── */}
      {niveau === 'factures' && (
        <>
          <button className="explorer-back" onClick={nav.backToAnnee}>
            <IconBack /> Retour à {nav.annee}
          </button>
          <div className="explorer-files-header">
            <div className="explorer-files-title">
              <IconFolder color="#002a7a" fill="#e8edf8" />
              <strong>{MOIS_NOMS[nav.mois]} {nav.annee}</strong>
              {isPayeur() && nav.type && (
                <span className="explorer-type-tag" style={{ background: TYPE_CONFIG[nav.type].bg, color: TYPE_CONFIG[nav.type].couleur }}>
                  {TYPE_CONFIG[nav.type].label}
                </span>
              )}
              <span className="explorer-files-count">{facturesDuMois.length} facture{facturesDuMois.length > 1 ? 's' : ''}</span>
            </div>
          </div>
          {facturesDuMois.length === 0 ? (
            <div className="card"><div className="empty-state"><p>Aucune facture pour cette période.</p></div></div>
          ) : (
            <>
              <div className="factures-grid">
                {facturesPaginees.map(f => (
                  <FactureCard key={f.id} facture={f} />
                ))}
              </div>
              
              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination-container">
                  <div className="pagination-info">
                    Affichage de {indexDebut + 1} à {Math.min(indexFin, totalFactures)} sur {totalFactures} facture{totalFactures > 1 ? 's' : ''}
                  </div>
                  <div className="pagination-controls">
                    <button
                      className="pagination-btn"
                      onClick={() => setPage(1)}
                      disabled={page === 1}
                      title="Première page"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M11 17l-5-5 5-5M18 17l-5-5 5-5"/>
                      </svg>
                    </button>
                    <button
                      className="pagination-btn"
                      onClick={() => setPage(page - 1)}
                      disabled={page === 1}
                      title="Page précédente"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M15 18l-6-6 6-6"/>
                      </svg>
                    </button>
                    
                    <div className="pagination-pages">
                      {[...Array(totalPages)].map((_, idx) => {
                        const pageNum = idx + 1
                        // Afficher les 5 premières, les 5 dernières, et autour de la page actuelle
                        if (
                          pageNum === 1 ||
                          pageNum === totalPages ||
                          (pageNum >= page - 2 && pageNum <= page + 2)
                        ) {
                          return (
                            <button
                              key={pageNum}
                              className={`pagination-page ${page === pageNum ? 'active' : ''}`}
                              onClick={() => setPage(pageNum)}
                            >
                              {pageNum}
                            </button>
                          )
                        } else if (pageNum === page - 3 || pageNum === page + 3) {
                          return <span key={pageNum} className="pagination-ellipsis">...</span>
                        }
                        return null
                      })}
                    </div>
                    
                    <button
                      className="pagination-btn"
                      onClick={() => setPage(page + 1)}
                      disabled={page === totalPages}
                      title="Page suivante"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M9 18l6-6-6-6"/>
                      </svg>
                    </button>
                    <button
                      className="pagination-btn"
                      onClick={() => setPage(totalPages)}
                      disabled={page === totalPages}
                      title="Dernière page"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M13 17l5-5-5-5M6 17l5-5-5-5"/>
                      </svg>
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}

    </div>
  )
}
