import { useAuth } from '../../contexts/AuthContext'
import DashboardEmploye from './DashboardEmploye'
import DashboardPayeur from './DashboardPayeur'
import DashboardAgentFacturation from './DashboardAgentFacturation'

export default function Dashboard() {
  const { isPayeur, isAgentFacturation } = useAuth()

  if (isAgentFacturation()) return <DashboardAgentFacturation />
  return isPayeur() ? <DashboardPayeur /> : <DashboardEmploye />
}
