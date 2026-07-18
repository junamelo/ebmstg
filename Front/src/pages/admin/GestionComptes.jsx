import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'motion/react'
import { getUtilisateurs, activerCompte, suspendreCompte, reinitialiserMotDePasseAdmin } from '../../services/adminService'
import { mockCreerUtilisateur } from '../../services/mockApi'
import './Admin.css'

// ── Couleurs avatar par rôle ─────────────────────────────────
const ROLE_CONFIG = {
  SUPER_ADMIN:       { label: 'Super Admin',   bg: '#fee2e2', color: '#b91c1c' },
  AGENT_FACTURATION: { label: 'Agent',          bg: '#ede9fe', color: '#6d28d9' },
  PAYEUR:            { label: 'Payeur',          bg: '#dbeafe', color: '#1d4ed8' },
  EMPLOYE:           { label: 'Employé',         bg: '#dcfce7', color: '#15803d' },
}

function getInitiales(prenom, nom) {
  return `${prenom?.[0] ?? ''}${nom?.[0] ?? ''}`.toUpperCase()
}

// ── Formulaire création compte ───────────────────────────────
const ROLES_OPTIONS = [
  { value: 'EMPLOYE',           label: 'Employé' },
  { value: 'PAYEUR',            label: 'Payeur (Entreprise)' },
  { value: 'AGENT_FACTURATION', label: 'Agent Facturation' },
  { value: 'SUPER_ADMIN',       label: 'Super Administrateur' },
]

function ModalCreerCompte({ onClose, onSuccess }) {
  const [form, setForm] = useState({ nom: '', prenom: '', email: '', login: '', motDePasse: '', role: 'EMPLOYE', raisonSociale: '' })
  const [chargement, setChargement] = useState(false)
  const [erreur, setErreur] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErreur('')
    if (!form.nom || !form.prenom || !form.login || !form.motDePasse) {
      setErreur('Veuillez remplir tous les champs obligatoires.')
      return
    }
    setChargement(true)
    try {
      await mockCreerUtilisateur(form)
      onSuccess('Compte créé avec succès.')
      onClose()
    } catch {
      setErreur('Erreur lors de la création du compte.')
    } finally {
      setChargement(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 10 }}
        transition={{ duration: 0.2 }}
        className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-100">
          <h2 className="text-base font-semibold text-zinc-900">Créer un compte</h2>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-zinc-100 text-zinc-400 text-lg transition-colors">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {erreur && <div className="alert alert-danger text-sm">{erreur}</div>}

          <div className="grid grid-cols-2 gap-4">
            <div className="form-group">
              <label className="form-label">Prénom *</label>
              <input className="form-control" placeholder="Kodjo" value={form.prenom} onChange={e => setForm({ ...form, prenom: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Nom *</label>
              <input className="form-control" placeholder="MENSAH" value={form.nom} onChange={e => setForm({ ...form, nom: e.target.value })} />
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

          <div className="flex justify-end gap-3 pt-2">
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
        <div className="pagination">
          <button className="btn btn-outline btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Précédent</button>
          <span className="text-muted">Page {page} / {pages}</span>
          <button className="btn btn-outline btn-sm" disabled={page === pages} onClick={() => setPage(p => p + 1)}>Suivant</button>
        </div>
      )}
    </div>
  )
}
