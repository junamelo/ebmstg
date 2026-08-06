import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import api from '../../services/api'

export default function GestionCommerciaux() {
  const [commerciaux, setCommerciaux] = useState([])
  const [chargement, setChargement] = useState(true)
  const [message, setMessage] = useState(null)
  const [recherche, setRecherche] = useState('')
  const [filtreActif, setFiltreActif] = useState('tous')
  const [pageCourante, setPageCourante] = useState(1)
  const ITEMS_PAR_PAGE = 10

  const [modalOuvert, setModalOuvert] = useState(false)
  const [commercialEnEdition, setCommercialEnEdition] = useState(null)
  const [form, setForm] = useState({ nom: '', prenom: '', matricule: '', telephone: '', email: '' })
  const [errorsForm, setErrorsForm] = useState({})
  const [saving, setSaving] = useState(false)

  useEffect(() => { charger() }, [])
  useEffect(() => { setPageCourante(1) }, [recherche, filtreActif])

  const charger = async () => {
    try {
      setChargement(true)
      const resp = await api.get('/billing/commerciaux/')
      setCommerciaux(resp.data.results || resp.data)
    } catch (e) {
      showMsg('error', 'Impossible de charger les commerciaux')
    } finally {
      setChargement(false)
    }
  }

  const showMsg = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage(null), 4000)
  }

  const ouvrirCreation = () => {
    setCommercialEnEdition(null)
    setForm({ nom: '', prenom: '', matricule: '', telephone: '', email: '' })
    setErrorsForm({})
    setModalOuvert(true)
  }

  const ouvrirEdition = (c) => {
    setCommercialEnEdition(c)
    setForm({ nom: c.nom, prenom: c.prenom, matricule: c.matricule, telephone: c.telephone || '', email: c.email || '' })
    setErrorsForm({})
    setModalOuvert(true)
  }

  const fermerModal = () => {
    setModalOuvert(false)
    setCommercialEnEdition(null)
    setErrorsForm({})
  }

  const valider = () => {
    const errs = {}
    if (!form.nom.trim()) errs.nom = 'Obligatoire'
    if (!form.prenom.trim()) errs.prenom = 'Obligatoire'
    if (!form.matricule.trim()) errs.matricule = 'Obligatoire'
    return errs
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = valider()
    if (Object.keys(errs).length) { setErrorsForm(errs); return }
    setSaving(true)
    try {
      if (commercialEnEdition) {
        await api.patch(`/billing/commerciaux/${commercialEnEdition.id}/`, form)
        showMsg('success', 'Commercial modifié')
      } else {
        await api.post('/billing/commerciaux/', form)
        showMsg('success', 'Commercial créé')
      }
      fermerModal()
      charger()
    } catch (e) {
      const data = e.response?.data || {}
      const errsBack = {}
      if (data.matricule) errsBack.matricule = data.matricule[0]
      if (data.email) errsBack.email = data.email[0]
      if (Object.keys(errsBack).length) setErrorsForm(errsBack)
      else showMsg('error', data.error || data.detail || 'Erreur lors de l\'enregistrement')
    } finally {
      setSaving(false)
    }
  }

  const toggleActif = async (c) => {
    try {
      await api.post(`/billing/commerciaux/${c.id}/toggle_actif/`)
      charger()
    } catch (e) {
      showMsg('error', e.response?.data?.error || 'Erreur')
    }
  }

  const filtres = commerciaux.filter(c => {
    const matchActif = filtreActif === 'tous' || (filtreActif === 'actif' ? c.est_actif : !c.est_actif)
    const q = recherche.toLowerCase()
    const matchRecherche = !q || c.nom.toLowerCase().includes(q) || c.prenom.toLowerCase().includes(q) ||
      c.matricule.toLowerCase().includes(q) || (c.telephone || '').includes(q)
    return matchActif && matchRecherche
  })

  const nbPages = Math.ceil(filtres.length / ITEMS_PAR_PAGE)
  const page = filtres.slice((pageCourante - 1) * ITEMS_PAR_PAGE, pageCourante * ITEMS_PAR_PAGE)

  const inputCls = (field) => `w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-[#002a7a] outline-none ${errorsForm[field] ? 'border-red-400' : 'border-zinc-300'}`

  return (
    <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Toast */}
      <AnimatePresence>
        {message && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className={`fixed top-4 right-4 z-[1200] px-5 py-3 rounded-lg shadow-lg text-sm font-medium ${message.type === 'success' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'}`}>
            {message.text}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">Gestion des Commerciaux</h1>
          <p className="text-sm text-zinc-500 mt-1">Commerciaux Moov Africa liés aux contrats</p>
        </div>
        <button onClick={ouvrirCreation}
          className="px-4 py-2.5 bg-[#002a7a] hover:bg-[#003d9e] text-white font-semibold text-sm rounded-lg transition-colors">
          + Nouveau commercial
        </button>
      </div>

      {/* Filtres */}
      <div className="bg-white rounded-xl border border-zinc-200 p-4 flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <svg className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
          <input type="text" placeholder="Nom, prénom, matricule, téléphone..." value={recherche}
            onChange={e => setRecherche(e.target.value)}
            className="pl-9 pr-4 py-2 w-full border border-zinc-300 rounded-lg text-sm focus:ring-2 focus:ring-[#002a7a] outline-none"/>
        </div>
        <select value={filtreActif} onChange={e => setFiltreActif(e.target.value)}
          className="px-3 py-2 border border-zinc-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-[#002a7a] outline-none">
          <option value="tous">Tous</option>
          <option value="actif">Actifs</option>
          <option value="inactif">Inactifs</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-zinc-200 overflow-hidden">
        {chargement ? (
          <div className="py-16 flex justify-center">
            <div className="w-7 h-7 border-2 border-zinc-200 border-t-[#002a7a] rounded-full animate-spin"/>
          </div>
        ) : filtres.length === 0 ? (
          <div className="py-16 text-center text-zinc-400 text-sm">Aucun commercial trouvé</div>
        ) : (
          <>
            <table className="w-full">
              <thead className="bg-zinc-50 border-b border-zinc-100">
                <tr>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-zinc-500">Nom</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-zinc-500">Matricule</th>
                  <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-zinc-500">Contact</th>
                  <th className="px-5 py-3 text-center text-xs font-semibold uppercase tracking-wide text-zinc-500">Contrats</th>
                  <th className="px-5 py-3 text-center text-xs font-semibold uppercase tracking-wide text-zinc-500">Statut</th>
                  <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-zinc-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100">
                {page.map((c, idx) => (
                  <motion.tr key={c.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: idx * 0.03 }}
                    className="hover:bg-zinc-50 transition-colors">
                    <td className="px-5 py-3.5">
                      <p className="font-semibold text-zinc-900 text-sm">{c.prenom} {c.nom}</p>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="font-mono text-xs bg-zinc-100 px-2 py-0.5 rounded">{c.matricule}</span>
                    </td>
                    <td className="px-5 py-3.5 text-sm text-zinc-600">
                      {c.telephone && <p>{c.telephone}</p>}
                      {c.email && <p className="text-zinc-400 text-xs">{c.email}</p>}
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <span className="text-sm font-semibold text-zinc-900">{c.nombre_contrats || 0}</span>
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${c.est_actif ? 'bg-emerald-100 text-emerald-700' : 'bg-zinc-100 text-zinc-500'}`}>
                        {c.est_actif ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button onClick={() => ouvrirEdition(c)}
                          className="px-2.5 py-1 text-xs font-medium text-zinc-600 border border-zinc-200 rounded-md hover:bg-zinc-100 transition-colors">
                          Modifier
                        </button>
                        <button onClick={() => toggleActif(c)}
                          className={`px-2.5 py-1 text-xs font-medium rounded-md border transition-colors ${c.est_actif ? 'text-red-600 border-red-200 hover:bg-red-50' : 'text-emerald-600 border-emerald-200 hover:bg-emerald-50'}`}>
                          {c.est_actif ? 'Désactiver' : 'Activer'}
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>

            {nbPages > 1 && (
              <div className="flex items-center justify-between px-5 py-3 border-t border-zinc-100">
                <p className="text-sm text-zinc-500">
                  {(pageCourante-1)*ITEMS_PAR_PAGE+1}–{Math.min(pageCourante*ITEMS_PAR_PAGE, filtres.length)} sur {filtres.length}
                </p>
                <div className="flex gap-1.5">
                  <button disabled={pageCourante===1} onClick={() => setPageCourante(p=>p-1)}
                    className="px-3 py-1.5 text-sm border border-zinc-200 rounded-lg disabled:opacity-40 hover:bg-zinc-50">← Préc.</button>
                  {Array.from({length:nbPages},(_,i)=>i+1).map(p=>(
                    <button key={p} onClick={()=>setPageCourante(p)}
                      className={`px-3 py-1.5 text-sm rounded-lg ${p===pageCourante?'bg-[#002a7a] text-white':'border border-zinc-200 hover:bg-zinc-50'}`}>{p}</button>
                  ))}
                  <button disabled={pageCourante===nbPages} onClick={() => setPageCourante(p=>p+1)}
                    className="px-3 py-1.5 text-sm border border-zinc-200 rounded-lg disabled:opacity-40 hover:bg-zinc-50">Suiv. →</button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Modal création/édition */}
      <AnimatePresence>
        {modalOuvert && (
          <div className="fixed inset-0 z-[1100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
            <motion.div initial={{opacity:0,scale:0.96}} animate={{opacity:1,scale:1}} exit={{opacity:0,scale:0.96}}
              className="bg-white rounded-xl shadow-2xl w-full max-w-lg">
              <div className="px-6 py-4 border-b border-zinc-200 flex items-center justify-between">
                <h3 className="text-base font-semibold text-zinc-900">
                  {commercialEnEdition ? 'Modifier le commercial' : 'Nouveau commercial'}
                </h3>
                <button onClick={fermerModal} className="w-7 h-7 flex items-center justify-center rounded-md hover:bg-zinc-100 text-zinc-400">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-zinc-700 mb-1">Nom *</label>
                    <input className={inputCls('nom')} value={form.nom} onChange={e=>setForm(f=>({...f,nom:e.target.value}))} placeholder="DUPONT"/>
                    {errorsForm.nom && <p className="text-xs text-red-500 mt-0.5">{errorsForm.nom}</p>}
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-zinc-700 mb-1">Prénom *</label>
                    <input className={inputCls('prenom')} value={form.prenom} onChange={e=>setForm(f=>({...f,prenom:e.target.value}))} placeholder="Jean"/>
                    {errorsForm.prenom && <p className="text-xs text-red-500 mt-0.5">{errorsForm.prenom}</p>}
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Matricule *</label>
                  <input className={inputCls('matricule')} value={form.matricule} onChange={e=>setForm(f=>({...f,matricule:e.target.value}))} placeholder="COM001" disabled={!!commercialEnEdition}/>
                  {errorsForm.matricule && <p className="text-xs text-red-500 mt-0.5">{errorsForm.matricule}</p>}
                  {commercialEnEdition && <p className="text-xs text-zinc-400 mt-0.5">Le matricule ne peut pas être modifié</p>}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-zinc-700 mb-1">Téléphone</label>
                    <input className={inputCls('telephone')} value={form.telephone} onChange={e=>setForm(f=>({...f,telephone:e.target.value}))} placeholder="90000001"/>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-zinc-700 mb-1">Email</label>
                    <input type="email" className={inputCls('email')} value={form.email} onChange={e=>setForm(f=>({...f,email:e.target.value}))} placeholder="jean@moov.tg"/>
                    {errorsForm.email && <p className="text-xs text-red-500 mt-0.5">{errorsForm.email}</p>}
                  </div>
                </div>
                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={fermerModal}
                    className="flex-1 px-4 py-2 text-sm font-semibold bg-zinc-100 text-zinc-700 rounded-lg hover:bg-zinc-200 transition-colors">
                    Annuler
                  </button>
                  <button type="submit" disabled={saving}
                    className="flex-1 px-4 py-2 text-sm font-semibold bg-[#002a7a] hover:bg-[#003d9e] text-white rounded-lg transition-colors disabled:opacity-60">
                    {saving ? 'Enregistrement...' : (commercialEnEdition ? 'Modifier' : 'Créer')}
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
