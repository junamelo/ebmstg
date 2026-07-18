import { useState, useEffect } from 'react'
import { getTarifsActifs, simulerFacturation } from '../../services/simulationService'
import { mockGetServices } from '../../services/mockApi'
import illustrationSimulation from '../../assets/illustration-simulation.png'
import './Simulation.css'

export default function Simulation() {
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
    Promise.all([getTarifsActifs(), mockGetServices()])
      .then(([t, s]) => {
        setTarifs(t)
        setServices(s.filter(srv => srv.actif))
      })
      .catch(() => setErreur('Impossible de charger les tarifs.'))
      .finally(() => setChargementInit(false))
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
    const minutes = parseFloat(form.minutesAppel) || 0
    const sms     = parseFloat(form.nombreSms)    || 0
    const data    = parseFloat(form.volumeDataGo) || 0
    const montantAppels   = minutes * tarifs.prixParMinute
    const montantSms      = sms * tarifs.prixParSms
    const montantData     = data * tarifs.prixParGo
    const montantServices = optionsChoisies.reduce((acc, o) => acc + o.tarif, 0)
    return { montantAppels, montantSms, montantData, montantServices,
             total: montantAppels + montantSms + montantData + montantServices }
  }

  const apercu = calculApercu()

  // ── Soumission ────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault()
    setErreur('')
    const minutes = parseFloat(form.minutesAppel) || 0
    const sms     = parseFloat(form.nombreSms)    || 0
    const data    = parseFloat(form.volumeDataGo) || 0
    const services_montant = optionsChoisies.reduce((acc, o) => acc + o.tarif, 0)

    if (minutes === 0 && sms === 0 && data === 0 && optionsChoisies.length === 0) {
      setErreur('Veuillez saisir au moins une valeur de consommation ou choisir un service.')
      return
    }
    setChargement(true)
    try {
      const res = await simulerFacturation({ minutesAppel: minutes, nombreSms: sms, volumeDataGo: data })
      setResultat({
        ...res,
        montantServices: services_montant,
        montantTotal: res.montantTotal + services_montant,
        servicesChoisis: [...optionsChoisies],
      })
    } catch {
      setErreur('Erreur lors de la simulation. Réessayez.')
    } finally {
      setChargement(false)
    }
  }

  if (chargementInit) {
    return <div className="loading-overlay"><div className="spinner"></div><span>Chargement...</span></div>
  }

  return (
    <div className="simulation-page">
      <div className="page-header">
        <h1 className="page-title">Simulation de facturation</h1>
        <p className="text-muted">Estimez le montant de votre prochaine facture.</p>
      </div>

      <div className="simulation-layout">

        {/* Illustration */}
        <div className="simulation-illustration">
          <img src={illustrationSimulation} alt="Illustration simulation" className="simulation-illustration-img" />
        </div>

        {/* Formulaire + résultat */}
        <div className="simulation-grid">

          {/* ── Consommation ── */}
          <div className="card simulation-form-card">
            <div className="card-header">
              <h2 className="card-title">Consommation prévue</h2>
            </div>

            {erreur && <div className="alert alert-danger">{erreur}</div>}

            {tarifs && (
              <div className="tarifs-info">
                <h3>Tarifs en vigueur — {tarifs.nom}</h3>
                <div className="tarifs-grid">
                  <div className="tarif-item">
                    <span>Appels</span>
                    <strong>{tarifs.prixParMinute?.toLocaleString('fr-FR')} FCFA / min</strong>
                  </div>
                  <div className="tarif-item">
                    <span>SMS</span>
                    <strong>{tarifs.prixParSms?.toLocaleString('fr-FR')} FCFA / SMS</strong>
                  </div>
                  <div className="tarif-item">
                    <span>Data</span>
                    <strong>{tarifs.prixParGo?.toLocaleString('fr-FR')} FCFA / Go</strong>
                  </div>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Durée d'appels prévue (minutes)</label>
                <input type="number" className="form-control" placeholder="Ex : 3000 min" min="0"
                  value={form.minutesAppel} onChange={e => setForm({ ...form, minutesAppel: e.target.value })} />
                {apercu && form.minutesAppel > 0 && (
                  <span className="form-hint">≈ {apercu.montantAppels.toLocaleString('fr-FR')} FCFA</span>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Nombre de SMS prévus</label>
                <input type="number" className="form-control" placeholder="Ex : 200 SMS" min="0"
                  value={form.nombreSms} onChange={e => setForm({ ...form, nombreSms: e.target.value })} />
                {apercu && form.nombreSms > 0 && (
                  <span className="form-hint">≈ {apercu.montantSms.toLocaleString('fr-FR')} FCFA</span>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Volume de data prévu (Go)</label>
                <input type="number" className="form-control" placeholder="Ex : 5 Go" min="0" step="0.1"
                  value={form.volumeDataGo} onChange={e => setForm({ ...form, volumeDataGo: e.target.value })} />
                {apercu && form.volumeDataGo > 0 && (
                  <span className="form-hint">≈ {apercu.montantData.toLocaleString('fr-FR')} FCFA</span>
                )}
              </div>

              {/* ── Services optionnels — accordéon ── */}
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
                          {/* En-tête du service — cliquable pour dérouler */}
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

                          {/* Options tarifaires — déroulées */}
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

                      {optionsChoisies.length > 0 && (
                        <div className="sim-accordion-total">
                          <span>Total services :</span>
                          <strong>{apercu?.montantServices.toLocaleString('fr-FR')} FCFA/mois</strong>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {apercu && apercu.total > 0 && (
                <div className="apercu-total">
                  <span>Estimation totale :</span>
                  <strong className="text-orange">{apercu.total.toLocaleString('fr-FR')} FCFA</strong>
                </div>
              )}

              <div className="simulation-actions">
                <button type="submit" className="btn btn-primary" disabled={chargement}>
                  {chargement ? <><div className="spinner" style={{ width: 16, height: 16 }}></div> Calcul...</> : "Calculer l'estimation"}
                </button>
                <button type="button" className="btn btn-outline"
                  onClick={() => { setForm({ minutesAppel: '', nombreSms: '', volumeDataGo: '' }); setOptionsChoisies([]); setResultat(null); setErreur('') }}>
                  Réinitialiser
                </button>
              </div>
            </form>
          </div>

          {/* ── Résultat ── */}
          {resultat && (
            <div className="card resultat-card">
              <div className="card-header">
                <h2 className="card-title">Résultat de la simulation</h2>
              </div>
              <div className="resultat-detail">
                {resultat.montantAppels > 0 && (
                  <div className="resultat-ligne">
                    <span>Appels ({form.minutesAppel} min × {tarifs?.prixParMinute} F)</span>
                    <strong>{resultat.montantAppels?.toLocaleString('fr-FR')} FCFA</strong>
                  </div>
                )}
                {resultat.montantSms > 0 && (
                  <div className="resultat-ligne">
                    <span>SMS ({form.nombreSms} SMS × {tarifs?.prixParSms} F)</span>
                    <strong>{resultat.montantSms?.toLocaleString('fr-FR')} FCFA</strong>
                  </div>
                )}
                {resultat.montantData > 0 && (
                  <div className="resultat-ligne">
                    <span>Data ({form.volumeDataGo} Go × {tarifs?.prixParGo} F)</span>
                    <strong>{resultat.montantData?.toLocaleString('fr-FR')} FCFA</strong>
                  </div>
                )}
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
                Cette simulation est indicative. Le montant réel peut varier selon votre consommation effective.
              </p>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
