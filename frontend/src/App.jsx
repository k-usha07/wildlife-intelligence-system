import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'
import AppShell from './components/AppShell.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import MonitoringSites from './pages/MonitoringSites.jsx'
import Devices from './pages/Devices.jsx'
import Surveys from './pages/Surveys.jsx'
import Users from './pages/Users.jsx'
import SurveyDetail from './pages/SurveyDetail.jsx'
import SpeciesExplorer from './pages/SpeciesExplorer.jsx'
import ImageAnalysis from './pages/ImageAnalysis.jsx'
import AudioAnalysis from './pages/AudioAnalysis.jsx'
import PopulationAnalytics from './pages/PopulationAnalytics.jsx'
import BiodiversityDashboard from './pages/BiodiversityDashboard.jsx'
import HabitatAssessment from './pages/HabitatAssessment.jsx'
import ConservationRecommendations from './pages/ConservationRecommendations.jsx'
import Reports from './pages/Reports.jsx'

// Inside the protected <Route> subtree:
<Route path="species" element={<SpeciesExplorer />} />
<Route path="image-analysis" element={<ImageAnalysis />} />
<Route path="audio-analysis" element={<AudioAnalysis />} />
<Route path="population" element={<PopulationAnalytics />} />
<Route path="biodiversity" element={<BiodiversityDashboard />} />
<Route path="habitat" element={<HabitatAssessment />} />
<Route path="conservation" element={<ConservationRecommendations />} />
<Route path="reports" element={<Reports />} />

function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ padding: '2rem' }}>Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="surveys" element={<Surveys />} />
        <Route path="surveys/:id" element={<SurveyDetail />} />
        <Route path="monitoring-sites" element={<MonitoringSites />} />
        <Route path="devices" element={<Devices />} />
        <Route path="species" element={<SpeciesExplorer />} />
        <Route path="image-analysis" element={<ImageAnalysis />} />
        <Route path="audio-analysis" element={<AudioAnalysis />} />
        <Route path="population" element={<PopulationAnalytics />} />
        <Route path="biodiversity" element={<BiodiversityDashboard />} />
        <Route path="habitat" element={<HabitatAssessment />} />
        <Route path="conservation" element={<ConservationRecommendations />} />
        <Route path="reports" element={<Reports />} />
        <Route
          path="users"
          element={
            <ProtectedRoute roles={['admin']}>
              <Users />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
