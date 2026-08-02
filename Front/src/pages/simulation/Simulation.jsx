import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getTarifsActifs, simulerFacturation } from '../../services/simulationService'
import { getServices } from '../../services/servicesService'
import { calculerMontantData, calculerMontantVoixMinutes, calculerMontantSms } from '../../services/tarifsService'
import ImageWithFallback from '../../components/common/ImageWithFallback'
import illustrationSimulation from '../../assets/illustration-simulation.png'
import './Simulation.css'

export default function Simulation() {
  // Type de client
  const [typeClient, setTypeClient] = useState('') // '', 'HYB', 'OP'
  
  const [tarifs, setTarifs]           = useState(null)
  const [services, setServices]       = useState([])
  const [optionsChoisies, setOptionsChoisies] = useState([])
  const [accordionOuvert, setAccordionOuvert] = useState(false)
  const [serviceOuvert, setServiceOuvert]     = useState(null) // [{serviceId, optionId, nom, tarif}]
  const [form, setForm]               = useState({ minutesAppel: '', nombreSms: '', volumeDataGo: '' })
  const [resultat, setResultat]       = useState(null)
  const [chargement, setChargement]   = useState(false)
  const [chargementInit, setChargementInit] = useState(true)
  const [erreur, setErreur]           = useState('')

  useEffect(() => {
    console.log('[Simulation] Chargement initial...')
    Promise.all([getTarifsActifs(), getServices()])
      .then(([t, s]) => {
        console.log('[Simulation] Tarifs:', t)
        console.log('[Simulation] Services:', s)
        setTarifs(t)
        // Filtrer uniquement les services actifs
        const servicesActifs = (s.results || s).filter(srv => srv.est_actif)
        setServices(servicesActifs)
      })
      .catch((err) => {
        console.error('[Simulation] Erreur chargement:', err)
        setErreur('Impossible de charger les tarifs.')
      })
      .finally(() => {
        console.log('[Simulation] Chargement terminé')
        setChargementInit(false)
      })
  }, [])

  // ── Sélection / désélection d'une option de service ──────────
  const toggleOption = (serviceId, option) => {
    const cle = `${serviceId}-${option.id}`
    const existe = optionsChoisies.find(o => o.cle === cle)
    if (existe) {
      setOptionsChoisies(optionsChoisies.filter(o => o.cle !== cle))
    } else {
      // Une seule option par service à la fois
      setOptionsChoisies([
        ...optionsChoisies.filter(o => o.serviceId !== serviceId),
        { cle, serviceId, optionId: option.id, nom: option.nom, tarif: option.tarif },
      ])
    }
  }

  const estChoisie = (serviceId, optionId) =>
    !!optionsChoisies.find(o => o.serviceId === serviceId && o.optionId === optionId)

  // ── Calcul aperçu en temps réel ───────────────────────────────
  const calculApercu = () => {
    if (!tarifs) return null
    const montantServices = optionsChoisies.reduce((acc, o) => acc + o.tarif, 0)
    return { 
      montantAppels: 0, 
      montantSms: 0, 
      montantData: 0, 
      montantServices,
      total: montantServices 
    }
  }

  const apercu = calculApercu()

  // ── Soumission HYBRIDE ────────────────────────────────────────
  const handleSubmitHybride = async (e) => {
    e.preventDefault()
    setErreur('')
    const services_montant = optionsChoisies.reduce((acc, o) => acc + o.tarif, 0)

    if (optionsChoisies.length === 0) {
      setErreur('Veuillez sélectionner au moins un service.')
      return
    }
    setChargement(true)
    try {
      // Simulation avec uniquement les services
      setResultat({
        montantAppels: 0,
        montantSms: 0,
        montantData: 0,
        montantServices: services_montant,
        montantTotal: services_montant,
        servicesChoisis: [...optionsChoisies],
        typeClient: 'HYB'
      })
    } catch {
      setErreur('Erreur lors de la simulation. Réessayez.')
    } finally {
      setChargement(false)
    }
  }

  // ── Soumission OPEN ───────────────────────────────────────────
  const handleSubmitOpen = async (e) => {
    e.preventDefault()
    setErreur('')

    const minutes = parseFloat(form.minutesAppel) || 0
    const sms = parseFloat(form.nombreSms) || 0
    const dataGo = parseFloat(form.volumeDataGo) || 0
    const services_montant = optionsChoisies.reduce((acc, o) => acc + o.tarif, 0)

    if (minutes === 0 && sms === 0 && dataGo === 0 && optionsChoisies.length === 0) {
      setErreur('Veuillez entrer au moins une consommation prévue ou sélectionner un service.')
      return
    }

    setChargement(true)
    try {
      // Calcul selon les PALIERS de tarification
      const montantAppels = calculerMontantVoixMinutes(minutes)
      const montantSms = calculerMontantSms(sms)
      const montantData = calculerMontantData(dataGo)

      setResultat({
        montantAppels,
        montantSms,
        montantData,
        montantServices: services_montant,
        montantTotal: montantAppels + montantSms + montantData + services_montant,
        servicesChoisis: [...optionsChoisies],
        consommationPrevue: { minutes, sms, dataGo },
        typeClient: 'OP'
      })
    } catch {
      setErreur('Erreur lors de la simulation. Réessayez.')
    } finally {
      setChargement(false)
    }
  }

  // ── Réinitialisation ──────────────────────────────────────────
  const handleReset = () => {
    setForm({ minutesAppel: '', nombreSms: '', volumeDataGo: '' })
    setOptionsChoisies([])
    setResultat(null)
    setErreur('')
  }

  if (chargementInit) {
    console.log('[Simulation] Affichage écran de chargement')
    return <div className="loading-overlay"><div className="spinner"></div><span>Chargement...</span></div>
  }

  // ── Écran de sélection du type de client ─────────────────────
  if (!typeClient) {
    console.log('[Simulation] Affichage écran de sélection du type')
    return (
      <div className="simulation-page">
        <div className="page-header">
          <div>
            <h1 className="page-title">Simulation de facturation</h1>
            <p className="text-muted">Choisissez d'abord votre type de client pour accéder à la simulation adaptée.</p>
          </div>
        </div>

        <div className="type-client-selection">
          <button
            className="type-client-card type-client-card--hyb"
            onClick={() => setTypeClient('HYB')}
          >
            <div className="type-client-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
            </div>
            <h3 className="type-client-title">Client HYBRIDE</h3>
            <p className="type-client-description">
              Simulation basée sur votre consommation réelle passée. Sélectionnez uniquement les services optionnels que vous souhaitez ajouter.
            </p>
            <div className="type-client-badge">Facturation basée sur l'historique</div>
          </button>

          <button
            className="type-client-card type-client-card--op"
            onClick={() => setTypeClient('OP')}
          >
            <div className="type-client-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
            </div>
            <h3 className="type-client-title">Client OPEN (Postpayé)</h3>
            <p className="type-client-description">
              Simulation prévisionnelle. Entrez la consommation que vous prévoyez en voix, SMS et data pour estimer votre facture future.
            </p>
            <div className="type-client-badge">Facturation prévisionnelle</div>
          </button>
        </div>
      </div>
    )
  }

  // ──  Page principale de simulation ────────────────────────────
  console.log('[Simulation] Affichage page principale, typeClient:', typeClient)
  console.log('[Simulation] Services disponibles:', services.length)
  console.log('[Simulation] Tarifs:', tarifs)
  
  return (
    <div className="simulation-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            Simulation de facturation 
            {typeClient === 'HYB' && ' - Client HYBRIDE'}
            {typeClient === 'OP' && ' - Client OPEN'}
          </h1>
          <p className="text-muted">
            {typeClient === 'HYB' && 'Sélectionnez les services optionnels pour estimer votre facture.'}
            {typeClient === 'OP' && 'Entrez vos prévisions de consommation pour estimer votre facture.'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            className="btn btn-outline"
            onClick={() => { setTypeClient(''); handleReset() }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
            Changer de type
          </button>
          <Link to="/simulation/historique" className="btn btn-outline">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            Historique
          </Link>
        </div>
      </div>

      <div className="simulation-layout">
        {/* Illustration */}
        <div className="simulation-illustration">
          <ImageWithFallback 
            src={illustrationSimulation} 
            alt="Illustration simulation" 
            className="simulation-illustration-img" 
          />
        </div>

        {/* Formulaire + résultat */}
        <div className="simulation-grid">
          
          {/* ══════════════════════════════════════════════════
              SIMULATION HYBRIDE
          ══════════════════════════════════════════════════ */}
          {typeClient === 'HYB' && (
            <div className="card simulation-form-card">
              <div className="card-header">
                <h2 className="card-title">Services optionnels</h2>
              </div>

              {erreur && <div className="alert alert-danger">{erreur}</div>}

              <form onSubmit={handleSubmitHybride}>
                {/* ── Services — accordéon ── */}
                {services.length > 0 && (
                  <div className="sim-accordion">
                    <button
                      type="button"
                      className="sim-accordion-header"
                      onClick={() => setAccordionOuvert(!accordionOuvert)}
                    >
                      <div className="sim-accordion-header-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
                          <line x1="7" y1="7" x2="7.01" y2="7"/>
                        </svg>
                        <span>Services</span>
                        {optionsChoisies.length > 0 && (
                          <span className="sim-accordion-badge">{optionsChoisies.length} sélectionné{optionsChoisies.length > 1 ? 's' : ''}</span>
                        )}
                      </div>
                      <svg
                        width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
                        style={{ transform: accordionOuvert ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}
                      >
                        <polyline points="6 9 12 15 18 9"/>
                      </svg>
                    </button>

                    {accordionOuvert && (
                      <div className="sim-accordion-body">
                        {services.map(srv => (
                          <div key={srv.id} className="sim-service-item">
                            <button
                              type="button"
                              className="sim-service-header"
                              onClick={() => setServiceOuvert(serviceOuvert === srv.id ? null : srv.id)}
                            >
                              <div className="sim-service-header-left">
                                <svg
                                  width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#002a7a" strokeWidth="2.5"
                                  style={{ transform: serviceOuvert === srv.id ? 'rotate(90deg)' : 'rotate(0)', transition: 'transform 0.2s' }}
                                >
                                  <polyline points="9 18 15 12 9 6"/>
                                </svg>
                                <span className="sim-service-nom">{srv.nom}</span>
                                <span className="sim-service-desc">{srv.description}</span>
                              </div>
                              {optionsChoisies.find(o => o.serviceId === srv.id) && (
                                <span className="sim-service-chosen">
                                  ✓ {optionsChoisies.find(o => o.serviceId === srv.id)?.tarif.toLocaleString('fr-FR')} FCFA/mois
                                </span>
                              )}
                            </button>

                            {serviceOuvert === srv.id && (
                              <div className="sim-options-list">
                                {srv.options.filter(o => o.actif).map(opt => {
                                  const choisi = estChoisie(srv.id, opt.id)
                                  return (
                                    <button
                                      key={opt.id}
                                      type="button"
                                      onClick={() => toggleOption(srv.id, opt)}
                                      className={`sim-option-row ${choisi ? 'sim-option-row--active' : ''}`}
                                    >
                                      <span className="sim-option-row-check">
                                        {choisi ? '●' : '○'}
                                      </span>
                                      <span className="sim-option-row-nom">{opt.nom}</span>
                                      <span className="sim-option-row-tarif">
                                        {opt.tarif.toLocaleString('fr-FR')} FCFA<span>/mois</span>
                                      </span>
                                    </button>
                                  )
                                })}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div className="simulation-actions">
                  <button type="submit" className="btn btn-primary" disabled={chargement}>
                    {chargement ? <><div className="spinner" style={{ width: 16, height: 16 }}></div> Calcul...</> : "Calculer l'estimation"}
                  </button>
                  <button type="button" className="btn btn-outline" onClick={handleReset}>
                    Réinitialiser
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* ══════════════════════════════════════════════════
              SIMULATION OPEN
          ══════════════════════════════════════════════════ */}
          {typeClient === 'OP' && (
            <div className="card simulation-form-card">
              <div className="card-header">
                <h2 className="card-title">Consommation prévue</h2>
              </div>

              {erreur && <div className="alert alert-danger">{erreur}</div>}

              <form onSubmit={handleSubmitOpen}>
                {/* Champs de saisie pour la consommation prévue */}
                <div className="form-group">
                  <label>Minutes d'appel prévues</label>
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Ex: 120"
                    min="0"
                    step="1"
                    value={form.minutesAppel}
                    onChange={(e) => setForm({ ...form, minutesAppel: e.target.value })}
                  />
                  {form.minutesAppel && (
                    <span className="form-hint">
                      ≈ {calculerMontantVoixMinutes(parseFloat(form.minutesAppel)).toLocaleString('fr-FR')} FCFA
                    </span>
                  )}
                </div>

                <div className="form-group">
                  <label>Nombre de SMS prévus</label>
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Ex: 50"
                    min="0"
                    step="1"
                    value={form.nombreSms}
                    onChange={(e) => setForm({ ...form, nombreSms: e.target.value })}
                  />
                  {form.nombreSms && (
                    <span className="form-hint">
                      ≈ {calculerMontantSms(parseFloat(form.nombreSms)).toLocaleString('fr-FR')} FCFA
                    </span>
                  )}
                </div>

                <div className="form-group">
                  <label>Volume de data prévu (en Go)</label>
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Ex: 5"
                    min="0"
                    step="0.1"
                    value={form.volumeDataGo}
                    onChange={(e) => setForm({ ...form, volumeDataGo: e.target.value })}
                  />
                  {form.volumeDataGo && (
                    <span className="form-hint">
                      ≈ {calculerMontantData(parseFloat(form.volumeDataGo)).toLocaleString('fr-FR')} FCFA
                    </span>
                  )}
                </div>

                {/* Services optionnels également pour OPEN */}
                {services.length > 0 && (
                  <div className="sim-accordion">
                    <button
                      type="button"
                      className="sim-accordion-header"
                      onClick={() => setAccordionOuvert(!accordionOuvert)}
                    >
                      <div className="sim-accordion-header-left">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
                          <line x1="7" y1="7" x2="7.01" y2="7"/>
                        </svg>
                        <span>Services optionnels</span>
                        {optionsChoisies.length > 0 && (
                          <span className="sim-accordion-badge">{optionsChoisies.length} sélectionné{optionsChoisies.length > 1 ? 's' : ''}</span>
                        )}
                      </div>
                      <svg
                        width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
                        style={{ transform: accordionOuvert ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}
                      >
                        <polyline points="6 9 12 15 18 9"/>
                      </svg>
                    </button>

                    {accordionOuvert && (
                      <div className="sim-accordion-body">
                        {services.map(srv => (
                          <div key={srv.id} className="sim-service-item">
                            <button
                              type="button"
                              className="sim-service-header"
                              onClick={() => setServiceOuvert(serviceOuvert === srv.id ? null : srv.id)}
                            >
                              <div className="sim-service-header-left">
                                <svg
                                  width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#002a7a" strokeWidth="2.5"
                                  style={{ transform: serviceOuvert === srv.id ? 'rotate(90deg)' : 'rotate(0)', transition: 'transform 0.2s' }}
                                >
                                  <polyline points="9 18 15 12 9 6"/>
                                </svg>
                                <span className="sim-service-nom">{srv.nom}</span>
                                <span className="sim-service-desc">{srv.description}</span>
                              </div>
                              {optionsChoisies.find(o => o.serviceId === srv.id) && (
                                <span className="sim-service-chosen">
                                  ✓ {optionsChoisies.find(o => o.serviceId === srv.id)?.tarif.toLocaleString('fr-FR')} FCFA/mois
                                </span>
                              )}
                            </button>

                            {serviceOuvert === srv.id && (
                              <div className="sim-options-list">
                                {srv.options.filter(o => o.actif).map(opt => {
                                  const choisi = estChoisie(srv.id, opt.id)
                                  return (
                                    <button
                                      key={opt.id}
                                      type="button"
                                      onClick={() => toggleOption(srv.id, opt)}
                                      className={`sim-option-row ${choisi ? 'sim-option-row--active' : ''}`}
                                    >
                                      <span className="sim-option-row-check">
                                        {choisi ? '●' : '○'}
                                      </span>
                                      <span className="sim-option-row-nom">{opt.nom}</span>
                                      <span className="sim-option-row-tarif">
                                        {opt.tarif.toLocaleString('fr-FR')} FCFA<span>/mois</span>
                                      </span>
                                    </button>
                                  )
                                })}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Aperçu du total en temps réel pour OPEN */}
                {(form.minutesAppel || form.nombreSms || form.volumeDataGo || optionsChoisies.length > 0) && (
                  <div className="apercu-total">
                    <span>Montant estimé</span>
                    <strong>
                      {(
                        calculerMontantVoixMinutes(parseFloat(form.minutesAppel) || 0) +
                        calculerMontantSms(parseFloat(form.nombreSms) || 0) +
                        calculerMontantData(parseFloat(form.volumeDataGo) || 0) +
                        optionsChoisies.reduce((acc, o) => acc + o.tarif, 0)
                      ).toLocaleString('fr-FR')} FCFA
                    </strong>
                  </div>
                )}

                <div className="simulation-actions">
                  <button type="submit" className="btn btn-primary" disabled={chargement}>
                    {chargement ? <><div className="spinner" style={{ width: 16, height: 16 }}></div> Calcul...</> : "Calculer l'estimation"}
                  </button>
                  <button type="button" className="btn btn-outline" onClick={handleReset}>
                    Réinitialiser
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* ── Résultat ── */}
          {resultat && (
            <div className="card resultat-card">
              <div className="card-header">
                <h2 className="card-title">Résultat de la simulation</h2>
              </div>
              
              <div className="resultat-detail">
                {/* Détails pour OPEN */}
                {resultat.typeClient === 'OP' && resultat.consommationPrevue && (
                  <>
                    {resultat.consommationPrevue.minutes > 0 && (
                      <div className="resultat-ligne">
                        <span>Appels ({resultat.consommationPrevue.minutes} min)</span>
                        <strong>{resultat.montantAppels.toLocaleString('fr-FR')} FCFA</strong>
                      </div>
                    )}
                    {resultat.consommationPrevue.sms > 0 && (
                      <div className="resultat-ligne">
                        <span>SMS ({resultat.consommationPrevue.sms} SMS)</span>
                        <strong>{resultat.montantSms.toLocaleString('fr-FR')} FCFA</strong>
                      </div>
                    )}
                    {resultat.consommationPrevue.dataGo > 0 && (
                      <div className="resultat-ligne">
                        <span>Data ({resultat.consommationPrevue.dataGo} Go)</span>
                        <strong>{resultat.montantData.toLocaleString('fr-FR')} FCFA</strong>
                      </div>
                    )}
                  </>
                )}

                {/* Services */}
                {resultat.servicesChoisis?.map(o => (
                  <div key={o.cle} className="resultat-ligne">
                    <span>{o.nom}</span>
                    <strong>{o.tarif.toLocaleString('fr-FR')} FCFA</strong>
                  </div>
                ))}
              </div>
              
              <div className="resultat-total">
                <span>Montant total estimé</span>
                <span className="resultat-montant">{resultat.montantTotal?.toLocaleString('fr-FR')} FCFA</span>
              </div>
              
              <p className="resultat-note">
                {resultat.typeClient === 'HYB' 
                  ? "Cette simulation est basée sur votre consommation réelle passée, plus les services optionnels sélectionnés."
                  : "Cette simulation est basée sur vos prévisions de consommation. Le montant réel peut varier selon votre consommation effective."
                }
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
