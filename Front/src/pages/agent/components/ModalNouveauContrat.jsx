import { useState, useEffect } from 'react'
import { motion } from 'motion/react'
import api from '../../../services/api'

export default function ModalNouveauContrat({ onClose, onCreate }) {
  const [step, setStep] = useState(1) // 1 = Identité, 2 = Contrat, 3 = Services
  const [commerciaux, setCommerciaux] = useState([])
  const [tarifsNoLimit, setTarifsNoLimit] = useState([])
  const [tarifsBlackBerry, setTarifsBlackBerry] = useState([])
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  const [form, setForm] = useState({
    // Identité
    typePayeur: 'ENTREPRISE',
    raisonSociale: '',
    nom: '',
    prenom: '',
    email: '',
    telephone: '',
    adresse: '',
    adresse_ligne2: '',
    email_facturation: '',
    // Contrat
    categorie: 'PE',
    commercial: '',
    mode_reglement: 'VIREMENT',
    date_effet: '',
    date_fin: '',
    observation: '',
    type_revenu: '',
    est_exonere: false,
    // Services
    facture_detaillee_defaut: false,
    option_nolimit_defaut: '',
    option_blackberry_defaut: '',
    est_incognito_defaut: false,
    roaming_defaut: false,
    internet_defaut: false,
    international_defaut: false,
    est_non_revenu_defaut: false,
  })

  useEffect(() => {
    // Empêche le scroll de la page derrière le modal
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    Promise.all([
      api.get('/billing/commerciaux/', { params: { est_actif: true } }),
      api.get('/billing/tarifs/', { params: { actif_only: true } })
    ])
      .then(([respCommerciaux, respTarifs]) => {
        setCommerciaux(respCommerciaux.data.results || respCommerciaux.data || [])

        const tarifs = respTarifs.data.results || respTarifs.data || []
        const noLimit = tarifs
          .filter(t => {
            const texte = `${t.service_name || ''} ${t.nom_option || ''}`.toLowerCase()
            return texte.includes('no limit') || texte.includes('nolimit')
          })
          .map(t => t.nom_option)
          .filter(Boolean)
        const blackberry = tarifs
          .filter(t => {
            const texte = `${t.service_name || ''} ${t.nom_option || ''}`.toLowerCase()
            return texte.includes('blackberry') || texte.includes(' bb') || texte.startsWith('bb')
          })
          .map(t => t.nom_option)
          .filter(Boolean)

        setTarifsNoLimit([...new Set(noLimit)])
        setTarifsBlackBerry([...new Set(blackberry)])
      })
      .catch(() => {})

    return () => {
      document.body.style.overflow = previousOverflow
    }
  }, [])

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))
  const setCheck = (key) => (e) => set(key, e.target.checked)
  const setVal = (key) => (e) => set(key, e.target.value)

  const inputCls = (field) =>
    `w-full px-3 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-[#002a7a] outline-none ${errors[field] ? 'border-red-400' : 'border-zinc-300'}`

  const validerStep1 = () => {
    const errs = {}
    if (form.typePayeur === 'ENTREPRISE' && !form.raisonSociale.trim()) errs.raisonSociale = 'Obligatoire'
    if (form.typePayeur === 'PARTICULIER' && !form.nom.trim()) errs.nom = 'Obligatoire'
    if (form.typePayeur === 'PARTICULIER' && !form.prenom.trim()) errs.prenom = 'Obligatoire'
    return errs
  }

  const validerStep2 = () => {
    const errs = {}
    if (!form.categorie) errs.categorie = 'Obligatoire'
    if (!form.commercial) errs.commercial = 'Obligatoire'
    if (!form.mode_reglement) errs.mode_reglement = 'Obligatoire'
    if (form.date_effet && form.date_fin && form.date_fin < form.date_effet)
      errs.date_fin = 'La date de fin doit être postérieure à la date d\'effet'
    return errs
  }

  const handleNext = () => {
    let errs = {}
    if (step === 1) errs = validerStep1()
    if (step === 2) errs = validerStep2()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setErrors({})
    setStep(s => s + 1)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const payload = {
        compte: genererNumeroContrat(),
        raison_sociale: form.typePayeur === 'ENTREPRISE' ? form.raisonSociale : `${form.prenom} ${form.nom}`,
        nom_commercial: form.typePayeur === 'ENTREPRISE' ? form.raisonSociale : `${form.prenom} ${form.nom}`,
        categorie: form.categorie,
        commercial: form.commercial || null,
        mode_reglement: form.mode_reglement,
        adresse: form.adresse,
        adresse_ligne2: form.adresse_ligne2,
        email_facturation: form.email_facturation || form.email,
        date_effet: form.date_effet || null,
        date_fin: form.date_fin || null,
        observation: form.observation,
        type_revenu: form.type_revenu,
        est_exonere: form.est_exonere,
        facture_detaillee_defaut: form.facture_detaillee_defaut,
        option_nolimit_defaut: form.option_nolimit_defaut,
        option_blackberry_defaut: form.option_blackberry_defaut,
        est_incognito_defaut: form.est_incognito_defaut,
        roaming_defaut: form.roaming_defaut,
        internet_defaut: form.internet_defaut,
        international_defaut: form.international_defaut,
        est_non_revenu_defaut: form.est_non_revenu_defaut,
      }
      await onCreate(payload)
    } finally {
      setSaving(false)
    }
  }

  const genererNumeroContrat = () => {
    const annee = new Date().getFullYear().toString().slice(-2)
    const seq = Math.floor(Math.random() * 999999).toString().padStart(6, '0')
    return `A${annee}${seq}`
  }

  const CATEGORIES = [
    { value: 'GE', label: 'Grande Entreprise' },
    { value: 'PE', label: 'Petite Entreprise' },
    { value: 'P', label: 'Particulier' },
    { value: 'OI', label: 'Organisme International' },
    { value: 'EP', label: 'Entreprise Publique' },
    { value: 'A', label: 'Association' },
  ]



  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[1100] p-4">
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[92vh] flex flex-col">

        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-zinc-200 px-6 py-4 flex items-center justify-between rounded-t-xl z-10 flex-shrink-0">
          <div>
            <h3 className="text-lg font-bold text-zinc-900">Créer un nouveau contrat</h3>
            <div className="flex items-center gap-2 mt-1.5">
              {[1,2,3].map(s => (
                <div key={s} className="flex items-center gap-1.5">
                  <div className={`w-6 h-6 rounded-full text-xs flex items-center justify-center font-bold ${step >= s ? 'bg-[#002a7a] text-white' : 'bg-zinc-100 text-zinc-400'}`}>{s}</div>
                  <span className={`text-xs ${step === s ? 'text-zinc-700 font-medium' : 'text-zinc-400'}`}>
                    {s === 1 ? 'Identité' : s === 2 ? 'Contrat' : 'Services'}
                  </span>
                  {s < 3 && <div className="w-6 h-px bg-zinc-200"/>}
                </div>
              ))}
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-zinc-100 text-zinc-400">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="overflow-y-auto overscroll-contain flex-1 p-6 space-y-5">

          {/* STEP 1 — Identité */}
          {step === 1 && (
            <>
              <div>
                <label className="block text-sm font-semibold text-zinc-700 mb-2">Type de compte *</label>
                <div className="grid grid-cols-2 gap-3">
                  {[{v:'ENTREPRISE',label:'Entreprise',icon:'🏢',desc:'Plusieurs lignes'},{v:'PARTICULIER',label:'Particulier',icon:'👤',desc:'Une seule ligne'}].map(t => (
                    <button key={t.v} type="button" onClick={() => set('typePayeur', t.v)}
                      className={`p-3 rounded-lg border-2 text-left transition-all ${form.typePayeur===t.v ? 'border-[#002a7a] bg-[#002a7a]/5' : 'border-zinc-200 hover:border-zinc-300'}`}>
                      <div className="text-xl mb-1">{t.icon}</div>
                      <p className="font-semibold text-sm text-zinc-900">{t.label}</p>
                      <p className="text-xs text-zinc-500">{t.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {form.typePayeur === 'ENTREPRISE' ? (
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Raison sociale *</label>
                  <input className={inputCls('raisonSociale')} value={form.raisonSociale} onChange={setVal('raisonSociale')} placeholder="SOCIETE EXAMPLE SARL"/>
                  {errors.raisonSociale && <p className="text-xs text-red-500 mt-0.5">{errors.raisonSociale}</p>}
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-zinc-700 mb-1">Nom *</label>
                    <input className={inputCls('nom')} value={form.nom} onChange={setVal('nom')}/>
                    {errors.nom && <p className="text-xs text-red-500 mt-0.5">{errors.nom}</p>}
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-zinc-700 mb-1">Prénom *</label>
                    <input className={inputCls('prenom')} value={form.prenom} onChange={setVal('prenom')}/>
                    {errors.prenom && <p className="text-xs text-red-500 mt-0.5">{errors.prenom}</p>}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Email</label>
                  <input type="email" className={inputCls('email')} value={form.email} onChange={setVal('email')}/>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Téléphone</label>
                  <input className={inputCls('telephone')} value={form.telephone} onChange={setVal('telephone')}/>
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-zinc-700 mb-1">Adresse 1</label>
                <input className={inputCls('adresse')} value={form.adresse} onChange={setVal('adresse')}/>
              </div>
              <div>
                <label className="block text-xs font-semibold text-zinc-700 mb-1">Adresse 2</label>
                <input className={inputCls('adresse_ligne2')} value={form.adresse_ligne2} onChange={setVal('adresse_ligne2')}/>
              </div>
            </>
          )}

          {/* STEP 2 — Contrat */}
          {step === 2 && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Catégorie *</label>
                  <select className={inputCls('categorie')} value={form.categorie} onChange={setVal('categorie')}>
                    {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                  </select>
                  {errors.categorie && <p className="text-xs text-red-500 mt-0.5">{errors.categorie}</p>}
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Commercial *</label>
                  <select className={inputCls('commercial')} value={form.commercial} onChange={setVal('commercial')}>
                    <option value="">-- Sélectionner un commercial --</option>
                    {commerciaux.map(c => (
                      <option key={c.id} value={c.id}>{c.prenom} {c.nom} ({c.matricule})</option>
                    ))}
                  </select>
                  {errors.commercial && <p className="text-xs text-red-500 mt-0.5">{errors.commercial}</p>}
                  {commerciaux.length === 0 && (
                    <p className="text-xs text-amber-600 mt-0.5">Aucun commercial actif — créez-en un d&apos;abord</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-700 mb-1">Mode de règlement *</label>
                <select className={inputCls('mode_reglement')} value={form.mode_reglement} onChange={setVal('mode_reglement')}>
                  <option value="CHEQUE">Chèque</option>
                  <option value="VIREMENT">Virement</option>
                  <option value="ESPECES">Espèces</option>
                </select>
                {errors.mode_reglement && <p className="text-xs text-red-500 mt-0.5">{errors.mode_reglement}</p>}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Date d&apos;effet</label>
                  <input type="date" className={inputCls('date_effet')} value={form.date_effet} onChange={setVal('date_effet')}/>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Date de fin</label>
                  <input type="date" className={inputCls('date_fin')} value={form.date_fin} onChange={setVal('date_fin')}/>
                  {errors.date_fin && <p className="text-xs text-red-500 mt-0.5">{errors.date_fin}</p>}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-700 mb-1">Email de facturation</label>
                <input type="email" className={inputCls('email_facturation')} value={form.email_facturation} onChange={setVal('email_facturation')} placeholder="Laissez vide pour utiliser l'email principal"/>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-700 mb-1">Type de revenu</label>
                <input className={inputCls('type_revenu')} value={form.type_revenu} onChange={setVal('type_revenu')} placeholder="Ex: Corporate, Prépayé..."/>
              </div>

              <div>
                <label className="block text-xs font-semibold text-zinc-700 mb-1">Observation</label>
                <textarea className={`${inputCls('observation')} resize-none`} rows={2} value={form.observation} onChange={setVal('observation')}/>
              </div>

              <div className="border border-zinc-200 rounded-lg p-4">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" checked={form.est_exonere} onChange={setCheck('est_exonere')}
                    className="w-4 h-4 text-[#002a7a] rounded"/>
                  <span className="text-sm font-medium text-zinc-700">Exonéré de TVA</span>
                </label>
              </div>
            </>
          )}

          {/* STEP 3 — Services par défaut */}
          {step === 3 && (
            <>
              <div className="bg-zinc-50 rounded-lg p-3 border border-zinc-200">
                <p className="text-xs text-zinc-600">
                  Ces services seront activés par défaut sur toutes les nouvelles lignes du contrat. Chaque ligne peut ensuite les modifier individuellement.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                {[
                  {key:'facture_detaillee_defaut', label:'Facturation détaillée'},
                  {key:'est_incognito_defaut', label:'Incognito'},
                  {key:'roaming_defaut', label:'Roaming'},
                  {key:'internet_defaut', label:'Internet'},
                  {key:'international_defaut', label:'International'},
                  {key:'est_non_revenu_defaut', label:'Non Revenu'},
                ].map(({key,label}) => (
                  <label key={key} className="flex items-center gap-3 p-3 rounded-lg border border-zinc-200 hover:bg-white cursor-pointer">
                    <input type="checkbox" checked={form[key]||false} onChange={setCheck(key)}
                      className="w-4 h-4 text-[#002a7a] rounded"/>
                    <span className="text-sm text-zinc-700">{label}</span>
                  </label>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Option No Limit</label>
                  <select className={inputCls('option_nolimit_defaut')} value={form.option_nolimit_defaut} onChange={setVal('option_nolimit_defaut')}>
                    <option value="">-- Aucune option --</option>
                    {tarifsNoLimit.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                  {tarifsNoLimit.length === 0 && (
                    <p className="text-xs text-zinc-400 mt-1">Aucune option No Limit active disponible</p>
                  )}
                </div>
                <div>
                  <label className="block text-xs font-semibold text-zinc-700 mb-1">Option BlackBerry</label>
                  <select className={inputCls('option_blackberry_defaut')} value={form.option_blackberry_defaut} onChange={setVal('option_blackberry_defaut')}>
                    <option value="">-- Aucune option --</option>
                    {tarifsBlackBerry.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                  {tarifsBlackBerry.length === 0 && (
                    <p className="text-xs text-zinc-400 mt-1">Aucune option BlackBerry active disponible</p>
                  )}
                </div>
              </div>
            </>
          )}
        </form>

        {/* Footer navigation */}
        <div className="flex gap-3 px-6 py-4 border-t border-zinc-200 flex-shrink-0">
          <button type="button" onClick={step === 1 ? onClose : () => setStep(s => s - 1)}
            className="flex-1 px-4 py-2.5 text-sm font-semibold bg-zinc-100 text-zinc-700 rounded-lg hover:bg-zinc-200 transition-colors">
            {step === 1 ? 'Annuler' : '← Retour'}
          </button>
          {step < 3 ? (
            <button type="button" onClick={handleNext}
              className="flex-1 px-4 py-2.5 text-sm font-semibold bg-[#002a7a] text-white rounded-lg hover:bg-[#003d9e] transition-colors">
              Suivant →
            </button>
          ) : (
            <button type="button" disabled={saving} onClick={handleSubmit}
              className="flex-1 px-4 py-2.5 text-sm font-semibold bg-[#e05500] hover:bg-[#c44a00] text-white rounded-lg transition-colors disabled:opacity-60">
              {saving ? 'Création...' : 'Créer le contrat'}
            </button>
          )}
        </div>
      </motion.div>
    </div>
  )
}
