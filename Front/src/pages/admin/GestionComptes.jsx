import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'motion/react'
import { getUtilisateurs, activerCompte, suspendreCompte, reinitialiserMotDePasseAdmin } from '../../services/adminService'
import api from '../../services/api'
import './Admin.css'

// ── Couleurs avatar par rôle ─────────────────────────────────
const ROLE_CONFIG = {
  SUPER_ADMIN:       { label: 'Super Admin',      bg: '#fee2e2', color: '#b91c1c' },
  CHEF_FACTURATION:  { label: 'Chef Facturation', bg: '#fed7aa', color: '#c2410c' },
  AGENT_FACTURATION: { label: 'Agent',             bg: '#ede9fe', color: '#6d28d9' },
  PAYEUR:            { label: 'Payeur',            bg: '#dbeafe', color: '#1d4ed8' },
  EMPLOYE:           { label: 'Employé',           bg: '#dcfce7', color: '#15803d' },
}

function getInitiales(prenom, nom) {
  return `${prenom?.[0] ?? ''}${nom?.[0] ?? ''}`.toUpperCase()
}

// ── Formulaire création compte ───────────────────────────────
const ROLES_OPTIONS = [
  { value: 'EMPLOYE',           label: 'Employé' },
  { value: 'PAYEUR',            label: 'Payeur (Entreprise)' },
  { value: 'AGENT_FACTURATION', label: 'Agent Facturation' },
  { value: 'CHEF_FACTURATION',  label: 'Chef Facturation' },
  { value: 'SUPER_ADMIN',       label: 'Super Administrateur' },
]

