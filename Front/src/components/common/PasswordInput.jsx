import { useState } from 'react'
import { validerMotDePasse, getCouleurForce, genererMotDePasseAleatoire } from '../../utils/passwordUtils'

export default function PasswordInput({ 
  value, 
  onChange, 
  label = 'Mot de passe', 
  showStrength = true,
  showGenerateButton = true,
  required = true,
  placeholder = ''
}) {
  const [visible, setVisible] = useState(false)
  const validation = validerMotDePasse(value)
  const couleur = getCouleurForce(validation.force)

  const handleGenerer = () => {
    onChange(genererMotDePasseAleatoire(12))
  }

  return (
    <div>
      <label className="block text-sm font-semibold text-zinc-700 dark:text-zinc-300 mb-2">
        {label} {required && '*'}
      </label>
      
      <div className="relative">
        <input
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          placeholder={placeholder}
          className="w-full px-4 py-2.5 pr-24 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-white focus:ring-2 focus:ring-[#002a7a] outline-none"
        />
        
        <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
          {/* Bouton Voir/Cacher */}
          <button
            type="button"
            onClick={() => setVisible(!visible)}
            className="p-1.5 text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-700 rounded transition-colors"
            title={visible ? 'Cacher' : 'Voir'}
          >
            {visible ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            )}
          </button>

          {/* Bouton Générer */}
          {showGenerateButton && (
            <button
              type="button"
              onClick={handleGenerer}
              className="p-1.5 text-zinc-500 hover:text-[#002a7a] dark:hover:text-blue-400 hover:bg-zinc-100 dark:hover:bg-zinc-700 rounded transition-colors"
              title="Générer un mot de passe aléatoire"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Indicateur de force */}
      {showStrength && value && (
        <div className="mt-2 space-y-2">
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
              <div 
                className={`h-full ${couleur.bg} transition-all duration-300`}
                style={{ width: `${couleur.barre}%` }}
              />
            </div>
            <span className={`text-xs font-semibold ${couleur.text}`}>
              {couleur.label}
            </span>
          </div>

          {/* Exigences */}
          <div className="text-xs space-y-1">
            <div className={`flex items-center gap-1 ${validation.regles.longueur ? 'text-emerald-600' : 'text-zinc-500'}`}>
              {validation.regles.longueur ? '✓' : '○'} Au moins 8 caractères
            </div>
            <div className={`flex items-center gap-1 ${validation.regles.majuscule ? 'text-emerald-600' : 'text-zinc-500'}`}>
              {validation.regles.majuscule ? '✓' : '○'} Une majuscule
            </div>
            <div className={`flex items-center gap-1 ${validation.regles.minuscule ? 'text-emerald-600' : 'text-zinc-500'}`}>
              {validation.regles.minuscule ? '✓' : '○'} Une minuscule
            </div>
            <div className={`flex items-center gap-1 ${validation.regles.chiffre ? 'text-emerald-600' : 'text-zinc-500'}`}>
              {validation.regles.chiffre ? '✓' : '○'} Un chiffre
            </div>
            <div className={`flex items-center gap-1 ${validation.regles.special ? 'text-emerald-600' : 'text-zinc-500'}`}>
              {validation.regles.special ? '✓' : '○'} Un caractère spécial (@#$%^&*!)
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
