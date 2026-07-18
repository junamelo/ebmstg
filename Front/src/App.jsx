import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/common/ProtectedRoute'
import MainLayout from './components/layout/MainLayout'

// Pages auth
import Login from './pages/auth/Login'
import ForgotPassword from './pages/auth/ForgotPassword'

// Pages communes
import Dashboard from './pages/dashboard/Dashboard'
import Factures from './pages/factures/Factures'
import Simulation from './pages/simulation/Simulation'

// Pages admin (Super Admin uniquement)
import AdminDashboard from './pages/admin/AdminDashboard'
import GestionComptes from './pages/admin/GestionComptes'
import AgentDashboard from './pages/agent/AgentDashboard'
import PublicationPdf from './pages/agent/PublicationPdf'
import GestionForfaits from './pages/agent/GestionForfaits'
import GestionServices from './pages/agent/GestionServices'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Routes publiques */}
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          {/* Routes protégées — Employé & Payeur */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="factures" element={<Factures />} />
            <Route path="simulation" element={<Simulation />} />
          </Route>

          {/* Routes protégées — Agent Facturation uniquement */}
          <Route
            path="/agent"
            element={
              <ProtectedRoute role="AGENT_FACTURATION">
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/agent/dashboard" replace />} />
            <Route path="dashboard" element={<AgentDashboard />} />
            <Route path="publication" element={<PublicationPdf />} />
            <Route path="forfaits" element={<GestionForfaits />} />
            <Route path="services" element={<GestionServices />} />
          </Route>

          {/* Routes protégées — Super Admin uniquement */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute role="ADMIN">
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="comptes" element={<GestionComptes />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
