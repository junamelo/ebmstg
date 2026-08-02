import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import PasswordInput from '../../components/common/PasswordInput'
import { genererMotDePasseDefaut, genererLoginPayeur, genererLoginEmploye } from '../../utils/passwordUtils'

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
  const [login, setLogin] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [forcerChangement, setForcerChangement] = useState(true)
  const [envoyerEmail, setEnvoyerEmail] = useState(true)

  const ouvrirModal = (type) => {
    setTypeCompte(type)
    setFormData({})
    
    // Générer login et mot de passe par défaut
    if (type === 'PAYEUR') {
      setLogin(genererLoginPayeur())
    } else {
      setLogin('') // Sera généré à partir du numéro de ligne
    }
    setMotDePasse(genererMotDePasseDefaut())
    setForcerChangement(true)
    setEnvoyerEmail(true)
    setModalOuvert(true)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Générer le login pour employé à partir du numéro de ligne
    const loginFinal = typeCompte === 'EMPLOYE' 
      ? genererLoginEmploye(formData.numeroLigne)
      : login
    
    const nouveauCompte = {
      id: String(Date.now()),
      ...formData,
      role: typeCompte,
      login: loginFinal,
      motDePasse: motDePasse, // En production, ce sera hashé côté backend
      doitChangerMotDePasse: forcerChangement,
      estActif: true,
      nbLignes: typeCompte === 'PAYEUR' ? 0 : undefined,
      dateCreation: new Date().toISOString()
    }
    
    setComptes([...comptes, nouveauCompte])
    
    // Simuler l'envoi d'email
    if (envoyerEmail) {
      console.log('📧 Email envoyé à:', formData.email)
      console.log('Login:', loginFinal)
      console.log('Mot de passe temporaire:', motDePasse)
    }
    
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
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] flex flex-col overflow-hidden">
            <div className="p-6 border-b border-zinc-200 dark:border-zinc-800 flex-shrink-0">
              <h3 className="text-xl font-bold text-zinc-900 dark:text-white">
                Créer un compte {typeCompte === 'PAYEUR' ? 'Payeur' : 'Employé'}
              </h3>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto flex-1 overscroll-contain">
              {typeCompte === 'PAYEUR' ? (
                <>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Raison sociale *</label>
                    <input type="text" name="raisonSociale" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg" 
                      onChange={handleChange} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Numéro de contrat *</label>
                    <input type="text" name="numeroContrat" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={handleChange} />
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Nom *</label>
                    <input type="text" name="nom" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={handleChange} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Prénom *</label>
                    <input type="text" name="prenom" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={handleChange} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Numéro de ligne *</label>
                    <input type="text" name="numeroLigne" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={handleChange} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Entreprise *</label>
                    <input type="text" name="entreprise" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                      onChange={handleChange} />
                  </div>
                </>
              )}
              <div>
                <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">Email *</label>
                <input type="email" name="email" required className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg"
                  onChange={handleChange} />
              </div>
              
              {/* Section Identifiants */}
              <div className="border-t border-zinc-200 dark:border-zinc-800 pt-4 mt-2">
                <h4 className="text-sm font-bold text-zinc-900 dark:text-white mb-3 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                    <path d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
                  </svg>
                  Identifiants de connexion
                </h4>
                
                <div>
                  <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
                    Login * {typeCompte === 'EMPLOYE' && '(auto-généré depuis le numéro)'}
                  </label>
                  <input 
                    type="text" 
                    value={typeCompte === 'PAYEUR' ? login : (formData.numeroLigne ? genererLoginEmploye(formData.numeroLigne) : '')}
                    readOnly={typeCompte === 'EMPLOYE'}
                    onChange={(e) => typeCompte === 'PAYEUR' && setLogin(e.target.value)}
                    className="w-full px-4 py-2.5 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-zinc-50 dark:bg-zinc-800 font-mono text-zinc-900 dark:text-white"
                  />
                  {typeCompte === 'PAYEUR' && (
                    <button
                      type="button"
                      onClick={() => setLogin(genererLoginPayeur())}
                      className="mt-2 text-xs text-[#002a7a] hover:text-[#003d9e] font-semibold flex items-center gap-1"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                        <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                      </svg>
                      Regénérer le login
                    </button>
                  )}
                </div>
                
                <PasswordInput
                  value={motDePasse}
                  onChange={setMotDePasse}
                  label="Mot de passe temporaire"
                  showStrength={true}
                  showGenerateButton={true}
                  required={true}
                />
                
                <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p className="text-xs text-blue-700 dark:text-blue-300 flex items-start gap-2">
                    <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
                    </svg>
                    <span>MDP par défaut : <strong>Moov@AAAAMMJJ</strong> (ex: Moov@{new Date().getFullYear()}{String(new Date().getMonth()+1).padStart(2,'0')}{String(new Date().getDate()).padStart(2,'0')})</span>
                  </p>
                </div>
                
                <div className="mt-3 space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={forcerChangement}
                      onChange={(e) => setForcerChangement(e.target.checked)}
                      className="w-4 h-4 rounded border-zinc-300 text-[#002a7a] focus:ring-[#002a7a]"
                    />
                    <span className="text-sm text-zinc-700 dark:text-zinc-300">Forcer changement à la première connexion</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input 
                      type="checkbox"
                      checked={envoyerEmail}
                      onChange={(e) => setEnvoyerEmail(e.target.checked)}
                      className="w-4 h-4 rounded border-zinc-300 text-[#002a7a] focus:ring-[#002a7a]"
                    />
                    <span className="text-sm text-zinc-700 dark:text-zinc-300">Envoyer les identifiants par email</span>
                  </label>
                </div>
              </div>
              
              <div className="flex gap-3 pt-4 flex-shrink-0">
                <button type="submit" className="flex-1 px-4 py-2.5 bg-[#002a7a] text-white font-semibold rounded-lg hover:bg-[#003d9e] transition-colors">
                  Créer
                </button>
                <button type="button" onClick={() => setModalOuvert(false)} className="flex-1 px-4 py-2.5 bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-semibold rounded-lg hover:bg-zinc-300 dark:hover:bg-zinc-700 transition-colors">
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
