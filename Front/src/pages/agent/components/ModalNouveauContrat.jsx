import { useState } from 'react'
import { motion } from 'motion/react'

export default function ModalNouveauContrat({ onClose, onCreate }) {
  const [typePayeur, setTypePayeur] = useState('ENTREPRISE')
  const [formData, setFormData] = useState({
    typeContrat: 'Professionnel',
    dureeEngagement: 12,
    modeFacturation: 'Mensuel',
    statut: 'ACTIF'
  })

  const genererNumeroContrat = () => {
    const annee = new Date().getFullYear().toString().slice(-2)
    const sequence = Math.floor(Math.random() * 999999).toString().padStart(6, '0')
    return `A${annee}${sequence}`
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    const nouveauContrat = {
      ...formData,
      typePayeur,
      numeroContrat: genererNumeroContrat(),
      dateCreation: new Date().toISOString().split('T')[0],
      lignes: [],
      caMensuel: 0
    }
    
    onCreate(nouveauContrat)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[1100] p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 p-6 z-10">
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-bold text-zinc-900 dark:text-white">Créer un Nouveau Contrat</h3>
            <button onClick={onClose} className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Type de payeur */}
          <div>
            <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-3">Type de compte *</label>
            <div className="grid grid-cols-2 gap-4">
              <button type="button" onClick={() => setTypePayeur('ENTREPRISE')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  typePayeur === 'ENTREPRISE'
                    ? 'border-[#002a7a] bg-[#002a7a]/5'
                    : 'border-zinc-300 dark:border-zinc-700 hover:border-zinc-400'
                }`}>
                <div className="text-2xl mb-2">🏢</div>
                <p className="font-bold text-zinc-900 dark:text-white">Entreprise</p>
                <p className="text-xs text-zinc-500">Plusieurs lignes</p>
              </button>
              <button type="button" onClick={() => setTypePayeur('PARTICULIER')}
                className={`p-4 rounded-lg border-2 transition-all ${
                  typePayeur === 'PARTICULIER'
                    ? 'border-[#002a7a] bg-[#002a7a]/5'
                    : 'border-zinc-300 dark:border-zinc-700 hover:border-zinc-400'
                }`}>
                <div className="text-2xl mb-2">👤</div>
                <p className="font-bold text-zinc-900 dark:text-white">Particulier</p>
                <p className="text-xs text-zinc-500">Une seule ligne</p>
              </button>
            </div>
          </div>

          {/* Formulaire Entreprise */}
          {typePayeur === 'ENTREPRISE' && (
            <>
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Raison sociale *</label>
                <input type="text" name="raisonSociale" required value={formData.raisonSociale || ''}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none"/>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Email *</label>
                  <input type="email" name="email" required value={formData.email || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none"/>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Téléphone *</label>
                  <input type="tel" name="telephone" required value={formData.telephone || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none"/>
                </div>
              </div>
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Adresse</label>
                <input type="text" name="adresse" value={formData.adresse || ''}
                  onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none"/>
              </div>
            </>
          )}

          {/* Formulaire Particulier */}
          {typePayeur === 'PARTICULIER' && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Nom *</label>
                  <input type="text" name="nom" required value={formData.nom || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none"/>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Prénom *</label>
                  <input type="text" name="prenom" required value={formData.prenom || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none"/>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Email *</label>
                  <input type="email" name="email" required value={formData.email || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none"/>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Téléphone *</label>
                  <input type="tel" name="telephone" required value={formData.telephone || ''}
                    onChange={handleChange}
                    className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none"/>
                </div>
              </div>
            </>
          )}

          {/* Configuration du contrat */}
          <div className="border-t border-zinc-200 dark:border-zinc-800 pt-6">
            <h4 className="text-lg font-bold text-zinc-900 dark:text-white mb-4">Configuration du Contrat</h4>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Type de contrat *</label>
                <select name="typeContrat" value={formData.typeContrat} onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none">
                  <option value="Particulier">Particulier</option>
                  <option value="Professionnel">Professionnel</option>
                  <option value="Entreprise">Entreprise</option>
                  <option value="Corporate">Corporate</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Durée engagement (mois)</label>
                <select name="dureeEngagement" value={formData.dureeEngagement} onChange={handleChange}
                  className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none">
                  <option value="0">Sans engagement</option>
                  <option value="12">12 mois</option>
                  <option value="24">24 mois</option>
                  <option value="36">36 mois</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Mode de facturation</label>
              <select name="modeFacturation" value={formData.modeFacturation} onChange={handleChange}
                className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 focus:ring-2 focus:ring-[#002a7a] outline-none">
                <option value="Mensuel">Mensuel</option>
                <option value="Trimestriel">Trimestriel</option>
                <option value="Annuel">Annuel</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={onClose}
              className="flex-1 px-4 py-2.5 bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-lg hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-colors">
              Annuler
            </button>
            <button type="submit"
              className="flex-1 px-4 py-2.5 bg-gradient-to-br from-[#002a7a] to-[#003d9e] text-white font-semibold rounded-lg hover:shadow-lg transition-all">
              Créer le Contrat
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}
