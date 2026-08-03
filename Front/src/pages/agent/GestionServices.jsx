import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'

export default function GestionServices() {
  const [message, setMessage] = useState(null)
  const [serviceActif, setServiceActif] = useState('DATA') // DATA, VOIX, SMS
  
  // Paliers DATA (en Go et XOF)
  const [paliersData, setPaliersData] = useState([
    { id: 1, min: 0, max: 1, prix: 0, description: '0 à 1 Go' },
    { id: 2, min: 1, max: 7, prix: 4500, description: '> 1 Go et ≤ 7 Go' },
    { id: 3, min: 7, max: 15, prix: 5000, description: '> 7 Go et ≤ 15 Go' },
    { id: 4, min: 15, max: 35, prix: 9000, description: '> 15 Go et ≤ 35 Go' },
    { id: 5, min: 35, max: 85, prix: 15000, description: '> 35 Go et ≤ 85 Go' },
    { id: 6, min: 85, max: 275, prix: 50000, description: '> 85 Go et ≤ 275 Go' },
    { id: 7, min: 275, max: 999999, prix: 5, prixParMo: true, description: '> 275 Go (5 F/Mo après 275 Go + 50 000 F)' }
  ])

  // Tarifs VOIX (en FCFA)
  const [tarifsVoix, setTarifsVoix] = useState([
    { id: 1, dureeMin: 0, dureeMax: 30, prix: 39.5, unite: 'appel', description: '0 à 30 secondes' },
    { id: 2, dureeMin: 30, dureeMax: 60, prix: 79, unite: 'minute', description: '> 30s et ≤ 1 minute' },
    { id: 3, dureeMin: 60, dureeMax: 999999, prix: 79, unite: 'minute', description: 'Au-delà de 1 minute (79 F/min, pas de 30s)' }
  ])

  // Tarif SMS
  const [tarifSMS, setTarifSMS] = useState({ prix: 30, unite: 'SMS' })

  const [modalOuvert, setModalOuvert] = useState(false)
  const [palierEdite, setPalierEdite] = useState(null)

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 4000)
  }

  const ouvrirModal = (palier = null) => {
    setPalierEdite(palier)
    setModalOuvert(true)
  }

  const fermerModal = () => {
    setModalOuvert(false)
    setPalierEdite(null)
  }

  const handleSauvegarderPalier = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    
    if (serviceActif === 'DATA') {
      const nouveauPalier = {
        id: palierEdite?.id || Date.now(),
        min: parseFloat(formData.get('min')),
        max: parseFloat(formData.get('max')),
        prix: parseFloat(formData.get('prix')),
        prixParMo: formData.get('prixParMo') === 'true',
        description: formData.get('description')
      }
      
      if (palierEdite) {
        setPaliersData(paliersData.map(p => p.id === palierEdite.id ? nouveauPalier : p))
        showMessage('success', 'Palier DATA modifié avec succès')
      } else {
        setPaliersData([...paliersData, nouveauPalier])
        showMessage('success', 'Palier DATA ajouté avec succès')
      }
    } else if (serviceActif === 'VOIX') {
      const nouveauTarif = {
        id: palierEdite?.id || Date.now(),
        dureeMin: parseFloat(formData.get('dureeMin')),
        dureeMax: parseFloat(formData.get('dureeMax')),
        prix: parseFloat(formData.get('prix')),
        unite: formData.get('unite'),
        description: formData.get('description')
      }
      
      if (palierEdite) {
        setTarifsVoix(tarifsVoix.map(t => t.id === palierEdite.id ? nouveauTarif : t))
        showMessage('success', 'Tarif VOIX modifié avec succès')
      } else {
        setTarifsVoix([...tarifsVoix, nouveauTarif])
        showMessage('success', 'Tarif VOIX ajouté avec succès')
      }
    }
    
    fermerModal()
  }

  const handleSauvegarderTarifSMS = (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    setTarifSMS({
      prix: parseFloat(formData.get('prix')),
      unite: 'SMS'
    })
    showMessage('success', 'Tarif SMS mis à jour avec succès')
  }

  const handleSupprimerPalier = (id) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce palier ?')) return
    
    if (serviceActif === 'DATA') {
      setPaliersData(paliersData.filter(p => p.id !== id))
      showMessage('success', 'Palier DATA supprimé')
    } else if (serviceActif === 'VOIX') {
      setTarifsVoix(tarifsVoix.filter(t => t.id !== id))
      showMessage('success', 'Tarif VOIX supprimé')
    }
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Message flash */}
      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -8 }} 
            animate={{ opacity: 1, y: 0 }} 
            exit={{ opacity: 0, y: -8 }}
            className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-xl ${
              message.type === 'success'
                ? 'bg-emerald-500 text-white'
                : 'bg-rose-500 text-white'
            }`}
          >
            {message.text}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-zinc-900 mb-2">
          Gestion des Services Hors-Forfait
        </h1>
        <p className="text-zinc-600">
          Configuration des paliers de tarification pour DATA, VOIX et SMS
        </p>
      </div>

      {/* Tabs Services */}
      <div className="flex items-center gap-2 border-b border-zinc-200">
        {[
          { id: 'DATA', label: 'Data', icon: '📊' },
          { id: 'VOIX', label: 'Voix', icon: '📞' },
          { id: 'SMS', label: 'SMS', icon: '💬' }
        ].map(service => (
          <button
            key={service.id}
            onClick={() => setServiceActif(service.id)}
            className={`px-6 py-3 font-semibold text-sm transition-colors relative ${
              serviceActif === service.id
                ? 'text-[#e05500] border-b-2 border-[#e05500]'
                : 'text-zinc-600 hover:text-zinc-900'
            }`}
          >
            <span className="mr-2">{service.icon}</span>
            {service.label}
          </button>
        ))}
      </div>

      {/* Contenu DATA */}
      {serviceActif === 'DATA' && (
        <motion.div
          key="data"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-zinc-900">Paliers de facturation DATA</h2>
              <p className="text-sm text-zinc-600 mt-1">
                Tarification par tranche de consommation en Giga-octets
              </p>
            </div>
            <button
              onClick={() => ouvrirModal()}
              className="px-4 py-2.5 bg-[#e05500] hover:bg-[#c44a00] text-white font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4"/>
              </svg>
              Ajouter un palier
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {paliersData.map((palier, idx) => (
              <motion.div
                key={palier.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-gradient-to-br from-white to-blue-50 rounded-xl border-2 border-blue-200 p-5 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-600 text-white text-xs font-bold rounded-full">
                    Palier {idx + 1}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => ouvrirModal(palier)}
                      className="p-1.5 hover:bg-blue-100 rounded-lg transition-colors text-blue-700"
                      title="Modifier"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                      </svg>
                    </button>
                    <button
                      onClick={() => handleSupprimerPalier(palier.id)}
                      className="p-1.5 hover:bg-red-100 rounded-lg transition-colors text-red-600"
                      title="Supprimer"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </div>
                </div>
                
                <p className="text-sm font-medium text-zinc-700 mb-2">{palier.description}</p>
                
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-2xl font-black text-blue-700">
                    {palier.prix.toLocaleString('fr-FR')}
                  </span>
                  <span className="text-sm font-semibold text-zinc-600">
                    {palier.prixParMo ? 'F/Mo' : 'FCFA'}
                  </span>
                </div>
                
                {palier.prixParMo && (
                  <p className="text-xs text-amber-700 bg-amber-50 px-2 py-1 rounded">
                    + 50 000 F de base après 275 Go
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Contenu VOIX */}
      {serviceActif === 'VOIX' && (
        <motion.div
          key="voix"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-zinc-900">Tarifs VOIX</h2>
              <p className="text-sm text-zinc-600 mt-1">
                Tarification des appels avec pas de facturation de 30 secondes
              </p>
            </div>
            <button
              onClick={() => ouvrirModal()}
              className="px-4 py-2.5 bg-[#e05500] hover:bg-[#c44a00] text-white font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M12 4v16m8-8H4"/>
              </svg>
              Ajouter un tarif
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {tarifsVoix.map((tarif, idx) => (
              <motion.div
                key={tarif.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-gradient-to-br from-white to-green-50 rounded-xl border-2 border-green-200 p-5 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-600 text-white text-xs font-bold rounded-full">
                    Tarif {idx + 1}
                  </span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => ouvrirModal(tarif)}
                      className="p-1.5 hover:bg-green-100 rounded-lg transition-colors text-green-700"
                      title="Modifier"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                      </svg>
                    </button>
                    <button
                      onClick={() => handleSupprimerPalier(tarif.id)}
                      className="p-1.5 hover:bg-red-100 rounded-lg transition-colors text-red-600"
                      title="Supprimer"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                  </div>
                </div>
                
                <p className="text-sm font-medium text-zinc-700 mb-2">{tarif.description}</p>
                
                <div className="flex items-baseline gap-2">
                  <span className="text-2xl font-black text-green-700">
                    {tarif.prix.toLocaleString('fr-FR')}
                  </span>
                  <span className="text-sm font-semibold text-zinc-600">
                    F/{tarif.unite}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
              </svg>
              <div>
                <h4 className="font-semibold text-amber-900 mb-1">Règle de facturation</h4>
                <p className="text-sm text-amber-800">
                  Exemple : Appel de 1 min 20s = 79 F + (79 F / 2) = 118,50 F<br/>
                  Appel de 1 min 40s = 79 F × 2 = 158 F
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Contenu SMS */}
      {serviceActif === 'SMS' && (
        <motion.div
          key="sms"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div>
            <h2 className="text-xl font-bold text-zinc-900">Tarif SMS</h2>
            <p className="text-sm text-zinc-600 mt-1">
              Prix unitaire par SMS envoyé
            </p>
          </div>

          <div className="max-w-md">
            <form onSubmit={handleSauvegarderTarifSMS} className="bg-gradient-to-br from-white to-purple-50 rounded-xl border-2 border-purple-200 p-6">
              <div className="mb-4">
                <label className="block text-sm font-semibold text-zinc-700 mb-2">
                  Prix unitaire (FCFA) *
                </label>
                <input
                  name="prix"
                  type="number"
                  step="0.01"
                  required
                  defaultValue={tarifSMS.prix}
                  className="w-full px-4 py-3 bg-white border-2 border-purple-300 rounded-lg text-lg font-bold text-purple-700 focus:ring-2 focus:ring-purple-500 outline-none"
                />
              </div>
              
              <div className="flex items-baseline gap-2 mb-4 p-4 bg-purple-100 rounded-lg">
                <span className="text-3xl font-black text-purple-700">
                  {tarifSMS.prix}
                </span>
                <span className="text-sm font-semibold text-purple-600">
                  FCFA / SMS
                </span>
              </div>

              <button
                type="submit"
                className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors"
              >
                Enregistrer le tarif SMS
              </button>
            </form>
          </div>
        </motion.div>
      )}

      {/* Modal ajout/édition palier */}
      <AnimatePresence>
        {modalOuvert && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              className="bg-white rounded-2xl shadow-2xl w-full max-w-lg"
            >
              <div className="px-6 py-4 border-b border-zinc-200">
                <h3 className="text-lg font-bold text-zinc-900">
                  {palierEdite ? `Modifier ${serviceActif === 'DATA' ? 'le palier' : 'le tarif'}` : `Ajouter un ${serviceActif === 'DATA' ? 'palier' : 'tarif'} ${serviceActif}`}
                </h3>
              </div>

              <form onSubmit={handleSauvegarderPalier} className="p-6 space-y-4">
                {serviceActif === 'DATA' && (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-zinc-700 mb-1">Min (Go) *</label>
                        <input
                          name="min"
                          type="number"
                          step="0.01"
                          required
                          defaultValue={palierEdite?.min || 0}
                          className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-700 mb-1">Max (Go) *</label>
                        <input
                          name="max"
                          type="number"
                          step="0.01"
                          required
                          defaultValue={palierEdite?.max || 0}
                          className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-zinc-700 mb-1">Prix (FCFA) *</label>
                      <input
                        name="prix"
                        type="number"
                        step="0.01"
                        required
                        defaultValue={palierEdite?.prix || 0}
                        className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                      />
                    </div>
                    <div>
                      <label className="flex items-center gap-2">
                        <input
                          name="prixParMo"
                          type="checkbox"
                          value="true"
                          defaultChecked={palierEdite?.prixParMo || false}
                          className="w-4 h-4 text-[#e05500] border-zinc-300 rounded focus:ring-[#e05500]"
                        />
                        <span className="text-sm font-medium text-zinc-700">Prix par Mo (au lieu de forfait)</span>
                      </label>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-zinc-700 mb-1">Description *</label>
                      <input
                        name="description"
                        type="text"
                        required
                        defaultValue={palierEdite?.description || ''}
                        placeholder="Ex: > 1 Go et ≤ 7 Go"
                        className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                      />
                    </div>
                  </>
                )}

                {serviceActif === 'VOIX' && (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-zinc-700 mb-1">Durée min (s) *</label>
                        <input
                          name="dureeMin"
                          type="number"
                          required
                          defaultValue={palierEdite?.dureeMin || 0}
                          className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-zinc-700 mb-1">Durée max (s) *</label>
                        <input
                          name="dureeMax"
                          type="number"
                          required
                          defaultValue={palierEdite?.dureeMax || 0}
                          className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-zinc-700 mb-1">Prix (FCFA) *</label>
                      <input
                        name="prix"
                        type="number"
                        step="0.01"
                        required
                        defaultValue={palierEdite?.prix || 0}
                        className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-zinc-700 mb-1">Unité *</label>
                      <select
                        name="unite"
                        required
                        defaultValue={palierEdite?.unite || 'minute'}
                        className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                      >
                        <option value="appel">Par appel</option>
                        <option value="minute">Par minute</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-zinc-700 mb-1">Description *</label>
                      <input
                        name="description"
                        type="text"
                        required
                        defaultValue={palierEdite?.description || ''}
                        placeholder="Ex: 0 à 30 secondes"
                        className="w-full px-3 py-2 border border-zinc-300 rounded-lg focus:ring-2 focus:ring-[#e05500] outline-none"
                      />
                    </div>
                  </>
                )}

                <div className="flex items-center gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2.5 bg-[#e05500] hover:bg-[#c44a00] text-white font-semibold rounded-lg transition-colors"
                  >
                    {palierEdite ? 'Enregistrer' : 'Ajouter'}
                  </button>
                  <button
                    type="button"
                    onClick={fermerModal}
                    className="flex-1 px-4 py-2.5 bg-zinc-200 text-zinc-700 font-semibold rounded-lg hover:bg-zinc-300 transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
