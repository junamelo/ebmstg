import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import {
  mockGetServices,
  mockCreerService,
  mockToggleService,
  mockAjouterOption,
  mockToggleOption,
} from '../../services/mockApi'

export default function GestionServices() {
  const [services, setServices] = useState([])
  const [chargement, setChargement] = useState(true)
  const [message, setMessage]     = useState(null)
  const [servicesOuverts, setServicesOuverts] = useState({})

  // Modal nouveau service
  const [formService, setFormService] = useState({ nom: '', description: '' })
  const [formServiceOuvert, setFormServiceOuvert] = useState(false)
  const [modeEditionService, setModeEditionService] = useState(false)
  const [serviceEnEdition, setServiceEnEdition] = useState(null)

  // Modal nouvelle option — on mémorise le serviceId ciblé
  const [formOption, setFormOption]   = useState({ nom: '', tarif: '' })
  const [serviceSelectionne, setServiceSelectionne] = useState(null) // id du service en cours d'édition
  const [modeEditionOption, setModeEditionOption] = useState(false)
  const [optionEnEdition, setOptionEnEdition] = useState(null)

  useEffect(() => {
    mockGetServices().then(setServices).finally(() => setChargement(false))
  }, [])

  const showMsg = (type, texte) => {
    setMessage({ type, texte })
    setTimeout(() => setMessage(null), 4000)
  }

  // ── Créer ou modifier un service ─────────────────────────────
  const handleCreerService = async (e) => {
    e.preventDefault()
    try {
      if (modeEditionService && serviceEnEdition) {
        // Mode modification
        setServices(services.map(s =>
          s.id === serviceEnEdition.id
            ? { ...s, nom: formService.nom, description: formService.description }
            : s
        ))
        showMsg('success', `Forfait « ${formService.nom} » modifié.`)
        setModeEditionService(false)
        setServiceEnEdition(null)
      } else {
        // Mode création
        const nouveau = await mockCreerService(formService)
        setServices([nouveau, ...services])
        showMsg('success', `Forfait « ${nouveau.nom} » créé.`)
      }
      setFormService({ nom: '', description: '' })
      setFormServiceOuvert(false)
    } catch { showMsg('error', 'Erreur lors de l\'opération.') }
  }

  // ── Ouvrir le formulaire de modification de service ──────────
  const handleModifierService = (service) => {
    setModeEditionService(true)
    setServiceEnEdition(service)
    setFormService({ nom: service.nom, description: service.description })
    setFormServiceOuvert(true)
  }

  // ── Annuler modification service ──────────────────────────────
  const annulerEditionService = () => {
    setModeEditionService(false)
    setServiceEnEdition(null)
    setFormService({ nom: '', description: '' })
    setFormServiceOuvert(false)
  }

  // ── Toggle actif/inactif service ──────────────────────────────
  const handleToggleService = async (id) => {
    await mockToggleService(id)
    setServices(services.map(s => s.id === id ? { ...s, actif: !s.actif } : s))
  }

  // ── Ajouter ou modifier une option tarifaire ─────────────────
  const handleAjouterOption = async (e) => {
    e.preventDefault()
    if (!serviceSelectionne) return
    try {
      if (modeEditionOption && optionEnEdition) {
        // Mode modification
        setServices(services.map(s =>
          s.id === serviceSelectionne
            ? {
                ...s,
                options: s.options.map(o =>
                  o.id === optionEnEdition.id
                    ? { ...o, nom: formOption.nom, tarif: parseFloat(formOption.tarif) }
                    : o
                )
              }
            : s
        ))
        showMsg('success', `Option « ${formOption.nom} » modifiée.`)
        setModeEditionOption(false)
        setOptionEnEdition(null)
      } else {
        // Mode création
        const opt = await mockAjouterOption(serviceSelectionne, formOption)
        setServices(services.map(s =>
          s.id === serviceSelectionne
            ? { ...s, options: [...s.options, opt] }
            : s
        ))
        showMsg('success', `Option « ${opt.nom} » ajoutée.`)
      }
      setFormOption({ nom: '', tarif: '' })
      setServiceSelectionne(null)
    } catch { showMsg('error', "Erreur lors de l'opération.") }
  }

  // ── Ouvrir le formulaire de modification d'option ────────────
  const handleModifierOption = (serviceId, option) => {
    setModeEditionOption(true)
    setOptionEnEdition(option)
    setServiceSelectionne(serviceId)
    setFormOption({ nom: option.nom, tarif: option.tarif.toString() })
  }

  // ── Annuler modification option ───────────────────────────────
  const annulerEditionOption = () => {
    setModeEditionOption(false)
    setOptionEnEdition(null)
    setFormOption({ nom: '', tarif: '' })
    setServiceSelectionne(null)
  }

  // ── Toggle option ─────────────────────────────────────────────
  const handleToggleOption = async (serviceId, optionId) => {
    await mockToggleOption(serviceId, optionId)
    setServices(services.map(s =>
      s.id === serviceId
        ? { ...s, options: s.options.map(o => o.id === optionId ? { ...o, actif: !o.actif } : o) }
        : s
    ))
  }

  if (chargement) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-zinc-300 border-t-[#e05500] rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 mb-2">Gestion des Forfaits</h1>
          <p className="text-zinc-600">
            Gestion des forfaits et packages (BlackBerry, No Limit, Facture Détaillée, Incognito...)
          </p>
        </div>
        <button
          onClick={() => setFormServiceOuvert(true)}
          className="px-4 py-2 bg-[#e05500] hover:bg-[#c44a00] text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
          Nouveau forfait
        </button>
      </div>

      {/* Message flash */}
      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
            className={`rounded-lg p-4 text-sm font-medium ${
              message.type === 'success'
                ? 'bg-emerald-50 border border-emerald-200 text-emerald-800'
                : 'bg-rose-50 border border-rose-200 text-rose-800'
            }`}
          >
            {message.texte}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal créer service */}
      <AnimatePresence>
        {formServiceOuvert && (
          <motion.div
            initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="bg-white rounded-xl border border-zinc-200 p-6">
              <h2 className="text-lg font-semibold text-zinc-900 mb-4">
                {modeEditionService ? 'Modifier le forfait' : 'Créer un nouveau forfait'}
              </h2>
              <form onSubmit={handleCreerService} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-1">Nom du forfait *</label>
                    <input
                      required type="text"
                      className="w-full px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-[#e05500] outline-none"
                      placeholder="Ex: BlackBerry BB12, No Limit..."
                      value={formService.nom}
                      onChange={e => setFormService({ ...formService, nom: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-zinc-700 mb-1">Description</label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-[#e05500] outline-none"
                      placeholder="Description courte"
                      value={formService.description}
                      onChange={e => setFormService({ ...formService, description: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex gap-3">
                  <button type="submit" className="px-5 py-2 bg-[#e05500] text-white rounded-lg text-sm font-medium hover:bg-[#c44a00] transition-colors">
                    {modeEditionService ? 'Enregistrer' : 'Créer'}
                  </button>
                  <button type="button" onClick={annulerEditionService}
                    className="px-5 py-2 bg-zinc-100 text-zinc-700 rounded-lg text-sm font-medium hover:bg-zinc-200 transition-colors">
                    Annuler
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modal ajouter option */}
      <AnimatePresence>
        {serviceSelectionne && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.96 }}
              className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-semibold text-zinc-900">
                  {modeEditionOption ? 'Modifier l\'option' : 'Ajouter une option'} — {services.find(s => s.id === serviceSelectionne)?.nom}
                </h2>
                <button onClick={annulerEditionOption}
                  className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-zinc-100 text-zinc-400">✕</button>
              </div>
              <form onSubmit={handleAjouterOption} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-zinc-700 mb-1">Nom de l'option *</label>
                  <input
                    required type="text"
                    className="w-full px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-[#e05500] outline-none"
                    placeholder="Ex: BlackBerry BB12"
                    value={formOption.nom}
                    onChange={e => setFormOption({ ...formOption, nom: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-zinc-700 mb-1">Tarif mensuel (FCFA) *</label>
                  <input
                    required type="number" min="0" step="100"
                    className="w-full px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-[#e05500] outline-none"
                    placeholder="Ex: 1200"
                    value={formOption.tarif}
                    onChange={e => setFormOption({ ...formOption, tarif: e.target.value })}
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button type="submit" className="px-5 py-2 bg-[#e05500] text-white rounded-lg text-sm font-medium hover:bg-[#c44a00] transition-colors">
                    {modeEditionOption ? 'Enregistrer' : 'Ajouter l\'option'}
                  </button>
                  <button type="button" onClick={annulerEditionOption}
                    className="px-5 py-2 bg-zinc-100 text-zinc-700 rounded-lg text-sm font-medium hover:bg-zinc-200 transition-colors">
                    Annuler
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Liste des services */}
      <div className="space-y-4">
        {services.map((service, idx) => (
          <motion.div
            key={service.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="bg-white rounded-xl border border-zinc-200 overflow-hidden"
          >
            {/* En-tête service cliquable */}
            <button
              onClick={() => setServicesOuverts(prev => ({ ...prev, [service.id]: !prev[service.id] }))}
              className="w-full flex items-center justify-between px-6 py-4 hover:bg-zinc-50 transition-colors text-left"
            >
              <div className="flex items-center gap-4 flex-1">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm ${service.actif ? 'bg-[#e05500]' : 'bg-zinc-400'}`}>
                  {service.nom[0]}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-zinc-900">{service.nom}</h3>
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                      service.actif ? 'bg-emerald-100 text-emerald-700' : 'bg-zinc-100 text-zinc-500'
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${service.actif ? 'bg-emerald-500 animate-pulse' : 'bg-zinc-400'}`} />
                      {service.actif ? 'Actif' : 'Inactif'}
                    </span>
                  </div>
                  <p className="text-sm text-zinc-500">{service.description} · {service.options.filter(o => o.actif).length} option(s) active(s)</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <svg className={`w-5 h-5 text-zinc-400 transition-transform ${servicesOuverts[service.id] ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </button>

            {/* Options tarifaires (accordéon) */}
            <AnimatePresence>
              {servicesOuverts[service.id] && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden border-t border-zinc-100"
                >
                  <div className="p-4 space-y-3">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-sm font-medium text-zinc-700">Actions rapides</span>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleModifierService(service)}
                          className="px-3 py-1.5 text-xs font-medium text-[#002a7a] border border-[#002a7a] rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          ✏️ Modifier
                        </button>
                        <button
                          onClick={() => setServiceSelectionne(service.id)}
                          className="px-3 py-1.5 text-xs font-medium text-[#e05500] border border-[#e05500] rounded-lg hover:bg-orange-50 transition-colors"
                        >
                          + Option
                        </button>
                        <button
                          onClick={() => handleToggleService(service.id)}
                          className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                            service.actif
                              ? 'text-zinc-600 border border-zinc-300 hover:bg-zinc-50'
                              : 'text-emerald-700 border border-emerald-300 hover:bg-emerald-50'
                          }`}
                        >
                          {service.actif ? 'Désactiver' : 'Activer'}
                        </button>
                      </div>
                    </div>

                    {service.options.length === 0 ? (
                      <div className="px-4 py-6 text-sm text-zinc-400 italic text-center">
                        Aucune option tarifaire — cliquez sur « + Option » pour en ajouter.
                      </div>
                    ) : (
                      <div className="divide-y divide-zinc-50">
                        {service.options.map(opt => (
                          <div key={opt.id} className="flex items-center justify-between px-4 py-3 hover:bg-zinc-50 transition-colors">
                            <div className="flex items-center gap-3">
                              <span className={`w-2 h-2 rounded-full ${opt.actif ? 'bg-emerald-500' : 'bg-zinc-300'}`} />
                              <span className="text-sm font-medium text-zinc-800">{opt.nom}</span>
                            </div>
                            <div className="flex items-center gap-4">
                              <span className="text-sm font-bold text-[#e05500]">
                                {opt.tarif.toLocaleString('fr-FR')} FCFA<span className="text-xs font-normal text-zinc-500">/mois</span>
                              </span>
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleModifierOption(service.id, opt)}
                                  className="text-xs px-2.5 py-1 rounded-lg transition-colors bg-blue-100 text-blue-700 hover:bg-blue-200"
                                >
                                  ✏️ Modifier
                                </button>
                                <button
                                  onClick={() => handleToggleOption(service.id, opt.id)}
                                  className={`text-xs px-2.5 py-1 rounded-lg transition-colors ${
                                    opt.actif
                                      ? 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
                                      : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200'
                                  }`}
                                >
                                  {opt.actif ? 'Désactiver' : 'Activer'}
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
