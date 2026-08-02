import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import ImageWithFallback from '../common/ImageWithFallback'
import logoMoov from '../../assets/logo-moov.png'
import './Navbar.css'

export default function Navbar() {
  const { user, logout, isAdmin, isPayeur, isAgentFacturation, isChefFacturation } = useAuth()
  const navigate = useNavigate()
  const [menuOuvert, setMenuOuvert] = useState(false)

  // Couleur navbar selon le rôle — orange pour payeur, bleu pour le reste
  const navBg = isPayeur()
    ? 'linear-gradient(135deg, #7a2000 0%, #c44200 50%, #e05500 100%)'
    : 'linear-gradient(135deg, var(--moov-blue) 0%, #004db3 100%)'

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getHomeLink = () => {
    if (isAdmin()) return '/admin/dashboard'
    if (isChefFacturation()) return '/chef/dashboard'
    if (isAgentFacturation()) return '/agent/dashboard'
    return '/dashboard'
  }

  const getProfilLink = () => {
    if (isAdmin()) return '/admin/profil'
    if (isChefFacturation()) return '/chef/profil'
    if (isAgentFacturation()) return '/agent/profil'
    return '/profil'
  }

  const getRoleLabel = () => {
    if (isAdmin()) return 'Super Administrateur'
    if (isAgentFacturation()) return 'Agent Facturation'
    if (isPayeur()) return 'Compte Entreprise'
    return 'Employé'
  }

  const getRoleBadgeClass = () => {
    if (isAdmin()) return 'badge-admin'
    if (isAgentFacturation()) return 'badge-agent'
    if (isPayeur()) return 'badge-payeur'
    return 'badge-employe'
  }

  return (
    <nav className="navbar" style={{ background: navBg }}>
      <div className="navbar-brand">
        <Link to={getHomeLink()} className="navbar-logo-link">
          <ImageWithFallback src={logoMoov} alt="Moov Africa" className="navbar-logo-img" />
        </Link>
        <span className="navbar-title">Portail Factures</span>
      </div>

      <div className="navbar-user">
        <div className="user-menu" onClick={() => setMenuOuvert(!menuOuvert)}>
          <div className="user-avatar">
            {user?.prenom?.[0]}{user?.nom?.[0]}
          </div>
          <span className="user-name">{user?.prenom} {user?.nom}</span>
          <span className="chevron">▾</span>

          {menuOuvert && (
            <div className="dropdown-menu">
              <Link to={getProfilLink()} className="dropdown-item" onClick={() => setMenuOuvert(false)}>
                <i className="ti ti-user-circle" style={{ fontSize: 16, marginRight: 8 }} />
                Mon profil
              </Link>
              <hr className="dropdown-divider" />
              <button className="dropdown-item dropdown-logout" onClick={handleLogout}>
                <i className="ti ti-logout" style={{ fontSize: 16, marginRight: 8 }} />
                Déconnexion
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
