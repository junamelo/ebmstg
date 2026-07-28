import { useState, useEffect } from 'react'
import { motion } from 'motion/react'

export default function GestionServices2() {
  const [services, setServices] = useState([
    {
      id: 'data',
      type: 'DATA',
      nom: 'Service DATA',
      actif: true,
      paliers: [
        { id: 1, volumeMin: 0, volumeMax: 1, unite: 'Go', tarif: 0, description: '0 - 1 Go' },
        { id: 2, volumeMin: 1, volumeMax: 7, unite: 'Go', tarif: 4500, description: '1 - 7 Go' },
        { id: 3, volumeMin: 7, volumeMax: 15, unite: 'Go', tarif: 5000, description: '7 - 15 Go' },
        { id: 4, volumeMin: 15, volumeMax: 35, unite: 'Go', tarif: 9000, description: '15 - 35 Go' },
        { id: 5, volumeMin: 35, volumeMax: 85, unite: 'Go', tarif: 15000, description: '35 - 85 Go' },
        { id: 6, volumeMin: 85, volumeMax: 275, unite: 'Go', tarif: 50000, description: '85 - 275 Go' },
        { id: 7, volumeMin: 275, volumeMax: null, unite: 'Mo', tarifParMo: 5, fixe: 50000, description: 'Plus de 275 Go (5 F/Mo au-delà + 50 000 F)' }
      ]
    },
    {
      id: 'voix',
      type: 'VOIX',
      nom: 'Service VOIX',
      actif: true,
      tarifMinute: 79,
      pasFacturation: 30,
      description: '79 F/min avec pas de facturation de 30s'
    },
    {
      id: 'sms',
      type: 'SMS',
      nom: 'Service SMS',
      actif: true,
      tarifUnite: 30,
      description: '30 F/unité'
    }
  ])

  const [modalOuvert, setModalOuvert] = useState(false)
  const [serviceEdite, setServiceEdite] = useState(null)
  const [palierEdite, setPalierEdite] = useState(null)
  const [formData, setFormData] = useState({})

  const ouvrirModalService = (service) => {
    setServiceEdite(service)
    if (service.type === 'VOIX') {
      setFormData({
        tarifMinute: service.tarifMinute,
        pasFacturation: service.pasFacturation
      })
    } else if (service.type === 'SMS') {
      setFormData({
        tarifUnite: service.tarifUnite
      })
    }
    setModalOuvert(true)
  }

  const ouvrirModalPalier = (service, palier) => {
    setServiceEdite(service)
    setPalierEdite(palier)
    setFormData({
      volumeMin: palier.volumeMin,
      volumeMax: palier.volumeMax,
      tarif: palier.tarif || '',
      tarifParMo: palier.tarifParMo || '',
      fixe: palier.fixe || ''
    })
    setModalOuvert(true)
  }

  const fermerModal = () => {
    setModalOuvert(false)
    setServiceEdite(null)
    setPalierEdite(null)
    setFormData({})
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (serviceEdite.type === 'DATA' && palierEdite) {
      // Modifier un palier DATA
      setServices(services.map(s => {
        if (s.id === serviceEdite.id) {
          return {
            ...s,
            paliers: s.paliers.map(p => 
              p.id === palierEdite.id 
                ? { ...p, ...formData, description: `${formData.volumeMin} - ${formData.volumeMax || '∞'} Go` }
                : p
            )
          }
        }
        return s
      }))
    } else if (serviceEdite.type === 'VOIX') {
      // Modifier le service VOIX
      setServices(services.map(s => 
        s.id === serviceEdite.id 
          ? { ...s, ...formData }
          : s
      ))
    } else if (serviceEdite.type === 'SMS') {
      // Modifier le service SMS
      setServices(services.map(s => 
        s.id === serviceEdite.id 
          ? { ...s, ...formData }
          : s
      ))
    }
    
    fermerModal()
  }

  const toggleService = (serviceId) => {
    setServices(services.map(s => 
      s.id === serviceId ? { ...s, actif: !s.actif } : s
    ))
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white mb-2">
          Gestion des Services de Facturation
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          Configuration des paliers de tarification pour DATA, VOIX et SMS
        </p>
      </motion.div>

      {/* Services */}
      <div className="space-y-6">
        {services.map((service, idx) => (
          <motion.div
            key={service.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden shadow-sm"
          >
            {/* En-tête du service */}
            <div className={`p-6 border-b border-zinc-200 dark:border-zinc-800 ${
              service.type === 'DATA' ? 'bg-[#002a7a]/5 dark:bg-[#002a7a]/10' :
              service.type === 'VOIX' ? 'bg-[#002a7a]/5 dark:bg-[#002a7a]/10' :
              'bg-[#e05500]/5 dark:bg-[#e05500]/10'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                    service.type === 'DATA' ? 'bg-[#002a7a]' :
                    service.type === 'VOIX' ? 'bg-[#002a7a]' :
                    'bg-[#e05500]'
                  }`}>
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      {service.type === 'DATA' && <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>}
                      {service.type === 'VOIX' && <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>}
                      {service.type === 'SMS' && <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>}
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-zinc-900 dark:text-white flex items-center gap-3">
                      {service.nom}
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                        service.actif 
                          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
                          : 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400'
                      }`}>
                        {service.actif ? (
                          <>
                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                            </svg>
                            Actif
                          </>
                        ) : (
                          <>
                            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
                            </svg>
                            Inactif
                          </>
                        )}
                      </span>
                    </h2>
                    {service.description && (
                      <p className="text-sm text-zinc-600 dark:text-zinc-400 mt-1">{service.description}</p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => toggleService(service.id)}
                  className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                    service.actif
                      ? 'bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-300 dark:hover:bg-zinc-700'
                      : 'bg-emerald-600 text-white hover:bg-emerald-700'
                  }`}
                >
                  {service.actif ? 'Désactiver' : 'Activer'}
                </button>
              </div>
            </div>

            {/* Contenu du service */}
            <div className="p-6">
              {service.type === 'DATA' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-zinc-900 dark:text-white">Paliers de facturation</h3>
                    <span className="text-sm text-zinc-500 dark:text-zinc-400">
                      {service.paliers.length} paliers configurés
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {service.paliers.map((palier) => (
                      <div 
                        key={palier.id}
                        className="border border-zinc-200 dark:border-zinc-800 rounded-lg p-4 hover:border-[#002a7a] dark:hover:border-[#002a7a] transition-colors"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <p className="text-xs font-semibold text-zinc-600 dark:text-zinc-400 mb-1">
                              {palier.description}
                            </p>
                            {palier.tarifParMo ? (
                              <div className="space-y-1">
                                <p className="text-lg font-bold text-[#002a7a] dark:text-blue-400">
                                  {palier.tarifParMo} F/Mo + {palier.fixe.toLocaleString('fr-FR')} F
                                </p>
                                <p className="text-xs text-zinc-500">Au-delà de {palier.volumeMin} Go</p>
                              </div>
                            ) : (
                              <p className="text-xl font-bold text-[#002a7a] dark:text-blue-400">
                                {palier.tarif.toLocaleString('fr-FR')} F
                              </p>
                            )}
                          </div>
                          <button
                            onClick={() => ouvrirModalPalier(service, palier)}
                            className="ml-2 p-1.5 text-zinc-600 dark:text-zinc-400 hover:text-[#002a7a] dark:hover:text-blue-400 hover:bg-[#002a7a]/10 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                              <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {service.type === 'VOIX' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border border-zinc-200 dark:border-zinc-800 rounded-lg p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-[#002a7a]/10 dark:bg-[#002a7a]/20 rounded-lg flex items-center justify-center">
                        <svg className="w-5 h-5 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">Tarif par minute</p>
                        <p className="text-2xl font-bold text-[#002a7a] dark:text-blue-400">{service.tarifMinute} F</p>
                      </div>
                    </div>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400">Prix facturé par minute d'appel</p>
                  </div>

                  <div className="border border-zinc-200 dark:border-zinc-800 rounded-lg p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-[#002a7a]/10 dark:bg-[#002a7a]/20 rounded-lg flex items-center justify-center">
                        <svg className="w-5 h-5 text-[#002a7a]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">Pas de facturation</p>
                        <p className="text-2xl font-bold text-[#002a7a] dark:text-blue-400">{service.pasFacturation} s</p>
                      </div>
                    </div>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400">
                      0-30s : demi-tarif • 30s-1min : tarif complet
                    </p>
                  </div>

                  <div className="md:col-span-2">
                    <button
                      onClick={() => ouvrirModalService(service)}
                      className="w-full px-4 py-2.5 bg-[#002a7a] hover:bg-[#003d9e] text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                      Modifier la tarification VOIX
                    </button>
                  </div>
                </div>
              )}

              {service.type === 'SMS' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border border-zinc-200 dark:border-zinc-800 rounded-lg p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 bg-[#e05500]/10 dark:bg-[#e05500]/20 rounded-lg flex items-center justify-center">
                        <svg className="w-5 h-5 text-[#e05500]" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                          <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">Tarif unitaire</p>
                        <p className="text-2xl font-bold text-[#e05500] dark:text-orange-400">{service.tarifUnite} F</p>
                      </div>
                    </div>
                    <p className="text-xs text-zinc-500 dark:text-zinc-400">Prix facturé par SMS envoyé</p>
                  </div>

                  <div className="md:col-span-2">
                    <button
                      onClick={() => ouvrirModalService(service)}
                      className="w-full px-4 py-2.5 bg-[#e05500] hover:bg-[#c2410c] text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                      Modifier la tarification SMS
                    </button>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Modal d'édition */}
      {modalOuvert && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-md w-full"
          >
            <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
              <h3 className="text-xl font-bold text-zinc-900 dark:text-white">
                {palierEdite ? `Modifier le palier ${palierEdite.description}` : `Modifier ${serviceEdite.nom}`}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {serviceEdite.type === 'DATA' && palierEdite && (
                <>
                  {!palierEdite.tarifParMo ? (
                    <div>
                      <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                        Tarif (F) <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="number"
                        value={formData.tarif}
                        onChange={(e) => setFormData({ ...formData, tarif: parseFloat(e.target.value) })}
                        required
                        className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] focus:border-transparent outline-none"
                      />
                    </div>
                  ) : (
                    <>
                      <div>
                        <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                          Tarif par Mo (F/Mo) <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          value={formData.tarifParMo}
                          onChange={(e) => setFormData({ ...formData, tarifParMo: parseFloat(e.target.value) })}
                          required
                          className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                          Tarif fixe (F) <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="number"
                          value={formData.fixe}
                          onChange={(e) => setFormData({ ...formData, fixe: parseFloat(e.target.value) })}
                          required
                          className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none"
                        />
                      </div>
                    </>
                  )}
                </>
              )}

              {serviceEdite.type === 'VOIX' && (
                <>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                      Tarif par minute (F) <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      value={formData.tarifMinute}
                      onChange={(e) => setFormData({ ...formData, tarifMinute: parseFloat(e.target.value) })}
                      required
                      className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-emerald-600 focus:border-transparent outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                      Pas de facturation (secondes) <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      value={formData.pasFacturation}
                      onChange={(e) => setFormData({ ...formData, pasFacturation: parseInt(e.target.value) })}
                      required
                      className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-emerald-600 focus:border-transparent outline-none"
                    />
                  </div>
                </>
              )}

              {serviceEdite.type === 'SMS' && (
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Tarif unitaire (F) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    value={formData.tarifUnite}
                    onChange={(e) => setFormData({ ...formData, tarifUnite: parseFloat(e.target.value) })}
                    required
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#e05500] focus:border-transparent outline-none"
                  />
                </div>
              )}

              <div className="flex items-center gap-3 pt-4">
                <button
                  type="submit"
                  className={`flex-1 px-4 py-2.5 text-white font-semibold rounded-lg transition-colors ${
                    serviceEdite.type === 'DATA' ? 'bg-[#002a7a] hover:bg-[#003d9e]' :
                    serviceEdite.type === 'VOIX' ? 'bg-[#002a7a] hover:bg-[#003d9e]' :
                    'bg-[#e05500] hover:bg-[#c2410c]'
                  }`}
                >
                  Enregistrer
                </button>
                <button
                  type="button"
                  onClick={fermerModal}
                  className="flex-1 px-4 py-2.5 bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-lg hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-colors"
                >
                  Annuler
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  )
}
