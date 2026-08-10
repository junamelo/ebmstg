import { useEffect, useMemo, useState } from 'react'
import * as XLSX from 'xlsx'
import api from '../../../services/api'

const normaliserNumero = (value) => String(value || '').replace(/\D/g, '')
const numeroMoovValide = (value) => /^(78|79|96|97|98|99)\d{6}$/.test(normaliserNumero(value))

export default function ModalAssocierLignesPayeur({ company, payeur, onClose, onSuccess }) {
  const [lignes, setLignes] = useState([])
  const [employesDisponibles, setEmployesDisponibles] = useState([])
  const [afficherBase, setAfficherBase] = useState(false)
  const [recherche, setRecherche] = useState('')
  const [saisie, setSaisie] = useState('')
  const [erreur, setErreur] = useState('')
  const [enregistrement, setEnregistrement] = useState(false)

  useEffect(() => {
    const charger = async () => {
      try {
        const response = await api.get('/billing/lines/available-employees/')
        const employes = response.data.results || response.data || []
        setEmployesDisponibles(employes)
      } catch (error) {
        console.error('Erreur chargement des employés disponibles:', error)
        setErreur('Impossible de charger les numéros disponibles depuis la base.')
      }
    }
    charger()
  }, [])

  const ajouterLignesManuelles = (valeur) => {
    setSaisie(valeur)
    const numeros = valeur.split(/\r?\n/).map(normaliserNumero).filter(numeroMoovValide)
    setLignes(numeros.map((numero, index) => ({
      id: `manuel-${index}-${numero}`,
      numero,
      nom: '',
      employe: null,
      source: 'Saisie manuelle',
    })))
    setErreur('')
  }

  const importerFichier = (event) => {
    const fichier = event.target.files?.[0]
    if (!fichier) return
    const reader = new FileReader()
    const ajouterDepuisLignes = (valeurs) => {
      const nouvellesLignes = valeurs
        .map((valeur, index) => {
          const colonnes = Array.isArray(valeur) ? valeur : String(valeur || '').split(/[;,]/)
          const numero = normaliserNumero(colonnes[0])
          if (!numeroMoovValide(numero)) return null
          return {
            id: `import-${index}-${numero}`,
            numero,
            nom: String(colonnes[1] || '').trim(),
            employe: null,
            source: 'Import fichier',
          }
        })
        .filter(Boolean)
      setLignes(nouvellesLignes)
      setSaisie('')
      setErreur(nouvellesLignes.length ? '' : 'Aucun numéro Moov valide trouvé dans le fichier.')
    }
    reader.onload = (loadEvent) => {
      const estExcel = /\.xlsx?$/i.test(fichier.name)
      if (estExcel) {
        const workbook = XLSX.read(loadEvent.target?.result, { type: 'array' })
        const premiereFeuille = workbook.Sheets[workbook.SheetNames[0]]
        ajouterDepuisLignes(XLSX.utils.sheet_to_json(premiereFeuille, { header: 1, raw: false }))
      } else {
        ajouterDepuisLignes(String(loadEvent.target?.result || '').split(/\r?\n/))
      }
    }
    if (/\.xlsx?$/i.test(fichier.name)) reader.readAsArrayBuffer(fichier)
    else reader.readAsText(fichier)
  }

  const ajouterEmploye = (employe) => {
    if (lignes.some(ligne => ligne.numero === employe.numero)) return
    setLignes(courantes => [...courantes, {
      id: `base-${employe.id}`,
      numero: employe.numero,
      nom: employe.nom,
      employe: employe.id,
      source: 'Base utilisateurs',
    }])
    setErreur('')
  }

  const retirerLigne = (id) => setLignes(courantes => courantes.filter(ligne => ligne.id !== id))

  const employesFiltres = useMemo(() => {
    const terme = recherche.trim().toLowerCase()
    return employesDisponibles.filter(employe => !terme || employe.numero.includes(terme) || employe.nom.toLowerCase().includes(terme))
  }, [employesDisponibles, recherche])

  const confirmer = async () => {
    if (!lignes.length) {
      setErreur('Ajoutez au moins une ligne.')
      return
    }
    const numeros = lignes.map(ligne => ligne.numero)
    if (new Set(numeros).size !== numeros.length) {
      setErreur('Un numéro ne peut être sélectionné qu’une seule fois.')
      return
    }
    setEnregistrement(true)
    setErreur('')
    try {
      await api.post('/billing/lines/bulk-create/', {
        company: company.id,
        lignes: lignes.map(ligne => ({
          msisdn: ligne.numero,
          utilisateur: ligne.nom || '',
          employe: ligne.employe || null,
          cycle: 'HYB',
          forfait: 0,
        })),
      })
      onSuccess(`${lignes.length} ligne(s) associée(s) au payeur avec succès.`)
      onClose()
    } catch (error) {
      const details = error.response?.data?.erreurs
      setErreur(details?.[0]?.erreurs?.msisdn?.[0] || error.response?.data?.error || "L'association des lignes a échoué.")
    } finally {
      setEnregistrement(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[1200] flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm">
      <div className="flex max-h-[90vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-zinc-100 px-6 py-4">
          <div><h2 className="text-lg font-semibold text-zinc-900">Associer des lignes au payeur</h2><p className="text-sm text-zinc-600">{payeur?.nom || company.raisonSociale} — contrat {company.compte}</p></div>
          <button onClick={onClose} className="rounded-full px-2 py-1 text-lg text-zinc-400 hover:bg-zinc-100">×</button>
        </div>
        {erreur && <div className="mx-6 mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{erreur}</div>}
        <div className="min-h-0 flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <section className="space-y-4"><h3 className="font-semibold text-zinc-900">Ajouter des lignes téléphoniques</h3>
              <div className="rounded-lg border border-zinc-200 p-4"><p className="mb-2 text-sm font-medium">1. Importer depuis un fichier</p><input type="file" accept=".txt,.csv,.xls,.xlsx" onChange={importerFichier} className="block w-full text-sm text-zinc-500 file:mr-3 file:rounded-lg file:border-0 file:bg-blue-50 file:px-3 file:py-2 file:text-blue-700" /><p className="mt-1 text-xs text-zinc-500">TXT/CSV : un numéro par ligne. Excel : numéro en colonne A, nom optionnel en colonne B.</p></div>
              <div className="rounded-lg border border-zinc-200 p-4"><p className="mb-2 text-sm font-medium">2. Saisie manuelle</p><textarea rows="4" value={saisie} onChange={e => ajouterLignesManuelles(e.target.value)} placeholder={'79342735\n79342736'} className="w-full rounded-lg border border-zinc-300 p-3 font-mono text-sm outline-none focus:ring-2 focus:ring-[#002a7a]" /><p className="mt-1 text-xs text-zinc-500">Un numéro par ligne.</p></div>
              <div className="rounded-lg border border-zinc-200 p-4"><p className="mb-2 text-sm font-medium">3. Sélectionner depuis la base</p><button type="button" onClick={() => setAfficherBase(value => !value)} className="rounded-lg border border-[#e05500] px-3 py-2 text-sm font-medium text-[#e05500] hover:bg-orange-50">{afficherBase ? 'Masquer' : 'Afficher'} les lignes disponibles</button>
                {afficherBase && <div className="mt-3"><input value={recherche} onChange={e => setRecherche(e.target.value)} placeholder="Rechercher par numéro ou nom…" className="mb-2 w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm" /><div className="max-h-48 overflow-y-auto rounded-lg border border-zinc-200 bg-zinc-50">{employesFiltres.length === 0 ? <p className="p-3 text-sm text-zinc-500">Aucun numéro disponible.</p> : employesFiltres.map(employe => <button type="button" key={employe.id} onClick={() => ajouterEmploye(employe)} className="flex w-full items-center justify-between border-b border-zinc-100 px-3 py-2 text-left hover:bg-white"><span><span className="font-mono text-sm font-semibold">{employe.numero}</span><span className="ml-2 text-sm text-zinc-700">{employe.nom}</span></span><span className="text-xs font-medium text-[#002a7a]">Ajouter</span></button>)}</div></div>}
              </div>
            </section>
            <section><h3 className="mb-4 font-semibold text-zinc-900">Lignes à attribuer ({lignes.length})</h3>{lignes.length ? <div className="overflow-hidden rounded-lg border border-zinc-200"><table className="w-full text-sm"><thead className="bg-zinc-50 text-left"><tr><th className="p-3">Numéro</th><th className="p-3">Utilisateur</th><th className="p-3">Source</th><th className="p-3"></th></tr></thead><tbody>{lignes.map(ligne => <tr key={ligne.id} className="border-t border-zinc-100"><td className="p-3 font-mono">{ligne.numero}</td><td className="p-3">{ligne.nom || 'Non renseigné'}</td><td className="p-3 text-xs text-zinc-500">{ligne.source}</td><td className="p-3 text-right"><button type="button" onClick={() => retirerLigne(ligne.id)} className="text-xs text-red-600">Retirer</button></td></tr>)}</tbody></table></div> : <div className="rounded-lg border-2 border-dashed border-zinc-200 p-10 text-center text-sm text-zinc-500">Aucune ligne ajoutée.<br />Utilisez une méthode à gauche.</div>}</section>
          </div>
        </div>
        <div className="flex justify-end gap-3 border-t border-zinc-100 px-6 py-4"><button onClick={onClose} className="rounded-lg border border-[#e05500] px-5 py-2 text-sm font-medium text-[#e05500]">Annuler</button><button onClick={confirmer} disabled={!lignes.length || enregistrement} className="rounded-lg bg-[#002a7a] px-5 py-2 text-sm font-medium text-white disabled:opacity-40">{enregistrement ? 'Association…' : 'Associer les lignes'}</button></div>
      </div>
    </div>
  )
}
