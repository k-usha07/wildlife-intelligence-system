import { useState } from 'react';
import { analyzeBiodiversity } from '../api/intelligence';

export default function BiodiversityDashboard() {
  const [surveyId, setSurveyId] = useState('');
  const [areaKm2, setAreaKm2] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!surveyId) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await analyzeBiodiversity(surveyId, areaKm2 ? parseFloat(areaKm2) : undefined);
      setResult(res.data);
    } catch (err) {
      setResult({ error: 'Biodiversity analysis failed' });
    } finally {
      setLoading(false);
    }
  };

  const ratingColors = { exceptional: '#22c55e', high: '#3b82f6', moderate: '#f59e0b', low: '#ea580c', very_low: '#dc2626' };

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1>🌿 Biodiversity Dashboard</h1>
      <p>Calculate biodiversity indices from survey observations</p>

      <div style={cardStyle}>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div>
            <label>Survey ID</label>
            <input type="text" value={surveyId} onChange={(e) => setSurveyId(e.target.value)} style={inputStyle} placeholder="Enter survey UUID" />
          </div>
          <div>
            <label>Area (km²)</label>
            <input type="number" value={areaKm2} onChange={(e) => setAreaKm2(e.target.value)} style={inputStyle} placeholder="Optional" />
          </div>
          <button onClick={handleAnalyze} disabled={loading} style={btnStyle}>
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>

      {result && !result.error && (
        <div style={{ marginTop: '1.5rem' }}>
          {/* Score Cards */}
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            <ScoreCard label="Shannon Index" value={result.shannon_index} />
            <ScoreCard label="Simpson Index" value={result.simpson_index} />
            <ScoreCard label="Richness" value={result.species_richness} />
            <ScoreCard label="Evenness" value={result.evenness_index} />
          </div>

          {/* Rating */}
          <div style={{ ...cardStyle, textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: ratingColors[result.biodiversity_rating] || '#6b7280' }}>
              {result.biodiversity_rating?.replace('_', ' ').toUpperCase()}
            </div>
            <div>Biodiversity Rating</div>
          </div>

          {/* Species Abundance */}
          {result.species_abundance && (
            <div style={{ marginTop: '1rem' }}>
              <h3>Species Abundance</h3>
              {Object.entries(result.species_abundance).slice(0, 15).map(([species, info]) => (
                <div key={species} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                  <span style={{ width: '150px', fontSize: '0.85rem' }}>{species}</span>
                  <div style={{ height: '1rem', background: '#3b82f6', borderRadius: '0.25rem', width: `${info.proportion * 100}%`, minWidth: '4px' }} />
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>{info.count} ({(info.proportion * 100).toFixed(1)}%)</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      {result?.error && <p style={{ color: 'red' }}>{result.error}</p>}
    </div>
  );
}

function ScoreCard({ label, value }) {
  return (
    <div style={{ background: 'white', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem', textAlign: 'center', minWidth: '120px' }}>
      <div style={{ fontSize: '1.8rem', fontWeight: 'bold' }}>{typeof value === 'number' ? value.toFixed(4) : value}</div>
      <div style={{ color: '#6b7280', fontSize: '0.85rem' }}>{label}</div>
    </div>
  );
}

const btnStyle = { padding: '0.5rem 1rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' };
const cardStyle = { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' };
const inputStyle = { width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', marginTop: '0.25rem' };