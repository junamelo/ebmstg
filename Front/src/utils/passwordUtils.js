/**
 * Utilitaires pour la gestion des mots de passe
 */

/**
 * Génère un mot de passe par défaut basé sur la date du jour
 * Format : Moov@AAAAMMJJ
 * @returns {string} Mot de passe par défaut
 */
export const genererMotDePasseDefaut = () => {
  const date = new Date()
  const annee = date.getFullYear()
  const mois = String(date.getMonth() + 1).padStart(2, '0')
  const jour = String(date.getDate()).padStart(2, '0')
  
  return `Moov@${annee}${mois}${jour}`
}

/**
 * Génère un mot de passe aléatoire sécurisé
 * @param {number} longueur - Longueur du mot de passe (défaut: 12)
 * @returns {string} Mot de passe aléatoire
 */
export const genererMotDePasseAleatoire = (longueur = 12) => {
  const majuscules = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  const minuscules = 'abcdefghijklmnopqrstuvwxyz'
  const chiffres = '0123456789'
  const speciaux = '@#$%^&*!'
  const tous = majuscules + minuscules + chiffres + speciaux
  
  let mdp = ''
  
  // S'assurer qu'il y a au moins un caractère de chaque type
  mdp += majuscules[Math.floor(Math.random() * majuscules.length)]
  mdp += minuscules[Math.floor(Math.random() * minuscules.length)]
  mdp += chiffres[Math.floor(Math.random() * chiffres.length)]
  mdp += speciaux[Math.floor(Math.random() * speciaux.length)]
  
  // Compléter avec des caractères aléatoires
  for (let i = mdp.length; i < longueur; i++) {
    mdp += tous[Math.floor(Math.random() * tous.length)]
  }
  
  // Mélanger les caractères
  return mdp.split('').sort(() => Math.random() - 0.5).join('')
}

/**
 * Valide un mot de passe selon les règles de sécurité
 * @param {string} mdp - Mot de passe à valider
 * @returns {object} { valide: boolean, regles: object, force: string }
 */
export const validerMotDePasse = (mdp) => {
  if (!mdp) {
    return {
      valide: false,
      regles: {
        longueur: false,
        majuscule: false,
        minuscule: false,
        chiffre: false,
        special: false
      },
      force: 'vide'
    }
  }
  
  const regles = {
    longueur: mdp.length >= 8,
    majuscule: /[A-Z]/.test(mdp),
    minuscule: /[a-z]/.test(mdp),
    chiffre: /[0-9]/.test(mdp),
    special: /[@#$%^&*!]/.test(mdp)
  }
  
  const valide = Object.values(regles).every(r => r)
  
  // Calcul de la force
  const score = Object.values(regles).filter(r => r).length
  let force = 'faible'
  if (score === 5 && mdp.length >= 12) force = 'excellent'
  else if (score === 5) force = 'fort'
  else if (score >= 4) force = 'moyen'
  
  return { valide, regles, force }
}

/**
 * Génère un login unique pour un payeur
 * Format : A + année(2) + numéro séquentiel(6)
 * @returns {string} Login unique
 */
export const genererLoginPayeur = () => {
  const annee = new Date().getFullYear().toString().slice(-2)
  const sequence = Math.floor(Math.random() * 999999).toString().padStart(6, '0')
  return `A${annee}${sequence}`
}

/**
 * Génère un login pour un employé basé sur son numéro de ligne
 * Format : Numéro sans espaces
 * @param {string} numeroLigne - Numéro de ligne (ex: "79 34 27 35")
 * @returns {string} Login
 */
export const genererLoginEmploye = (numeroLigne) => {
  return numeroLigne.replace(/\s+/g, '')
}

/**
 * Obtient la couleur selon la force du mot de passe
 * @param {string} force - Force du mot de passe
 * @returns {object} { bg, text, label }
 */
export const getCouleurForce = (force) => {
  const couleurs = {
    vide: { bg: 'bg-zinc-200', text: 'text-zinc-600', label: 'Aucun', barre: 0 },
    faible: { bg: 'bg-red-500', text: 'text-red-600', label: 'Faible', barre: 25 },
    moyen: { bg: 'bg-orange-500', text: 'text-orange-600', label: 'Moyen', barre: 50 },
    fort: { bg: 'bg-blue-500', text: 'text-blue-600', label: 'Fort', barre: 75 },
    excellent: { bg: 'bg-emerald-500', text: 'text-emerald-600', label: 'Excellent', barre: 100 }
  }
  return couleurs[force] || couleurs.vide
}
