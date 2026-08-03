import { useEffect, useState } from 'react'
import { createSite, fetchSites } from '../api/client.js'

const HABITATS = ['forest', 'grassland', 'wetland', 'desert', 'coastal', 'marine', 'mountain', 'other']

export default function MonitoringSites() {
  const [sites, setSites] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({
    name: '', habitat_type: 'forest', protected_area: '', latitude: '', longitude: '', description: '',
  })
  const [error, setError] = useState('')

  function load() {
    setLoading(true)
    fetchSites().then(setSites).finally(() => setLoading(false))
  }

  useEffect(load, [])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await createSite({
        ...form,
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
      })
      setShowForm(false)
      setForm({ name: '', habitat_type: 'forest', protected_area: '', latitude: '', longitude: '', description: '' })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create site.')
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Monitoring Sites</h1>
        <button onClick={() => setShowForm((v) => !v)}>{showForm ? 'Cancel' : '+ Register Site'}</button>
      </div>

      {showForm && (
        <form className="card" onSubmit={handleSubmit} style={{ marginBottom: '1.5rem', maxWidth: 480 }}>
          <label htmlFor="name">Site name</label>
          <input id="name" value={form.name} onChange={(e) => update('name', e.target.value)} required />

          <label htmlFor="habitat_type">Habitat type</label>
          <select id="habitat_type" value={form.habitat_type} onChange={(e) => update('habitat_type', e.target.value)}>
            {HABITATS.map((h) => <option key={h} value={h}>{h}</option>)}
          </select>

          <label htmlFor="protected_area">Protected area</label>
          <input id="protected_area" value={form.protected_area} onChange={(e) => update('protected_area', e.target.value)} />

          <div className="form-row">
            <div>
              <label htmlFor="latitude">Latitude</label>
              <input id="latitude" type="number" step="any" value={form.latitude} onChange={(e) => update('latitude', e.target.value)} required />
            </div>
            <div>
              <label htmlFor="longitude">Longitude</label>
              <input id="longitude" type="number" step="any" value={form.longitude} onChange={(e) => update('longitude', e.target.value)} required />
            </div>
          </div>

          <label htmlFor="description">Description</label>
          <textarea id="description" rows={3} value={form.description} onChange={(e) => update('description', e.target.value)} />

          {error && <p className="error-text">{error}</p>}

          <button type="submit">Save site</button>
        </form>
      )}

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Habitat</th>
              <th>Protected area</th>
              <th>Coordinates</th>
              <th>Devices</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={5}>Loading…</td></tr>}
            {!loading && sites.length === 0 && (
              <tr><td colSpan={5} style={{ color: 'var(--color-ink-500)' }}>No monitoring sites yet.</td></tr>
            )}
            {sites.map((s) => (
              <tr key={s.id}>
                <td>{s.name}</td>
                <td><span className="badge">{s.habitat_type}</span></td>
                <td>{s.protected_area || '—'}</td>
                <td>{s.latitude.toFixed(4)}, {s.longitude.toFixed(4)}</td>
                <td>{s.device_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