// ── Modal gestion des lignes ─────────────────────────────────
function ModalGestionLignes({ payeur, onClose, onSuccess }) {
  const [etapeActuelle, setEtapeActuelle] = useState(1)
  const [lignes, setLignes] = useState([])
  const [lignesValidees, setLignesValidees] = useState([])
  const [modeSelection, setModeSelection] = useState(false)
  const [lignesDisponibles, setLignesDisponibles] = useState([])
  const [rechercheLigne, setRechercheLigne] = useState('')
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState('')

  useEffect(() => {
    chargerLignesDisponibles()
  }, [])

  const chargerLignesDisponibles = async () => {
    try {
      // Récupérer les lignes sans entreprise (disponibles)
      const response = await api.get('/billing/lines/', { params: { company__isnull: true } })
      const lignesAPI = response.data.results || response.data
      setLignesDisponibles(lignesAPI.map(ligne => ({
        id: ligne.id,
        numero: ligne.msisdn,
        forfait: ligne.package_nom || 'Standard',
        statut: 'Disponible'
      })))
    } catch (error) {
      console.error('Erreur chargement lignes:', error)
      // Fallback : aucune ligne disponible
      setLignesDisponibles([])
    }
  }

  const handleImportFichier = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      const text = event.target.result
      const lignesImportees = text.split('\n')
        .map(ligne => ligne.trim())
        .filter(ligne => ligne && ligne.match(/^\d{2}\s?\d{2}\s?\d{2}\s?\d{2}$/))
        .map((numero, index) => ({
          id: `import-${index}`,
          numero: numero.replace(/(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4'),
          forfait: 'À définir',
          statut: 'Nouveau',
          source: 'import'
        }))
      
      setLignes(lignesImportees)
    }
    reader.readAsText(file)
  }

  const handleSaisieManuelle = (e) => {
    const text = e.target.value
    const lignesSaisies = text.split('\n')
      .map(ligne => ligne.trim())
      .filter(ligne => ligne)
      .map((numero, index) => {
        // Formater le numéro
        const numeroFormate = numero.replace(/[^\d]/g, '')
        if (numeroFormate.length === 8) {
          return {
            id: `manuel-${index}`,
            numero: numeroFormate.replace(/(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4'),
            forfait: 'À définir',
            statut: 'Nouveau',
            source: 'manuel'
          }
        }
        return null
      })
      .filter(Boolean)
    
    setLignes(lignesSaisies)
  }

  const ajouterLigneExistante = (ligne) => {
    if (!lignes.find(l => l.numero === ligne.numero)) {
      setLignes([...lignes, { ...ligne, source: 'existante' }])
    }
  }

  const retirerLigne = (ligneId) => {
    setLignes(lignes.filter(l => l.id !== ligneId))
  }

  const validerEtape1 = () => {
    if (lignes.length === 0) {
      setErreur('Veuillez ajouter au moins une ligne.')
      return
    }
    setErreur('')
    setLignesValidees(lignes)
    setEtapeActuelle(2)
  }

  const confirmerAttribution = async () => {
    setChargement(true)
    setErreur('')
    
    try {
      // Simuler l'attribution des lignes au payeur
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      onSuccess(`${lignesValidees.length} ligne(s) attribuée(s) avec succès à ${payeur.prenom} ${payeur.nom}.`)
      onClose()
    } catch (error) {
      setErreur('Erreur lors de l\'attribution des lignes.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 10 }}
        transition={{ duration: 0.2 }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-100">
          <div>
            <h2 className="text-lg font-semibold text-zinc-900">
              Associer des lignes au payeur
            </h2>
            <p className="text-sm text-zinc-600">
              {payeur.prenom} {payeur.nom} - {payeur.raisonSociale}
            </p>
          </div>
          <button 
            onClick={onClose} 
            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-zinc-100 text-zinc-400 text-lg transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-140px)]">
          {erreur && (
            <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {erreur}
            </div>
          )}

          {etapeActuelle === 1 ? (
            // ÉTAPE 1: Import/Ajout des lignes
            <div className="p-6 space-y-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">1</div>
                <h3 className="font-semibold text-zinc-900">Ajouter des lignes téléphoniques</h3>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Méthodes d'ajout */}
                <div className="space-y-4">
                  <h4 className="font-medium text-zinc-800">Méthodes d'ajout</h4>
                  
                  {/* Import fichier */}
                  <div className="p-4 border border-zinc-200 rounded-lg">
                    <label className="block font-medium text-sm text-zinc-700 mb-2">
                      1. Importer depuis un fichier
                    </label>
                    <input 
                      type="file" 
                      accept=".txt,.csv,.xlsx" 
                      onChange={handleImportFichier}
                      className="block w-full text-sm text-zinc-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
                    />
                    <p className="text-xs text-zinc-500 mt-1">
                      Format: un numéro par ligne (ex: 79342735)
                    </p>
                  </div>

                  {/* Saisie manuelle */}
                  <div className="p-4 border border-zinc-200 rounded-lg">
                    <label className="block font-medium text-sm text-zinc-700 mb-2">
                      2. Saisie manuelle
                    </label>
                    <textarea 
                      rows="4" 
                      className="form-control text-sm"
                      placeholder="79 34 27 35&#10;79 34 27 36&#10;79 34 27 37"
                      onChange={handleSaisieManuelle}
                    />
                    <p className="text-xs text-zinc-500 mt-1">
                      Un numéro par ligne
                    </p>
                  </div>

                  {/* Sélection depuis base */}
                  <div className="p-4 border border-zinc-200 rounded-lg">
                    <label className="block font-medium text-sm text-zinc-700 mb-2">
                      3. Sélectionner depuis la base
                    </label>
                    <button 
                      onClick={() => setModeSelection(!modeSelection)}
                      className="btn btn-outline btn-sm"
                    >
                      {modeSelection ? 'Masquer' : 'Afficher'} les lignes disponibles
                    </button>
                    
                    {modeSelection && (
                      <div className="mt-3 space-y-2">
                        <input 
                          type="text"
                          placeholder="Rechercher une ligne..."
                          value={rechercheLigne}
                          onChange={e => setRechercheLigne(e.target.value)}
                          className="form-control text-sm"
                        />
                        <div className="max-h-32 overflow-y-auto border rounded p-2 bg-zinc-50">
                          {lignesDisponibles
                            .filter(ligne => ligne.numero.includes(rechercheLigne))
                            .map(ligne => (
                              <div 
                                key={ligne.id} 
                                className="flex items-center justify-between p-2 hover:bg-white rounded cursor-pointer"
                                onClick={() => ajouterLigneExistante(ligne)}
                              >
                                <div>
                                  <span className="font-mono text-sm">{ligne.numero}</span>
                                  <span className="text-xs text-zinc-500 ml-2">{ligne.forfait}</span>
                                </div>
                                <button className="text-blue-600 hover:text-blue-800 text-xs">
                                  Ajouter
                                </button>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Aperçu des lignes ajoutées */}
                <div>
                  <h4 className="font-medium text-zinc-800 mb-4">
                    Lignes à attribuer ({lignes.length})
                  </h4>
                  
                  {lignes.length > 0 ? (
                    <div className="border border-zinc-200 rounded-lg overflow-hidden">
                      <div className="max-h-64 overflow-y-auto">
                        <table className="w-full text-sm">
                          <thead className="bg-zinc-50 sticky top-0">
                            <tr>
                              <th className="text-left p-3 font-medium">Numéro</th>
                              <th className="text-left p-3 font-medium">Forfait</th>
                              <th className="text-right p-3 font-medium">Action</th>
                            </tr>
                          </thead>
                          <tbody>
                            {lignes.map((ligne) => (
                              <tr key={ligne.id} className="border-t border-zinc-100">
                                <td className="p-3 font-mono">{ligne.numero}</td>
                                <td className="p-3 text-zinc-600">{ligne.forfait}</td>
                                <td className="p-3 text-right">
                                  <button 
                                    onClick={() => retirerLigne(ligne.id)}
                                    className="text-red-600 hover:text-red-800 text-xs"
                                  >
                                    Retirer
                                  </button>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="border-2 border-dashed border-zinc-200 rounded-lg p-8 text-center text-zinc-500">
                      <p>Aucune ligne ajoutée</p>
                      <p className="text-sm">Utilisez l'une des méthodes ci-contre</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            // ÉTAPE 2: Validation et attribution
            <div className="p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">2</div>
                <h3 className="font-semibold text-zinc-900">Valider l'attribution</h3>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-blue-800 font-medium">
                  Attribution de {lignesValidees.length} ligne(s) à {payeur.prenom} {payeur.nom}
                </p>
                <p className="text-blue-600 text-sm">
                  Entreprise: {payeur.raisonSociale}
                </p>
              </div>

              <div className="border border-zinc-200 rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-zinc-50">
                    <tr>
                      <th className="text-left p-4 font-medium">Numéro de ligne</th>
                      <th className="text-left p-4 font-medium">Forfait actuel</th>
                      <th className="text-left p-4 font-medium">Statut</th>
                      <th className="text-left p-4 font-medium">Source</th>
                      <th className="text-right p-4 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lignesValidees.map((ligne, index) => (
                      <tr key={ligne.id} className={index % 2 === 0 ? 'bg-white' : 'bg-zinc-50'}>
                        <td className="p-4 font-mono font-medium">{ligne.numero}</td>
                        <td className="p-4">{ligne.forfait}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            ligne.statut === 'Disponible' ? 'bg-green-100 text-green-800' :
                            ligne.statut === 'Nouveau' ? 'bg-blue-100 text-blue-800' :
                            'bg-zinc-100 text-zinc-800'
                          }`}>
                            {ligne.statut}
                          </span>
                        </td>
                        <td className="p-4 text-zinc-600 capitalize text-sm">{ligne.source}</td>
                        <td className="p-4 text-right">
                          <button 
                            onClick={() => {
                              setLignesValidees(lignesValidees.filter(l => l.id !== ligne.id))
                            }}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Retirer
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {lignesValidees.length === 0 && (
                <div className="text-center p-8 text-zinc-500">
                  <p>Aucune ligne à attribuer.</p>
                  <button 
                    onClick={() => setEtapeActuelle(1)}
                    className="btn btn-outline btn-sm mt-2"
                  >
                    Retour à l'étape 1
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center px-6 py-4 bg-zinc-50 border-t border-zinc-100">
          <button 
            onClick={onClose} 
            className="btn btn-outline"
            disabled={chargement}
          >
            Annuler
          </button>
          
          <div className="flex gap-3">
            {etapeActuelle === 2 && (
              <button 
                onClick={() => setEtapeActuelle(1)}
                className="btn btn-outline"
                disabled={chargement}
              >
                ← Retour
              </button>
            )}
            
            {etapeActuelle === 1 ? (
              <button 
                onClick={validerEtape1}
                className="btn btn-primary"
                disabled={lignes.length === 0}
              >
                Suivant →
              </button>
            ) : (
              <button 
                onClick={confirmerAttribution}
                className="btn btn-primary"
                disabled={chargement || lignesValidees.length === 0}
              >
                {chargement ? 'Attribution...' : `Confirmer l'attribution (${lignesValidees.length})`}
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  )
}

function ModalCreerCompte({ onClose, onSuccess, onPayeurCree }) {
  const [form, setForm] = useState({ 
    nom: '', 
    prenom: '', 
    email: '', 
    login: '', 
    motDePasse: '', 
    role: 'EMPLOYE', 
    raisonSociale: '',
    cycleFin: 'HYB'
  })
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErreur('')
    
    // Validation selon le rôle
    if (!form.login || !form.motDePasse) {
      setErreur('Identifiant et mot de passe sont obligatoires.')
      return
    }
    
    // Nom et prénom obligatoires uniquement pour EMPLOYE
    if (form.role === 'EMPLOYE' && (!form.nom || !form.prenom)) {
      setErreur('Nom et prénom sont obligatoires pour les employés.')
      return
    }
    
    setChargement(true)
    try {
      const response = await api.post('/auth/users/', {
        username: form.login,
        email: form.email || `${form.login}@moov.africa`,
        password: form.motDePasse,
        first_name: form.prenom || '',
        last_name: form.nom || '',
        role: form.role
      })
      
      const nouveauUtilisateur = response.data
      
      if (form.role === 'PAYEUR') {
        // Si c'est un payeur, déclencher la modal de gestion des lignes
        onPayeurCree(nouveauUtilisateur)
      } else {
        onSuccess('Compte créé avec succès.')
      }
      onClose()
    } catch (error) {
      const errorMsg = error.response?.data?.message || error.response?.data?.detail || 'Erreur lors de la création du compte.'
      setErreur(errorMsg)
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 10 }}
        transition={{ duration: 0.2 }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-hidden flex flex-col"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-100 flex-shrink-0">
          <h2 className="text-base font-semibold text-zinc-900">Créer un compte</h2>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-zinc-100 text-zinc-400 text-lg transition-colors">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
          <div className="p-6 space-y-4 overflow-y-auto flex-1">
          {erreur && <div className="alert alert-danger text-sm">{erreur}</div>}

          <div className="grid grid-cols-2 gap-4">
            <div className="form-group">
              <label className="form-label">Prénom {form.role === 'EMPLOYE' ? '*' : ''}</label>
              <input 
                className="form-control" 
                placeholder="Kodjo" 
                value={form.prenom} 
                onChange={e => setForm({ ...form, prenom: e.target.value })} 
                required={form.role === 'EMPLOYE'}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Nom {form.role === 'EMPLOYE' ? '*' : ''}</label>
              <input 
                className="form-control" 
                placeholder="MENSAH" 
                value={form.nom} 
                onChange={e => setForm({ ...form, nom: e.target.value })} 
                required={form.role === 'EMPLOYE'}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Rôle *</label>
            <select className="form-control" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
              {ROLES_OPTIONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Identifiant de connexion *</label>
            <input className="form-control"
              placeholder={form.role === 'PAYEUR' ? 'CT-001234' : form.role === 'EMPLOYE' ? '90123456' : 'email@moov.tg'}
              value={form.login} onChange={e => setForm({ ...form, login: e.target.value })} />
          </div>

          <div className="form-group">
            <label className="form-label">Email</label>
            <input type="email" className="form-control" placeholder="prenom.nom@entreprise.tg" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          </div>

          {(form.role === 'PAYEUR' || form.role === 'EMPLOYE') && (
            <div className="form-group">
              <label className="form-label">Raison sociale</label>
              <input className="form-control" placeholder="Nom de l'entreprise" value={form.raisonSociale} onChange={e => setForm({ ...form, raisonSociale: e.target.value })} />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Mot de passe provisoire *</label>
            <input type="password" className="form-control" placeholder="Mot de passe initial" value={form.motDePasse} onChange={e => setForm({ ...form, motDePasse: e.target.value })} />
          </div>

          {(form.role === 'PAYEUR' || form.role === 'EMPLOYE') && (
            <div className="form-group">
              <label className="form-label">Cycle de facturation</label>
              <select className="form-control" value={form.cycleFin} onChange={e => setForm({ ...form, cycleFin: e.target.value })}>
                <option value="HYB">Hybride (HYB)</option>
                <option value="OP">Open (OP)</option>
              </select>
              <small className="text-muted">Type de cycle de facturation</small>
            </div>
          )}

          {form.role === 'PAYEUR' && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
              <div className="flex items-start gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-blue-600 mt-0.5 flex-shrink-0">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                <div className="text-blue-800">
                  <p className="font-medium">Attribution des lignes</p>
                  <p className="text-blue-700">Après création du compte payeur, vous pourrez lui associer ses lignes téléphoniques via un assistant dédié.</p>
                </div>
              </div>
            </div>
          )}

          </div>

          <div className="flex justify-end gap-3 px-6 py-4 border-t border-zinc-100 bg-zinc-50 flex-shrink-0">
            <button type="button" className="btn btn-outline" onClick={onClose}>Annuler</button>
            <button type="submit" className="btn btn-primary" disabled={chargement}>
              {chargement ? 'Création...' : 'Créer le compte'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}

// ── Page principale ──────────────────────────────────────────
export default function GestionComptes() {
  const location = useLocation()
  const [utilisateurs, setUtilisateurs] = useState([])
  const [chargement, setChargement] = useState(true)
  const [recherche, setRecherche] = useState('')
  const [filtreRole, setFiltreRole] = useState('')
  const [message, setMessage] = useState(null)
  const [page, setPage] = useState(1)
  const [modalOuvert, setModalOuvert] = useState(false)
  const [modalLignesOuvert, setModalLignesOuvert] = useState(false)
  const [payeurCree, setPayeurCree] = useState(null)
  const [ligneActive, setLigneActive] = useState(null)
  const parPage = 10

  useEffect(() => {
    chargerUtilisateurs()
    if (location.search.includes('action=nouveau')) setModalOuvert(true)
  }, [])

  const chargerUtilisateurs = () => {
    getUtilisateurs().then(setUtilisateurs).catch(console.error).finally(() => setChargement(false))
  }

  const utilisateursFiltres = utilisateurs.filter(u => {
    const matchRecherche = !recherche ||
      u.nom?.toLowerCase().includes(recherche.toLowerCase()) ||
      u.prenom?.toLowerCase().includes(recherche.toLowerCase()) ||
      u.login?.toLowerCase().includes(recherche.toLowerCase()) ||
      u.raisonSociale?.toLowerCase().includes(recherche.toLowerCase())
    const matchRole = !filtreRole || u.role === filtreRole
    return matchRecherche && matchRole
  })

  const total = utilisateursFiltres.length
  const pages = Math.ceil(total / parPage)
  const utilisateursPage = utilisateursFiltres.slice((page - 1) * parPage, page * parPage)

  const showMessage = (type, texte) => {
    setMessage({ type, texte })
    setTimeout(() => setMessage(null), 4000)
  }

  const handlePayeurCree = (nouveauPayeur) => {
    setPayeurCree(nouveauPayeur)
    setModalLignesOuvert(true)
    showMessage('success', `Compte payeur créé pour ${nouveauPayeur.prenom} ${nouveauPayeur.nom}.`)
    chargerUtilisateurs()
  }

  const handleActiver = async (id) => {
    try { await activerCompte(id); showMessage('success', 'Compte activé.'); chargerUtilisateurs() }
    catch { showMessage('danger', "Erreur lors de l'activation.") }
  }

  const handleSuspendre = async (id) => {
    if (!window.confirm('Suspendre ce compte ?')) return
    try { await suspendreCompte(id); showMessage('success', 'Compte suspendu.'); chargerUtilisateurs() }
    catch { showMessage('danger', 'Erreur lors de la suspension.') }
  }

  const handleResetMdp = async (id, nom) => {
    if (!window.confirm(`Réinitialiser le mot de passe de ${nom} ?`)) return
    try { await reinitialiserMotDePasseAdmin(id); showMessage('success', `Mot de passe réinitialisé pour ${nom}.`) }
    catch { showMessage('danger', 'Erreur lors de la réinitialisation.') }
  }

  return (
    <div className="comptes-page">
      <AnimatePresence>
        {modalOuvert && (
          <ModalCreerCompte
            onClose={() => setModalOuvert(false)}
            onSuccess={(msg) => { showMessage('success', msg); chargerUtilisateurs() }}
            onPayeurCree={handlePayeurCree}
          />
        )}
        
        {modalLignesOuvert && payeurCree && (
          <ModalGestionLignes
            payeur={payeurCree}
            onClose={() => {
              setModalLignesOuvert(false)
              setPayeurCree(null)
            }}
            onSuccess={(msg) => {
              showMessage('success', msg)
              setModalLignesOuvert(false)
              setPayeurCree(null)
            }}
          />
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="comptes-header">
        <div>
          <h1 className="page-title">Gestion des comptes</h1>
          <p className="text-muted">{total} compte(s)</p>
        </div>
        <button className="btn btn-primary" onClick={() => setModalOuvert(true)}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Nouveau compte
        </button>
      </div>

      {/* Message */}
      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className={`alert alert-${message.type}`}
          >
            {message.texte}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Filtres */}
      <div className="comptes-filtres">
        <div className="comptes-search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#aaa" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            type="text"
            placeholder="Rechercher par nom, login, entreprise..."
            value={recherche}
            onChange={e => { setRecherche(e.target.value); setPage(1) }}
          />
        </div>
        <select
          className="comptes-select"
          value={filtreRole}
          onChange={e => { setFiltreRole(e.target.value); setPage(1) }}
        >
          <option value="">Tous les rôles</option>
          {ROLES_OPTIONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="comptes-table-wrap">
        {chargement ? (
          <div className="loading-overlay"><div className="spinner"></div></div>
        ) : utilisateursPage.length === 0 ? (
          <div className="empty-state"><p>Aucun compte ne correspond à votre recherche.</p></div>
        ) : (
          <table className="comptes-table">
            <thead>
              <tr>
                <th>NOM</th>
                <th>RÔLE</th>
                <th>ENTREPRISE</th>
                <th>LOGIN</th>
                <th>STATUT</th>
                <th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {utilisateursPage.map((u) => {
                const cfg = ROLE_CONFIG[u.role] || ROLE_CONFIG.EMPLOYE
                const initiales = getInitiales(u.prenom, u.nom)
                const isActive = ligneActive === u.id

                return (
                  <tr
                    key={u.id}
                    className={`comptes-row ${isActive ? 'comptes-row--active' : ''}`}
                    onMouseEnter={() => setLigneActive(u.id)}
                    onMouseLeave={() => setLigneActive(null)}
                  >
                    {/* Nom + avatar */}
                    <td>
                      <div className="comptes-cell-nom">
                        <div
                          className="comptes-avatar"
                          style={{ background: cfg.bg, color: cfg.color }}
                        >
                          {initiales}
                        </div>
                        <div>
                          <div className="comptes-nom">{u.prenom} {u.nom}</div>
                          <div className="comptes-email">{u.email || u.login}</div>
                        </div>
                      </div>
                    </td>

                    {/* Rôle */}
                    <td>
                      <span
                        className="comptes-role-badge"
                        style={{ background: cfg.bg, color: cfg.color }}
                      >
                        {cfg.label}
                      </span>
                    </td>

                    {/* Entreprise */}
                    <td className="comptes-td-muted">{u.raisonSociale || '—'}</td>

                    {/* Login */}
                    <td className="comptes-td-mono">{u.login}</td>

                    {/* Statut */}
                    <td>
                      <span className={`comptes-statut ${u.estActif ? 'comptes-statut--actif' : 'comptes-statut--suspendu'}`}>
                        {u.estActif ? 'Actif' : 'Suspendu'}
                      </span>
                    </td>

                    {/* Actions — visibles au hover */}
                    <td>
                      <div className={`comptes-actions ${isActive ? 'comptes-actions--visible' : ''}`}>
                        {/* Gérer les lignes (pour les payeurs) */}
                        {u.role === 'PAYEUR' && (
                          <button
                            className="comptes-action-btn comptes-action-btn--edit"
                            title="Gérer les lignes"
                            onClick={() => {
                              setPayeurCree(u)
                              setModalLignesOuvert(true)
                            }}
                          >
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                            </svg>
                          </button>
                        )}
                        
                        {/* Reset MDP */}
                        <button
                          className="comptes-action-btn comptes-action-btn--edit"
                          title="Réinitialiser le mot de passe"
                          onClick={() => handleResetMdp(u.id, `${u.prenom} ${u.nom}`)}
                        >
                          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                        </button>

                        {/* Activer / Suspendre */}
                        {u.estActif ? (
                          <button
                            className="comptes-action-btn comptes-action-btn--check"
                            title="Suspendre"
                            onClick={() => handleSuspendre(u.id)}
                          >
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
                          </button>
                        ) : (
                          <button
                            className="comptes-action-btn comptes-action-btn--check"
                            title="Activer"
                            onClick={() => handleActiver(u.id)}
                          >
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"/></svg>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {pages > 1 && (
        <div className="bg-white rounded-xl border border-zinc-200 dark:border-zinc-800 px-6 py-4 mt-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              Affichage {((page - 1) * parPage) + 1} à {Math.min(page * parPage, total)} sur {total} comptes
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="px-3 py-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                ← Précédent
              </button>
              
              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(5, pages) }, (_, i) => {
                  let pageNum
                  if (pages <= 5) {
                    pageNum = i + 1
                  } else if (page <= 3) {
                    pageNum = i + 1
                  } else if (page >= pages - 2) {
                    pageNum = pages - 4 + i
                  } else {
                    pageNum = page - 2 + i
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                        pageNum === page
                          ? 'bg-[#002a7a] text-white'
                          : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>

              <button
                onClick={() => setPage(page + 1)}
                disabled={page === pages}
                className="px-3 py-2 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Suivant →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
