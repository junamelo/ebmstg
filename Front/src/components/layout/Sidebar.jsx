import { NavLink } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import './Sidebar.css'

const IconDashboard   = () => <i className="ti ti-layout-dashboard" style={{ fontSize: 18 }} />
const IconFactures    = () => <i className="ti ti-file-invoice"     style={{ fontSize: 18 }} />
const IconSimulation  = () => <i className="ti ti-calculator"       style={{ fontSize: 18 }} />
const IconHistorique  = () => <i className="ti ti-history"          style={{ fontSize: 18 }} />
const IconPublication = () => <i className="ti ti-cloud-upload"     style={{ fontSize: 18 }} />
const IconComptes     = () => <i className="ti ti-users"            style={{ fontSize: 18 }} />
const IconForfaits    = () => <i className="ti ti-package"          style={{ fontSize: 18 }} />
const IconServices    = () => <i className="ti ti-settings"         style={{ fontSize: 18 }} />

const menusEmploye = [
  { path: '/dashboard',             label: 'Tableau de bord',     icon: <IconDashboard /> },
  { path: '/factures',              label: 'Mes factures',        icon: <IconFactures /> },
  { path: '/simulation',            label: 'Simulation',          icon: <IconSimulation /> },
  { path: '/simulation/historique', label: 'Historique',          icon: <IconHistorique /> },
]

const menusPayeur = [
  { path: '/dashboard',             label: 'Tableau de bord',     icon: <IconDashboard /> },
  { path: '/factures',              label: 'Factures',            icon: <IconFactures /> },
  { path: '/simulation',            label: 'Simulation',          icon: <IconSimulation /> },
  { path: '/simulation/historique', label: 'Historique',          icon: <IconHistorique /> },
]

const menusAdmin = [
  { path: '/admin/dashboard', label: 'Tableau de bord', icon: <IconDashboard /> },
  { path: '/admin/comptes',   label: 'Gestion comptes', icon: <IconComptes /> },
]

const menusAgentFacturation = [
  { path: '/agent/dashboard',   label: 'Dashboard',        icon: <IconDashboard /> },
  { path: '/agent/forfaits',    label: 'Gestion Forfaits', icon: <IconForfaits /> },
  { path: '/agent/services',    label: 'Gestion Services', icon: <IconServices /> },
  { path: '/agent/publication', label: 'Publication PDF',  icon: <IconPublication /> },
]

export default function Sidebar() {
  const { isAdmin, isPayeur, isAgentFacturation } = useAuth()

  const menus = isAdmin()
    ? menusAdmin
    : isAgentFacturation()
    ? menusAgentFacturation
    : isPayeur()
    ? menusPayeur
    : menusEmploye

  const accent = isPayeur() ? '#e05500' : '#002a7a'

  return (
    <aside className="sidebar">
      <div className="sidebar-role-band" style={{ background: accent }}>
        {isAdmin() ? 'Administration'
          : isAgentFacturation() ? 'Agent Facturation'
          : isPayeur() ? 'Espace Entreprise'
          : 'Espace Employé'}
      </div>

      <nav className="sidebar-nav">
        {menus.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/simulation' || item.path === '/dashboard' || item.path === '/factures'}
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            style={({ isActive }) => isActive ? { backgroundColor: accent, color: 'white' } : {}}
          >
            <span className="sidebar-icon">{item.icon}</span>
            <span className="sidebar-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className="sidebar-version">v1.0.0</span>
      </div>
    </aside>
  )
}
