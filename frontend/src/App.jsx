import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import DashboardLayout from './layouts/DashboardLayout'
import Dashboard from './pages/Dashboard'
import DigitalTwin from './pages/DigitalTwin'
import PPEDetection from './pages/PPEDetection'
import SensorMonitoring from './pages/SensorMonitoring'
import RiskForecast from './pages/RiskForecast'
import ComplianceCases from './pages/ComplianceCases'
import CorrectiveActions from './pages/CorrectiveActions'
import Workers from './pages/Workers'
import Equipment from './pages/Equipment'
import Reports from './pages/Reports'
import AuditTrail from './pages/AuditTrail'
import Settings from './pages/Settings'
import Login from './pages/Login'
import Contractors from './pages/Contractors'
import MobileFieldApp from './pages/MobileFieldApp'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7F8FA]">
      <div className="text-center">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        <p className="text-gray-500 text-sm">Loading Coal Mine Safety System…</p>
      </div>
    </div>
  )
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/mobile"
        element={
          <ProtectedRoute>
            <MobileFieldApp />
          </ProtectedRoute>
        }
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="digital-twin" element={<DigitalTwin />} />
        <Route path="ppe-detection" element={<PPEDetection />} />
        <Route path="sensors" element={<SensorMonitoring />} />
        <Route path="risk-forecast" element={<RiskForecast />} />
        <Route path="compliance-cases" element={<ComplianceCases />} />
        <Route path="actions" element={<CorrectiveActions />} />
        <Route path="workers" element={<Workers />} />
        <Route path="contractors" element={<Contractors />} />
        <Route path="equipment" element={<Equipment />} />
        <Route path="reports" element={<Reports />} />
        <Route path="audit-trail" element={<AuditTrail />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}

