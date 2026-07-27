import { Navigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

/**
 * Protège une route — redirige vers /login si non connecté
 * @param {string} role - rôle requis ('ADMIN' | 'PAYEUR' | 'EMPLOYE' | 'AGENT_FACTURATION' | 'CHEF_FACTURATION' | null pour tout rôle)
 */
export default function ProtectedRoute({ children, role = null }) {
  const { user, loading, isAdmin, isPayeur, isEmploye, isAgentFacturation, isChefFacturation } = useAuth()

  if (loading) {
    return (
      <div className="loading-overlay">
        <div className="spinner"></div>
        <span>Chargement...</span>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  // Vérification du rôle si précisé
  if (role === 'ADMIN' && !isAdmin()) {
    return <Navigate to="/dashboard" replace />
  }

  if (role === 'AGENT_FACTURATION' && !isAgentFacturation() && !isChefFacturation()) {
    return <Navigate to="/dashboard" replace />
  }
  
  if (role === 'CHEF_FACTURATION' && !isChefFacturation() && !isAdmin()) {
    return <Navigate to="/dashboard" replace />
  }

  if (role === 'PAYEUR' && !isPayeur() && !isAdmin()) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}
