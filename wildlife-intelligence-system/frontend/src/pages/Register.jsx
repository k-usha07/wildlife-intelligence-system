import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const ROLES = [
  { value: 'researcher', label: 'Wildlife Researcher' },
  { value: 'conservation_officer', label: 'Conservation Officer' },
  { value: 'forest_department', label: 'Forest Department Officer' },
]

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    full_name: '', email: '', password: '', role: 'researcher', organization: '',
  })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      await register(form)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h2>Create account</h2>

        <label htmlFor="full_name">Full name</label>
        <input id="full_name" value={form.full_name} onChange={(e) => update('full_name', e.target.value)} required />

        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={(e) => update('email', e.target.value)} required />

        <label htmlFor="password">Password</label>
        <input id="password" type="password" minLength={8} value={form.password} onChange={(e) => update('password', e.target.value)} required />

        <label htmlFor="role">Role</label>
        <select id="role" value={form.role} onChange={(e) => update('role', e.target.value)}>
          {ROLES.map((r) => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>

        <label htmlFor="organization">Organization (optional)</label>
        <input id="organization" value={form.organization} onChange={(e) => update('organization', e.target.value)} />

        {error && <p className="error-text">{error}</p>}

        <button type="submit" disabled={busy} style={{ width: '100%' }}>
          {busy ? 'Creating…' : 'Register'}
        </button>

        <p style={{ marginTop: '1rem', fontSize: '0.85rem' }}>
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </div>
  )
}
