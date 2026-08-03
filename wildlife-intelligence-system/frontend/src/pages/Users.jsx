import { useEffect, useState } from 'react'
import { fetchUsers } from '../api/client.js'

export default function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUsers().then(setUsers).finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h1>Users</h1>
      <p style={{ color: 'var(--color-ink-500)' }}>
        Admin-only view of all registered platform users.
      </p>

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Organization</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={5}>Loading…</td></tr>}
            {!loading && users.length === 0 && (
              <tr><td colSpan={5} style={{ color: 'var(--color-ink-500)' }}>No users found.</td></tr>
            )}
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.full_name}</td>
                <td>{u.email}</td>
                <td><span className="badge">{u.role.replace('_', ' ')}</span></td>
                <td>{u.organization || '—'}</td>
                <td>{u.is_active ? 'active' : 'deactivated'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
