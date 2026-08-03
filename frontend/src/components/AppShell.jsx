import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/surveys', label: 'Surveys' },
  { to: '/monitoring-sites', label: 'Monitoring Sites' },
  { to: '/devices', label: 'Devices' },
  { to: '/users', label: 'Users', roles: ['admin'] },
]

export default function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">🌿 WPI System</div>
        {NAV_ITEMS.filter((item) => !item.roles || item.roles.includes(user?.role)).map((item) => (
          <NavLink key={item.to} to={item.to} end={item.end}>
            {item.label}
          </NavLink>
        ))}
      </aside>
      <div>
        <header className="topbar">
          <span className="badge">{user?.role?.replace('_', ' ')}</span>
          <div>
            <span style={{ marginRight: '1rem' }}>{user?.full_name}</span>
            <button className="secondary" onClick={handleLogout}>Log out</button>
          </div>
        </header>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
