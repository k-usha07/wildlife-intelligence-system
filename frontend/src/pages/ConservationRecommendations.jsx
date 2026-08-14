import { useState } from 'react';
import { getConservationRecommendations } from '../api/intelligence';

export default function ConservationRecommendations() {
  const [surveyId, setSurveyId] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!surveyId) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await getConservationRecommendations(surveyId);
      setResult(res.data);
    } catch (err) {
      setResult({ error: 'Failed to generate recommendations' });
    } finally {
      setLoading(false);
    }
  };

  const priorityColors = { critical: '#dc2626', high: '#ea580c', medium: '#f59e0b', low: '#22c55e' };

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1>🛡️ Conservation Recommendations</h1>

      <div style={cardStyle}>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div>
            <label>Survey ID</label>
            <input type="text" value={surveyId} onChange={(e) => setSurveyId(e.target.value)} style={inputStyle} placeholder="Enter survey UUID" />
          </div>
          <button onClick={handleGenerate} disabled={loading} style={btnStyle}>
            {loading ? 'Generating...' : 'Generate Recommendations'}
          </button>
        </div>
      </div>

      {result && !result.error && (
        <div style={{ marginTop: '1.5rem' }}>
          {/* Summary */}
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
            <div style={cardStyle}><strong style={{ color: '#dc2626' }}>{result.critical_count}</strong> Critical</div>
            <div style={cardStyle}><strong style={{ color: '#ea580c' }}>{result.high_count}</strong> High</div>
            <div style={cardStyle}><strong style={{ color: '#f59e0b' }}>{result.medium_count}</strong> Medium</div>
          </div>

          {result.summary && <p style={{ fontStyle: 'italic', color: '#6b7280' }}>{result.summary}</p>}

          {/* Recommendations */}
          {(result.recommendations || []).map((rec, i) => (
            <div key={i} style={{ ...cardStyle, marginTop: '0.75rem', borderLeft: `4px solid ${priorityColors[rec.priority] || '#6b7280'}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h4 style={{ margin: 0 }}>{rec.title}</h4>
                <span style={{ padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', background: priorityColors[rec.priority] || '#6b7280', color: 'white', fontWeight: 'bold' }}>
                  {rec.priority}
                </span>
              </div>
              <p style={{ marginTop: '0.5rem' }}>{rec.description}</p>
              {rec.actions && (
                <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem' }}>
                  {rec.actions.map((a, j) => <li key={j} style={{ fontSize: '0.85rem' }}>{a}</li>)}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}
      {result?.error && <p style={{ color: 'red' }}>{result.error}</p>}
    </div>
  );
}

const btnStyle = { padding: '0.5rem 1rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' };
const cardStyle = { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' };
const inputStyle = { width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', marginTop: '0.25rem' };