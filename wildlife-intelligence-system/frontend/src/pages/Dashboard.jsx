import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { fetchSummary, fetchSurveys } from '../api/client.js'

export default function Dashboard() {
  const { user } = useAuth()
  const [summary, setSummary] = useState(null)
  const [surveys, setSurveys] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([fetchSummary(), fetchSurveys()])
      .then(([s, surv]) => {
        setSummary(s)
        setSurveys(surv)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h1>Welcome back, {user?.full_name}</h1>
      <p style={{ color: 'var(--color-ink-500)' }}>
        Here's what's happening across your wildlife monitoring workflows.
      </p>

      {loading ? (
        <p>Loading dashboard…</p>
      ) : (
        <>
          <div className="card-grid">
            <div className="card">
              <div className="stat-label">Active surveys</div>
              <div className="stat-value">{summary?.active_surveys ?? 0}</div>
            </div>
            <div className="card">
              <div className="stat-label">Monitoring sites</div>
              <div className="stat-value">{summary?.monitoring_sites ?? 0}</div>
            </div>
            <div className="card">
              <div className="stat-label">My uploads</div>
              <div className="stat-value">{summary?.my_uploads ?? 0}</div>
            </div>
            <div className="card">
              <div className="stat-label">Species tagged</div>
              <div className="stat-value">{summary?.species_tagged ?? 0}</div>
            </div>
          </div>

          <div className="card">
            <h3>Recent surveys</h3>
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Sites</th>
                  <th>Status</th>
                  <th>Start</th>
                  <th>End</th>
                </tr>
              </thead>
              <tbody>
                {surveys.length === 0 && (
                  <tr><td colSpan={5} style={{ color: 'var(--color-ink-500)' }}>No surveys yet. Create one from the Surveys tab.</td></tr>
                )}
                {surveys.map((s) => (
                  <tr key={s.id}>
                    <td>{s.name}</td>
                    <td>{s.site_count}</td>
                    <td><span className="badge">{s.status}</span></td>
                    <td>{s.start_date}</td>
                    <td>{s.end_date ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
