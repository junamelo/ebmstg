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

          <div className="bg-white rounded-xl border border-zinc-200 overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-zinc-100 bg-zinc-50">
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-zinc-500">Palier</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-zinc-500">Tranche</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-zinc-500">Prix</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-zinc-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {paliersData.map((palier, idx) => (
                  <motion.tr
                    key={palier.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.04 }}
                    className="hover:bg-zinc-50 transition-colors"
                  >
                    <td className="px-5 py-3.5">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md bg-zinc-100 text-zinc-700 text-xs font-semibold">
                        #{idx + 1}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-zinc-700">{palier.description}</td>
                    <td className="px-5 py-3.5 text-right">
                      <span className="text-sm font-bold text-zinc-900">
                        {palier.prix.toLocaleString('fr-FR')}
                      </span>
                      <span className="text-xs text-zinc-500 ml-1">{palier.prixParMo ? 'F/Mo' : 'FCFA'}</span>
                      {palier.prixParMo && (
                        <p className="text-xs text-zinc-400 mt-0.5">+ 50 000 F base</p>
                      )}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button onClick={() => ouvrirModal(palier)}
                          className="px-2.5 py-1 text-xs font-medium text-zinc-600 border border-zinc-200 rounded-md hover:bg-zinc-100 transition-colors">
                          Modifier
                        </button>
                        <button onClick={() => handleSupprimerPalier(palier.id)}
                          className="px-2.5 py-1 text-xs font-medium text-red-600 border border-red-200 rounded-md hover:bg-red-50 transition-colors">
                          Suppr.
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
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

          <div className="bg-white rounded-xl border border-zinc-200 overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-zinc-100 bg-zinc-50">
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-zinc-500">Tarif</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-zinc-500">Tranche</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-zinc-500">Prix</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-zinc-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {tarifsVoix.map((tarif, idx) => (
                  <motion.tr
                    key={tarif.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.04 }}
                    className="hover:bg-zinc-50 transition-colors"
                  >
                    <td className="px-5 py-3.5">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md bg-zinc-100 text-zinc-700 text-xs font-semibold">
                        #{idx + 1}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-zinc-700">{tarif.description}</td>
                    <td className="px-5 py-3.5 text-right">
                      <span className="text-sm font-bold text-zinc-900">
                        {tarif.prix.toLocaleString('fr-FR')}
                      </span>
                      <span className="text-xs text-zinc-500 ml-1">F/{tarif.unite}</span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button onClick={() => ouvrirModal(tarif)}
                          className="px-2.5 py-1 text-xs font-medium text-zinc-600 border border-zinc-200 rounded-md hover:bg-zinc-100 transition-colors">
                          Modifier
                        </button>
                        <button onClick={() => handleSupprimerPalier(tarif.id)}
                          className="px-2.5 py-1 text-xs font-medium text-red-600 border border-red-200 rounded-md hover:bg-red-50 transition-colors">
                          Suppr.
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bg-zinc-50 border border-zinc-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <svg className="w-4 h-4 text-zinc-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
              </svg>
              <div>
                <p className="text-xs font-semibold text-zinc-600 mb-0.5">Règle de facturation</p>
                <p className="text-xs text-zinc-500">
                  Appel 1 min 20s = 79 F + (79 F / 2) = 118,50 F &nbsp;|&nbsp; Appel 1 min 40s = 79 F x 2 = 158 F
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

          <div className="max-w-sm">
            <form onSubmit={handleSauvegarderTarifSMS} className="bg-white rounded-xl border border-zinc-200 p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-zinc-700 mb-1.5">
                  Prix unitaire (FCFA) *
                </label>
                <input
                  name="prix"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  defaultValue={tarifSMS.prix}
                  className="w-full px-3 py-2 border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-[#e05500] outline-none"
                />
              </div>

              <div className="flex items-baseline gap-2 p-4 bg-zinc-50 rounded-lg border border-zinc-100">
                <span className="text-2xl font-bold text-zinc-900">{tarifSMS.prix}</span>
                <span className="text-sm text-zinc-500">FCFA / SMS</span>
              </div>

              <button
                type="submit"
                className="w-full px-4 py-2.5 bg-[#e05500] hover:bg-[#c44a00] text-white font-semibold rounded-lg transition-colors text-sm"
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
          <div className="fixed inset-0 z-[1100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.96 }}
              className="bg-white rounded-2xl shadow-2xl w-full max-w-lg"
            >
              <div className="px-6 py-4 border-b border-zinc-200 flex items-center justify-between">
                <h3 className="text-base font-semibold text-zinc-900">
                  {palierEdite ? `Modifier ${serviceActif === 'DATA' ? 'le palier' : 'le tarif'}` : `Ajouter un ${serviceActif === 'DATA' ? 'palier' : 'tarif'} ${serviceActif}`}
                </h3>
                <button type="button" onClick={fermerModal}
                  className="w-7 h-7 flex items-center justify-center rounded-md hover:bg-zinc-100 text-zinc-400 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
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
