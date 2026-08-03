import { useEffect, useState } from 'react'
import { createSurvey, fetchSites, fetchSurveys } from '../api/client.js'

export default function Surveys() {
  const [surveys, setSurveys] = useState([])
  const [sites, setSites] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({
    name: '', objective: '', start_date: '', end_date: '', site_ids: [],
  })
  const [error, setError] = useState('')

  function load() {
    setLoading(true)
    Promise.all([fetchSurveys(), fetchSites()])
      .then(([surv, s]) => {
        setSurveys(surv)
        setSites(s)
      })
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function toggleSite(id) {
    setForm((f) => {
      const has = f.site_ids.includes(id)
      return { ...f, site_ids: has ? f.site_ids.filter((x) => x !== id) : [...f.site_ids, id] }
    })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await createSurvey({ ...form, end_date: form.end_date || null })
      setShowForm(false)
      setForm({ name: '', objective: '', start_date: '', end_date: '', site_ids: [] })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create survey.')
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Surveys</h1>
        <button onClick={() => setShowForm((v) => !v)}>{showForm ? 'Cancel' : '+ New Survey'}</button>
      </div>

      {showForm && (
        <form className="card" onSubmit={handleSubmit} style={{ marginBottom: '1.5rem', maxWidth: 520 }}>
          <label htmlFor="name">Survey name</label>
          <input id="name" value={form.name} onChange={(e) => update('name', e.target.value)} required />

          <label htmlFor="objective">Objective</label>
          <textarea id="objective" rows={2} value={form.objective} onChange={(e) => update('objective', e.target.value)} />

          <div className="form-row">
            <div>
              <label htmlFor="start_date">Start date</label>
              <input id="start_date" type="date" value={form.start_date} onChange={(e) => update('start_date', e.target.value)} required />
            </div>
            <div>
              <label htmlFor="end_date">End date</label>
              <input id="end_date" type="date" value={form.end_date} onChange={(e) => update('end_date', e.target.value)} />
            </div>
          </div>

          <label>Monitoring sites</label>
          <div style={{ marginBottom: '0.9rem' }}>
            {sites.length === 0 && <p style={{ color: 'var(--color-ink-500)', fontSize: '0.85rem' }}>No sites registered yet.</p>}
            {sites.map((s) => (
              <label key={s.id} style={{ fontWeight: 400, display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.3rem' }}>
                <input
                  type="checkbox"
                  style={{ width: 'auto', margin: 0 }}
                  checked={form.site_ids.includes(s.id)}
                  onChange={() => toggleSite(s.id)}
                />
                {s.name}
              </label>
            ))}
          </div>

          {error && <p className="error-text">{error}</p>}

          <button type="submit">Create survey</button>
        </form>
      )}

      <div className="card">
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
            {loading && <tr><td colSpan={5}>Loading…</td></tr>}
            {!loading && surveys.length === 0 && (
              <tr><td colSpan={5} style={{ color: 'var(--color-ink-500)' }}>No surveys yet.</td></tr>
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
    </div>
  )
}
