import { useEffect, useState } from 'react'
import { createDevice, fetchDevices, fetchSites } from '../api/client.js'

const DEVICE_TYPES = ['camera_trap', 'audio_sensor', 'drone', 'environmental_sensor']
const STATUSES = ['active', 'inactive', 'maintenance', 'lost']

export default function Devices() {
  const [devices, setDevices] = useState([])
  const [sites, setSites] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(true)
  const [form, setForm] = useState({
    device_code: '', device_type: 'camera_trap', monitoring_site_id: '', status: 'active', notes: '',
  })
  const [error, setError] = useState('')

  function load() {
    setLoading(true)
    Promise.all([fetchDevices(), fetchSites()])
      .then(([d, s]) => {
        setDevices(d)
        setSites(s)
        if (s.length > 0) setForm((f) => ({ ...f, monitoring_site_id: f.monitoring_site_id || s[0].id }))
      })
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function siteName(id) {
    return sites.find((s) => s.id === id)?.name || '—'
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      await createDevice(form)
      setShowForm(false)
      setForm((f) => ({ ...f, device_code: '', notes: '' }))
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not register device.')
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Devices</h1>
        <button onClick={() => setShowForm((v) => !v)} disabled={sites.length === 0}>
          {showForm ? 'Cancel' : '+ Add Device'}
        </button>
      </div>

      {sites.length === 0 && !loading && (
        <p style={{ color: 'var(--color-ink-500)' }}>
          Register a monitoring site first before adding devices.
        </p>
      )}

      {showForm && (
        <form className="card" onSubmit={handleSubmit} style={{ marginBottom: '1.5rem', maxWidth: 480 }}>
          <label htmlFor="device_code">Device ID / code</label>
          <input id="device_code" placeholder="e.g. CT-014" value={form.device_code} onChange={(e) => update('device_code', e.target.value)} required />

          <label htmlFor="device_type">Device type</label>
          <select id="device_type" value={form.device_type} onChange={(e) => update('device_type', e.target.value)}>
            {DEVICE_TYPES.map((t) => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
          </select>

          <label htmlFor="monitoring_site_id">Monitoring site</label>
          <select id="monitoring_site_id" value={form.monitoring_site_id} onChange={(e) => update('monitoring_site_id', e.target.value)}>
            {sites.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>

          <label htmlFor="status">Status</label>
          <select id="status" value={form.status} onChange={(e) => update('status', e.target.value)}>
            {STATUSES.map((st) => <option key={st} value={st}>{st}</option>)}
          </select>

          <label htmlFor="notes">Notes</label>
          <textarea id="notes" rows={2} value={form.notes} onChange={(e) => update('notes', e.target.value)} />

          {error && <p className="error-text">{error}</p>}

          <button type="submit">Save device</button>
        </form>
      )}

      <div className="card">
        <table>
          <thead>
            <tr>
              <th>Device ID</th>
              <th>Type</th>
              <th>Site</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={4}>Loading…</td></tr>}
            {!loading && devices.length === 0 && (
              <tr><td colSpan={4} style={{ color: 'var(--color-ink-500)' }}>No devices registered yet.</td></tr>
            )}
            {devices.map((d) => (
              <tr key={d.id}>
                <td>{d.device_code}</td>
                <td>{d.device_type.replace('_', ' ')}</td>
                <td>{siteName(d.monitoring_site_id)}</td>
                <td><span className="badge">{d.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
