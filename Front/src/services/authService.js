import api from './api'
import { mockLogin, mockDemanderReinitialisationMdp } from './mockApi'

// ⚠️ Mettre à false quand le backend .NET sera prêt
const USE_MOCK = true

/**
 * Connexion d'un utilisateur
 * Comptes de test :
 *   Admin            → login: admin@moov.tg   / mdp: admin123
 *   Payeur           → login: A0007612        / mdp: payeur123
 *   Employé          → login: 79342735        / mdp: 5678
 *   Agent Facturation→ login: agent@moov.tg   / mdp: agent123
 */
export const login = async (loginVal, motDePasse, typeLogin) => {
  if (USE_MOCK) return mockLogin(loginVal, motDePasse, typeLogin)
  const response = await api.post('/auth/login', { login: loginVal, motDePasse, typeLogin })
  return response.data
}

export const demanderReinitialisationMdp = async (email) => {
  if (USE_MOCK) return mockDemanderReinitialisationMdp(email)
  const response = await api.post('/auth/forgot-password', { email })
  return response.data
}

export const reinitialiserMdp = async (token, nouveauMotDePasse) => {
  const response = await api.post('/auth/reset-password', { token, nouveauMotDePasse })
  return response.data
}

export const logout = async () => {
  if (USE_MOCK) return
  try { await api.post('/auth/logout') } catch { /* nettoyage localStorage géré dans AuthContext */ }
}
