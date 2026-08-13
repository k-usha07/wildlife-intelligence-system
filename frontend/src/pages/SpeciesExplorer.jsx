import { useState, useEffect } from 'react';
import { getSpecies, getEndangeredSpecies, getSpeciesStats } from '../api/intelligence';

const SPECIES_GROUPS = ['mammals', 'birds', 'reptiles', 'amphibians', 'insects', 'marine_species'];
const STATUS_COLORS = { CR: '#dc2626', EN: '#ea580c', VU: '#f59e0b', NT: '#3b82f6', LC: '#22c55e', DD: '#9ca3af' };

export default function SpeciesExplorer() {
  const [species, setSpecies] = useState([]);
  const [endangered, setEndangered] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState({ group: '', endangeredOnly: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAll();
  }, [filter]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter.group) params.group = filter.group;
      if (filter.endangeredOnly) params.endangered_only = true;
      const [spRes, endRes, statRes] = await Promise.all([
        getSpecies(params),
        getEndangeredSpecies(),
        getSpeciesStats(),
      ]);
      setSpecies(spRes.data);
      setEndangered(endRes.data);
      setStats(statRes.data);
    } catch (err) {
      console.error('Failed to load species:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1>🦁 Species Explorer</h1>

      {/* Stats Cards */}
      {stats && (
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          <div style={cardStyle}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total_species}</div>
            <div style={{ color: '#6b7280' }}>Total Species</div>
          </div>
          <div style={{ ...cardStyle, borderLeft: '4px solid #dc2626' }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#dc2626' }}>{stats.endangered_count}</div>
            <div style={{ color: '#6b7280' }}>Endangered</div>
          </div>
          {Object.entries(stats.by_group || {}).map(([group, count]) => (
            <div key={group} style={cardStyle}>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{count}</div>
              <div style={{ color: '#6b7280', textTransform: 'capitalize' }}>{group}</div>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', alignItems: 'center' }}>
        <select value={filter.group} onChange={(e) => setFilter({ ...filter, group: e.target.value })} style={selectStyle}>
          <option value="">All Groups</option>
          {SPECIES_GROUPS.map((g) => <option key={g} value={g}>{g}</option>)}
        </select>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
          <input type="checkbox" checked={filter.endangeredOnly} onChange={(e) => setFilter({ ...filter, endangeredOnly: e.target.checked })} />
          Endangered Only
        </label>
      </div>

      {/* Species Table */}
      {loading ? <p>Loading...</p> : (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f3f4f6', textAlign: 'left' }}>
              <th style={thStyle}>Common Name</th>
              <th style={thStyle}>Scientific Name</th>
              <th style={thStyle}>Group</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Population</th>
              <th style={thStyle}>Endangered</th>
            </tr>
          </thead>
          <tbody>
            {species.map((s) => (
              <tr key={s.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
                <td style={tdStyle}>{s.common_name}</td>
                <td style={{ ...tdStyle, fontStyle: 'italic' }}>{s.scientific_name}</td>
                <td style={{ ...tdStyle, textTransform: 'capitalize' }}>{s.species_group}</td>
                <td style={tdStyle}>
                  <span style={{
                    padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 'bold',
                    background: STATUS_COLORS[s.conservation_status] || '#9ca3af', color: 'white',
                  }}>
                    {s.conservation_status}
                  </span>
                </td>
                <td style={tdStyle}>{s.population_estimate?.toLocaleString() || '—'}</td>
                <td style={tdStyle}>{s.is_endangered ? '🔴' : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

const cardStyle = { background: 'white', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem', minWidth: '120px' };
const selectStyle = { padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid #d1d5db' };
const thStyle = { padding: '0.75rem', fontSize: '0.875rem' };
const tdStyle = { padding: '0.75rem', fontSize: '0.875rem' };