import { useState } from 'react'
import { motion } from 'motion/react'

export default function GestionComptesClients() {
  const [comptes, setComptes] = useState([
    {
      id: '2',
      raisonSociale: 'BIOSPARTNERS',
      numeroContrat: 'A0007612',
      email: 'tg@biospartnership.com',
      role: 'PAYEUR',
      estActif: true,
      nbLignes: 3
    },
    {
      id: '3',
      nom: 'TOTSOVI',
      prenom: 'Eyram',
      numeroLigne: '79 34 27 35',
      email: 'e.totsovi@biospartners.com',
      entreprise: 'BIOSPARTNERS',
      role: 'EMPLOYE',
      estActif: true
    }
  ])

  const [modalOuvert, setModalOuvert] = useState(false)
  const [typeCompte, setTypeCompte] = useState('PAYEUR')
  const [formData, setFormData] = useState({})

  const ouvrirModal = (type) => {
    setTypeCompte(type)
    setFormData({})
    setModalOuvert(true)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const nouveauCompte = {
      id: String(Date.now()),
      ...formData,
      role: typeCompte,
      estActif: true,
      nbLignes: typeCompte === 'PAYEUR' ? 0 : undefined
    }
    setComptes([...comptes, nouveauCompte])
    setModalOuvert(false)
    setFormData({})
  }

  return (
    <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-white mb-2">Gestion des Comptes Clients</h1>
          <p className="text-zinc-600 dark:text-zinc-400">Créez et gérez les comptes Payeurs et Employés</p>
        </div>
        <div className="flex gap-3">
          <button onClick={() => ouvrirModal('PAYEUR')} className="px-4 py-2.5 bg-gradient-to-br from-[#e05500] to-[#c2410c] text-white font-semibold rounded-lg hover:shadow-lg">
            + Nouveau Payeur
          </button>
          <button onClick={() => ouvrirModal('EMPLOYE')} className="px-4 py-2.5 bg-gradient-to-br from-[#002a7a] to-[#003d9e] text-white font-semibold rounded-lg hover:shadow-lg">
            + Nouvel Employé
          </button>
        </div>
      </motion.div>

      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 overflow-hidden">
        <table className="w-full">
          <thead className="bg-zinc-50 dark:bg-zinc-900/50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Identifiant</th>
              <th className="px-6 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Email</th>
              <th className="px-6 py-3 text-left text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Type</th>
              <th className="px-6 py-3 text-center text-xs font-bold uppercase text-zinc-700 dark:text-zinc-300">Statut</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
            {comptes.map((compte) => (
              <tr key={compte.id} className="hover:bg-zinc-50 dark:hover:bg-zinc-800/40">
                <td className="px-6 py-4">
                  <p className="font-semibold text-zinc-900 dark:text-white">
                    {compte.raisonSociale || `${compte.prenom} ${compte.nom}`}
                  </p>
                  <p className="text-sm text-zinc-500">{compte.numeroContrat || compte.numeroLigne}</p>
                </td>
                <td className="px-6 py-4 text-sm text-zinc-600 dark:text-zinc-400">{compte.email}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                    compte.role === 'PAYEUR' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'
                  }`}>
                    {compte.role === 'PAYEUR' ? 'Payeur' : 'Employé'}
                  </span>
                </td>
                <td className="px-6 py-4 text-center">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                    compte.estActif ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {compte.estActif ? 'Actif' : 'Inactif'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modalOuvert && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-md w-full">
            <div className="p-6 border-b border-zinc-200 dark:border-zinc-800">
              <h3 className="text-xl font-bold text-zinc-900 dark:text-white">
                Créer un compte {typeCompte === 'PAYEUR' ? 'Payeur' : 'Employé'}
              </h3>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {typeCompte === 'PAYEUR' ? (
                <>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Raison sociale *</label>
                    <input type="text" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg" 
                      onChange={(e) => setFormData({...formData, raisonSociale: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Numéro de contrat *</label>
                    <input type="text" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={(e) => setFormData({...formData, numeroContrat: e.target.value})} />
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Nom *</label>
                    <input type="text" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={(e) => setFormData({...formData, nom: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Prénom *</label>
                    <input type="text" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={(e) => setFormData({...formData, prenom: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Numéro de ligne *</label>
                    <input type="text" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={(e) => setFormData({...formData, numeroLigne: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Entreprise *</label>
                    <input type="text" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={(e) => setFormData({...formData, entreprise: e.target.value})} />
                  </div>
                </>
              )}
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Email *</label>
                <input type="email" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                  onChange={(e) => setFormData({...formData, email: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Mot de passe *</label>
                <input type="password" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                  onChange={(e) => setFormData({...formData, motDePasse: e.target.value})} />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="submit" className="flex-1 px-4 py-2.5 bg-[#002a7a] text-white font-semibold rounded-lg hover:bg-[#003d9e]">
                  Créer
                </button>
                <button type="button" onClick={() => setModalOuvert(false)} className="flex-1 px-4 py-2.5 bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-lg">
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
