import api from './api'

// Backend Django prêt pour auth !

/**
 * Connexion d'un utilisateur
 * Endpoint: POST /api/auth/login/
 * Comptes de test disponibles :
 *   Admin            → login: admin@moov.tg      / mdp: admin123
 *   Chef Facturation → login: chef@moov.tg       / mdp: chef123
 *   Agent Facturation→ login: agent@moov.tg      / mdp: agent123
 *   Payeur           → login: A26TEST001         / mdp: payeur123
 *   Employé          → login: 99475555           / mdp: employe123
 */
export const login = async (loginVal, motDePasse, typeLogin) => {
  // Adapter les paramètres pour l'API Django
  const response = await api.post('/auth/login/', { 
    email: loginVal,  // Django backend attend 'email' 
    password: motDePasse  // Django backend attend 'password'
  })
  return response.data
}

/**
 * Demande de réinitialisation de mot de passe
 * Endpoint: POST /api/auth/forgot-password/
 */
export const demanderReinitialisationMdp = async (email) => {
  const response = await api.post('/auth/forgot-password/', { email })
  return response.data
}

/**
 * Réinitialisation du mot de passe
 * Endpoint: POST /api/auth/reset-password/
 */
export const reinitialiserMdp = async (token, nouveauMotDePasse) => {
  const response = await api.post('/auth/reset-password/', { token, nouveauMotDePasse })
  return response.data
}

/**
 * Déconnexion de l'utilisateur
 * Endpoint: POST /api/auth/logout/
 */
export const logout = async () => {
  try { 
    await api.post('/auth/logout/') 
  } catch { 
    /* nettoyage localStorage géré dans AuthContext */ 
  }
}
