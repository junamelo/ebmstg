import axios from 'axios'

// Instance Axios de base — toutes les requêtes passent par ici
const api = axios.create({
  baseURL: 'http://localhost:8000/api',  // Backend Django sur port 8000
  headers: {
    'Content-Type': 'application/json',
  },
})

// Intercepteur requête : ajoute le token JWT automatiquement
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      // Console.log seulement en dev
      if (import.meta.env?.DEV) {
        console.log('🔑 Token envoyé:', token.substring(0, 20) + '...')
      }
    } else {
      if (import.meta.env?.DEV) {
        console.log('⚠️ Aucun token disponible')
      }
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Intercepteur réponse : gère les erreurs globalement
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (import.meta.env?.DEV) {
      console.log('❌ API Error:', error.response?.status, error.response?.data)
    }
    
    if (error.response?.status === 401) {
      if (import.meta.env?.DEV) {
        console.log('🔐 Token expiré - déconnexion automatique')
      }
      // Token expiré ou invalide → déconnexion
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Éviter la redirection infinie si on est déjà sur /login
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
