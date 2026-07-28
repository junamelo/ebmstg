import { useAuth } from '../../contexts/AuthContext'
import DashboardEmploye from './DashboardEmploye'
import DashboardPayeur from './DashboardPayeur'
import AgentDashboard from '../agent/AgentDashboard'

export default function Dashboard() {
  const { isPayeur, isAgentFacturation, isChefFacturation } = useAuth()

  // Chaque rôle a son propre dashboard
  if (isChefFacturation()) return <AgentDashboard />
  if (isAgentFacturation()) return <AgentDashboard />
  return isPayeur() ? <DashboardPayeur /> : <DashboardEmploye />
}
