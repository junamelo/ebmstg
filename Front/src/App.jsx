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
import HistoriqueSimulations from './pages/simulation/HistoriqueSimulations'
import MonProfil from './pages/profile/MonProfil'
import MesLignes from './pages/payeur/MesLignes'

// Pages admin (Super Admin uniquement)
import AdminDashboard from './pages/admin/AdminDashboard'
import GestionComptes from './pages/admin/GestionComptes'
import AgentDashboard from './pages/agent/AgentDashboard'
import PublicationPdf from './pages/agent/PublicationPdf'
import FacturesAPublier from './pages/agent/FacturesAPublier'
import HistoriquePublications from './pages/agent/HistoriquePublications'
import GestionForfaits from './pages/agent/GestionForfaits'
import GestionServices from './pages/agent/GestionServices'
import GestionAgents from './pages/agent/GestionAgents'
import GestionComptesClients from './pages/agent/GestionComptesClients'
import GestionContrats from './pages/agent/GestionContrats'
import DetailContrat from './pages/agent/DetailContrat'

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
            <Route path="lignes" element={<MesLignes />} />
            <Route path="simulation" element={<Simulation />} />
            <Route path="simulation/historique" element={<HistoriqueSimulations />} />
            <Route path="profil" element={<MonProfil />} />
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
            <Route path="agents" element={<GestionAgents />} />
            <Route path="comptes-clients" element={<GestionComptesClients />} />
            <Route path="contrats" element={<GestionContrats />} />
            <Route path="contrats/:id" element={<DetailContrat />} />
            <Route path="publication" element={<PublicationPdf />} />
            <Route path="factures-a-publier" element={<FacturesAPublier />} />
            <Route path="publication/historique" element={<HistoriquePublications />} />
            <Route path="services" element={<GestionForfaits />} />
            <Route path="forfaits" element={<GestionServices />} />
            <Route path="profil" element={<MonProfil />} />
          </Route>
          
          {/* Routes protégées — Chef Facturation */}
          <Route
            path="/chef"
            element={
              <ProtectedRoute role="CHEF_FACTURATION">
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/chef/dashboard" replace />} />
            <Route path="dashboard" element={<AgentDashboard />} />
            <Route path="agents" element={<GestionAgents />} />
            <Route path="comptes-clients" element={<GestionComptesClients />} />
            <Route path="contrats" element={<GestionContrats />} />
            <Route path="contrats/:id" element={<DetailContrat />} />
            <Route path="publication" element={<PublicationPdf />} />
            <Route path="factures-a-publier" element={<FacturesAPublier />} />
            <Route path="publication/historique" element={<HistoriquePublications />} />
            <Route path="services" element={<GestionForfaits />} />
            <Route path="forfaits" element={<GestionServices />} />
            <Route path="profil" element={<MonProfil />} />
          </Route>

          {/* Routes protégées — Super Admin uniquement */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute role="SUPER_ADMIN">
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="comptes" element={<GestionComptes />} />
            <Route path="contrats" element={<GestionContrats />} />
            <Route path="contrats/:id" element={<DetailContrat />} />
            <Route path="services" element={<GestionForfaits />} />
            <Route path="forfaits" element={<GestionServices />} />
            <Route path="publication" element={<PublicationPdf />} />
            <Route path="publication/historique" element={<HistoriquePublications />} />
            <Route path="profil" element={<MonProfil />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
