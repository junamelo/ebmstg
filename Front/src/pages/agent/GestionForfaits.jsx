import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import { getPackages, togglePackageActif, createPackage, updatePackage } from '../../services/packageService'

export default function GestionForfaits() {
  const [packages, setPackages] = useState([])
  const [chargement, setChargement] = useState(true)
  const [erreur, setErreur] = useState(null)
  const [modalOuvert, setModalOuvert] = useState(false)
  const [packageEdite, setPackageEdite] = useState(null)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    chargerPackages()
  }, [])

  const chargerPackages = async () => {
    try {
      setChargement(true)
      setErreur(null)
      const data = await getPackages()
      setPackages(data)
    } catch (error) {
      console.error('Erreur chargement packages:', error)
      setErreur('Impossible de charger les forfaits')
    } finally {
      setChargement(false)
    }
  }

  const handleToggleActif = async (id) => {
    try {
      await togglePackageActif(id)
      showMessage('success', 'Statut modifié avec succès')
      chargerPackages()
    } catch (error) {
      showMessage('error', 'Erreur lors de la modification')
    }
  }

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 3000)
  }

  const ouvrirModal = (pkg = null) => {
    setPackageEdite(pkg)
    setModalOuvert(true)
  }

  const fermerModal = () => {
    setModalOuvert(false)
    setPackageEdite(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const formData = new FormData(e.target)
    const data = {
      nom: formData.get('nom'),
      code: formData.get('code'),
      prix_mensuel: parseFloat(formData.get('prix_mensuel')),
      type_forfait: formData.get('type_forfait'),
      quota_data_mo: parseInt(formData.get('quota_data_mo')) || 0,
      quota_minutes: parseInt(formData.get('quota_minutes')) || 0,
      quota_sms: parseInt(formData.get('quota_sms')) || 0,
      est_actif: formData.get('est_actif') === 'true'
    }

    try {
      if (packageEdite) {
        await updatePackage(packageEdite.id, data)
        showMessage('success', 'Forfait modifié avec succès')
      } else {
        await createPackage(data)
        showMessage('success', 'Forfait créé avec succès')
      }
      fermerModal()
      chargerPackages()
    } catch (error) {
      showMessage('error', 'Erreur lors de l\'enregistrement')
    }
  }

  if (chargement) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-zinc-300 border-t-[#002a7a] rounded-full animate-spin" />
          <span className="text-sm text-zinc-600">Chargement des forfaits...</span>
        </div>
      </div>
    )
  }

  if (erreur) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{erreur}</p>
          <button
            onClick={chargerPackages}
            className="px-4 py-2 bg-[#002a7a] text-white rounded-lg hover:bg-[#003399]"
          >
            Réessayer
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Message */}
      {message && (
        <div className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg ${
          message.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        }`}>
          {message.text}
        </div>
      )}

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-white mb-2">
              Gestion des Forfaits
            </h1>
            <p className="text-zinc-600 dark:text-zinc-400">
              {packages.length} forfait(s) disponible(s)
            </p>
          </div>
          <button
            onClick={() => ouvrirModal()}
            className="px-4 py-2.5 bg-[#002a7a] hover:bg-[#003d9e] text-white font-semibold rounded-lg transition-colors"
          >
            + Nouveau forfait
          </button>
        </div>
      </motion.div>

      {/* Liste des forfaits */}
      {packages.length === 0 ? (
        <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-12 text-center">
          <p className="text-zinc-500 dark:text-zinc-400 mb-4">Aucun forfait disponible</p>
          <button
            onClick={() => ouvrirModal()}
            className="px-4 py-2 bg-[#002a7a] text-white rounded-lg hover:bg-[#003399]"
          >
            Créer le premier forfait
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {packages.map((pkg, idx) => (
            <motion.div
              key={pkg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-zinc-900 dark:text-white mb-1">
                    {pkg.nom}
                  </h3>
                  <p className="text-sm text-zinc-500 font-mono">{pkg.code}</p>
                </div>
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                  pkg.est_actif 
                    ? 'bg-emerald-100 text-emerald-700' 
                    : 'bg-zinc-100 text-zinc-600'
                }`}>
                  {pkg.est_actif ? 'Actif' : 'Inactif'}
                </span>
              </div>

              <div className="mb-4">
                <p className="text-3xl font-bold text-[#002a7a] dark:text-blue-400">
                  {pkg.prix_mensuel.toLocaleString('fr-FR')} F
                </p>
                <p className="text-sm text-zinc-500">/ mois</p>
              </div>

              <div className="space-y-2 mb-4 text-sm">
                {pkg.quota_data_mo > 0 && (
                  <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                    </svg>
                    {(pkg.quota_data_mo / 1024).toFixed(1)} Go Data
                  </div>
                )}
                {pkg.quota_minutes > 0 && (
                  <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                    </svg>
                    {pkg.quota_minutes} min Voix
                  </div>
                )}
                {pkg.quota_sms > 0 && (
                  <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                      <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
                    </svg>
                    {pkg.quota_sms} SMS
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => ouvrirModal(pkg)}
                  className="flex-1 px-3 py-2 bg-zinc-100 hover:bg-zinc-200 dark:bg-zinc-800 dark:hover:bg-zinc-700 text-zinc-700 dark:text-zinc-300 font-medium rounded-lg text-sm transition-colors"
                >
                  Modifier
                </button>
                <button
                  onClick={() => handleToggleActif(pkg.id)}
                  className={`flex-1 px-3 py-2 font-medium rounded-lg text-sm transition-colors ${
                    pkg.est_actif
                      ? 'bg-zinc-200 hover:bg-zinc-300 text-zinc-700'
                      : 'bg-emerald-600 hover:bg-emerald-700 text-white'
                  }`}
                >
                  {pkg.est_actif ? 'Désactiver' : 'Activer'}
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Modal création/édition */}
      {modalOuvert && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          >
            <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
              <h3 className="text-xl font-bold text-zinc-900 dark:text-white">
                {packageEdite ? 'Modifier le forfait' : 'Nouveau forfait'}
              </h3>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Nom du forfait *
                  </label>
                  <input
                    name="nom"
                    required
                    defaultValue={packageEdite?.nom}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Code *
                  </label>
                  <input
                    name="code"
                    required
                    defaultValue={packageEdite?.code}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Prix mensuel (F) *
                  </label>
                  <input
                    name="prix_mensuel"
                    type="number"
                    step="0.01"
                    required
                    defaultValue={packageEdite?.prix_mensuel}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Type de forfait *
                  </label>
                  <select
                    name="type_forfait"
                    required
                    defaultValue={packageEdite?.type_forfait || 'MIXTE'}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  >
                    <option value="DATA">Data</option>
                    <option value="VOIX">Voix</option>
                    <option value="SMS">SMS</option>
                    <option value="MIXTE">Mixte (Voix + SMS + Data)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Quota Data (Mo)
                  </label>
                  <input
                    name="quota_data_mo"
                    type="number"
                    defaultValue={packageEdite?.quota_data_mo || 0}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Quota Voix (min)
                  </label>
                  <input
                    name="quota_minutes"
                    type="number"
                    defaultValue={packageEdite?.quota_minutes || 0}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Quota SMS
                  </label>
                  <input
                    name="quota_sms"
                    type="number"
                    defaultValue={packageEdite?.quota_sms || 0}
                    className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                  Statut
                </label>
                <select
                  name="est_actif"
                  defaultValue={packageEdite?.est_actif ? 'true' : 'false'}
                  className="w-full px-4 py-2.5 bg-white dark:bg-zinc-800 border border-zinc-300 dark:border-zinc-700 rounded-lg focus:ring-2 focus:ring-[#002a7a] outline-none"
                >
                  <option value="true">Actif</option>
                  <option value="false">Inactif</option>
                </select>
              </div>

              <div className="flex items-center gap-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2.5 bg-[#002a7a] hover:bg-[#003d9e] text-white font-semibold rounded-lg transition-colors"
                >
                  {packageEdite ? 'Enregistrer' : 'Créer'}
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
