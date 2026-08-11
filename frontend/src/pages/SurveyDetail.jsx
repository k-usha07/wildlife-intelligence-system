import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  fetchSurvey,
  fetchObservations,
  fetchBiodiversitySummary,
  fetchEcosystemHealth,
  fetchAlerts,
} from '../api/client.js'

const STATUS_COLORS = {
  excellent: '#4c8a5a',
  healthy: '#8fc19a',
  moderate_concern: '#d98b3c',
  vulnerable: '#d98b3c',
  critical: '#b3452f',
}

export default function SurveyDetail() {
  const { id } = useParams()
  const [survey, setSurvey] = useState(null)
  const [observations, setObservations] = useState([])
  const [biodiversity, setBiodiversity] = useState(null)
  const [health, setHealth] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    Promise.all([
      fetchSurvey(id),
      fetchObservations(id),
      fetchBiodiversitySummary(id),
      fetchEcosystemHealth(id),
      fetchAlerts(id),
    ])
      .then(([surv, obs, bio, hlth, alrt]) => {
        setSurvey(surv)
        setObservations(obs)
        setBiodiversity(bio)
        setHealth(hlth)
        setAlerts(alrt)
      })
      .catch((err) => {
        // Analytics endpoints are new — a 404/500 here most likely means
        // the Milestone 2 worker/analytics backend isn't deployed yet,
        // not that anything on this page is broken.
        setError(
          err.response?.status
            ? `Analytics not available yet (status ${err.response.status}). This survey's observations may still be processing, or the Milestone 2 backend isn't deployed.`
            : 'Could not reach the analytics API.',
        )
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <p>Loading survey…</p>

  return (
    <div>
      <Link to="/surveys" style={{ fontSize: '0.85rem' }}>&larr; Back to surveys</Link>
      <h1 style={{ marginTop: '0.5rem' }}>{survey?.name}</h1>
      <p style={{ color: 'var(--color-ink-500)' }}>{survey?.objective}</p>

      {error && (
        <div className="card" style={{ marginBottom: '1.5rem', borderLeft: '4px solid var(--color-amber-500)' }}>
          <p style={{ margin: 0 }}>{error}</p>
        </div>
      )}

      {health && (
        <div className="card-grid">
          <div className="card">
            <div className="stat-label">Ecosystem health score</div>
            <div className="stat-value" style={{ color: STATUS_COLORS[health.conservation_status] }}>
              {health.score}
            </div>
            <span className="badge" style={{ background: STATUS_COLORS[health.conservation_status], color: 'white' }}>
              {health.conservation_status?.replace('_', ' ')}
            </span>
          </div>
          <div className="card">
            <div className="stat-label">Species richness</div>
            <div className="stat-value">{biodiversity?.species_richness ?? '—'}</div>
          </div>
          <div className="card">
            <div className="stat-label">Biodiversity index</div>
            <div className="stat-value">{biodiversity?.shannon_index ?? '—'}</div>
          </div>
          <div className="card">
            <div className="stat-label">Endangered species</div>
            <div className="stat-value">{biodiversity?.endangered_species_count ?? '—'}</div>
          </div>
        </div>
      )}

      {alerts.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem', borderLeft: '4px solid var(--color-alert-600)' }}>
          <h3>Active alerts</h3>
          {alerts.map((a) => (
            <div key={a.id} style={{ padding: '0.5rem 0', borderBottom: '1px solid var(--color-bark-100)' }}>
              <span className="badge" style={{
                background: a.severity === 'critical' ? 'var(--color-alert-600)' : 'var(--color-amber-500)',
                color: 'white',
              }}>
                {a.severity}
              </span>{' '}
              {a.message}
            </div>
          ))}
        </div>
      )}

      {biodiversity?.top_species?.length > 0 && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3>Top species</h3>
          <table>
            <thead>
              <tr><th>Species</th><th>Count</th><th>Share</th></tr>
            </thead>
            <tbody>
              {biodiversity.top_species.map((s) => (
                <tr key={s.species_name}>
                  <td>{s.species_name?.replace(/_/g, ' ')}</td>
                  <td>{s.count}</td>
                  <td>{(s.share * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="card">
        <h3>Observations</h3>
        <table>
          <thead>
            <tr><th>Species</th><th>Confidence</th><th>Endangered</th><th>Notes</th><th>Detected</th></tr>
          </thead>
          <tbody>
            {observations.length === 0 && (
              <tr><td colSpan={5} style={{ color: 'var(--color-ink-500)' }}>
                No observations yet — upload media for this survey to see species detections here.
              </td></tr>
            )}
            {observations.map((o) => (
              <tr key={o.id}>
                <td>{o.species_name?.replace(/_/g, ' ') ?? 'Unidentified'}</td>
                <td>{o.confidence ? `${(o.confidence * 100).toFixed(0)}%` : '—'}</td>
                <td>{o.is_endangered ? '⚠️ Yes' : 'No'}</td>
                <td>{o.notes ?? '—'}</td>
                <td>{new Date(o.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}