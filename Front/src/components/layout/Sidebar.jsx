import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import './Sidebar.css'

const IconDashboard   = () => <i className="ti ti-layout-dashboard" style={{ fontSize: 18 }} />
const IconFactures    = () => <i className="ti ti-file-invoice"     style={{ fontSize: 18 }} />
const IconSimulation  = () => <i className="ti ti-calculator"       style={{ fontSize: 18 }} />
const IconHistorique  = () => <i className="ti ti-history"          style={{ fontSize: 18 }} />
const IconPublication = () => <i className="ti ti-cloud-upload"     style={{ fontSize: 18 }} />
const IconComptes     = () => <i className="ti ti-users"            style={{ fontSize: 18 }} />
const IconUsers       = () => <i className="ti ti-users-group"      style={{ fontSize: 18 }} />
const IconForfaits    = () => <i className="ti ti-package"          style={{ fontSize: 18 }} />
const IconServices    = () => <i className="ti ti-settings"         style={{ fontSize: 18 }} />
const IconProfil      = () => <i className="ti ti-user-circle"      style={{ fontSize: 18 }} />
const IconLignes      = () => <i className="ti ti-phone"            style={{ fontSize: 18 }} />
const IconChevron     = ({ collapsed }) => (
  <i 
    className={`ti ti-chevron-${collapsed ? 'right' : 'left'}`} 
    style={{ fontSize: 18 }} 
  />
)

const IconAgents     = () => <i className="ti ti-user-check"       style={{ fontSize: 18 }} />
const IconContrats   = () => <i className="ti ti-file-text"        style={{ fontSize: 18 }} />

const menusEmploye = [
  { path: '/dashboard',             label: 'Tableau de bord',     icon: <IconDashboard /> },
  { path: '/factures',              label: 'Mes factures',        icon: <IconFactures /> },
  { path: '/simulation',            label: 'Simulation',          icon: <IconSimulation /> },
  { path: '/simulation/historique', label: 'Historique',          icon: <IconHistorique /> },
  { path: '/profil',                label: 'Mon profil',          icon: <IconProfil /> },
]

const menusPayeur = [
  { path: '/dashboard',             label: 'Tableau de bord',     icon: <IconDashboard /> },
  { path: '/factures',              label: 'Factures',            icon: <IconFactures /> },
  { path: '/lignes',                label: 'Mes lignes',          icon: <IconLignes /> },
  { path: '/simulation',            label: 'Simulation',          icon: <IconSimulation /> },
  { path: '/simulation/historique', label: 'Historique',          icon: <IconHistorique /> },
  { path: '/profil',                label: 'Mon profil',          icon: <IconProfil /> },
]

const menusAdmin = [
  { path: '/admin/dashboard', label: 'Tableau de bord', icon: <IconDashboard /> },
  { path: '/admin/comptes',   label: 'Gestion comptes', icon: <IconComptes /> },
  { path: '/admin/contrats',  label: 'Gestion Contrats', icon: <IconContrats /> },
  { path: '/admin/services',  label: 'Gestion Services', icon: <IconServices /> },
  { path: '/admin/forfaits',  label: 'Gestion Forfaits', icon: <IconForfaits /> },
  { path: '/admin/publication', label: 'Publication PDF', icon: <IconPublication /> },
  { path: '/admin/publication/historique', label: 'Historique Pub.', icon: <IconHistorique /> },
  { path: '/admin/profil',    label: 'Mon profil',      icon: <IconProfil /> },
]

const menusAgentFacturation = [
  { path: '/agent/dashboard',                label: 'Dashboard',           icon: <IconDashboard /> },
  { path: '/agent/contrats',                 label: 'Gestion Contrats',    icon: <IconContrats /> },
  { path: '/agent/comptes-clients',          label: 'Comptes Clients',     icon: <IconUsers /> },
  { path: '/agent/services',                 label: 'Gestion Services',    icon: <IconServices /> },
  { path: '/agent/forfaits',                 label: 'Gestion Forfaits',    icon: <IconForfaits /> },
  { path: '/agent/publication',              label: 'Publication PDF',     icon: <IconPublication /> },
  { path: '/agent/publication/historique',   label: 'Historique Pub.',     icon: <IconHistorique /> },
  { path: '/agent/profil',                   label: 'Mon profil',          icon: <IconProfil /> },
]

const menusChefFacturation = [
  { path: '/chef/dashboard',                label: 'Dashboard',           icon: <IconDashboard /> },
  { path: '/chef/agents',                   label: 'Gestion Agents',      icon: <IconAgents /> },
  { path: '/chef/contrats',                 label: 'Gestion Contrats',    icon: <IconContrats /> },
  { path: '/chef/comptes-clients',          label: 'Comptes Clients',     icon: <IconUsers /> },
  { path: '/chef/services',                 label: 'Gestion Services',    icon: <IconServices /> },
  { path: '/chef/forfaits',                 label: 'Gestion Forfaits',    icon: <IconForfaits /> },
  { path: '/chef/publication',              label: 'Publication PDF',     icon: <IconPublication /> },
  { path: '/chef/publication/historique',   label: 'Historique Pub.',     icon: <IconHistorique /> },
  { path: '/chef/profil',                   label: 'Mon profil',          icon: <IconProfil /> },
]

export default function Sidebar() {
  const { isAdmin, isPayeur, isAgentFacturation, isChefFacturation } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  const menus = isAdmin()
    ? menusAdmin
    : isChefFacturation()
    ? menusChefFacturation
    : isAgentFacturation()
    ? menusAgentFacturation
    : isPayeur()
    ? menusPayeur
    : menusEmploye

  const accent = isPayeur() ? '#e05500' : '#002a7a'
  const roleText = isAdmin() ? 'Administration'
    : isChefFacturation() ? 'Chef Facturation'
    : isAgentFacturation() ? 'Agent Facturation'
    : isPayeur() ? 'Espace Entreprise'
    : 'Espace Employé'

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Bouton de toggle amélioré */}
      <button 
        className="sidebar-toggle"
        onClick={() => setCollapsed(!collapsed)}
        title={collapsed ? 'Agrandir la sidebar' : 'Réduire la sidebar'}
        style={{ '--accent-color': accent }}
      >
        <IconChevron collapsed={collapsed} />
      </button>

      {/* Bandeau rôle avec icône */}
      <div className="sidebar-role-band" style={{ background: accent }}>
        {!collapsed ? (
          <>
            <i className="ti ti-shield-check" style={{ fontSize: 14, marginRight: 6 }} />
            {roleText}
          </>
        ) : (
          <i className="ti ti-shield-check" style={{ fontSize: 16 }} />
        )}
      </div>

      <nav className="sidebar-nav">
        {menus.map((item, index) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={
              item.path === '/simulation' || 
              item.path === '/dashboard' || 
              item.path === '/factures' ||
              item.path === '/profil' ||
              item.path === '/agent/publication' ||
              item.path === '/chef/publication' ||
              item.path === '/admin/publication'
            }
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            style={({ isActive }) => isActive ? { 
              backgroundColor: accent, 
              color: 'white',
              boxShadow: `0 4px 12px ${accent}40`
            } : {}}
            title={collapsed ? item.label : ''}
          >
            <span className="sidebar-icon">{item.icon}</span>
            {!collapsed && <span className="sidebar-label">{item.label}</span>}
            {!collapsed && <span className="sidebar-indicator"></span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
