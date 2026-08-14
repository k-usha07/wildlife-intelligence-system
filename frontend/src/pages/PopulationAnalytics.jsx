import { useState } from 'react';
import { estimatePopulationMarkRecapture, analyzePopulationTrends, analyzeMigration } from '../api/intelligence';

export default function PopulationAnalytics() {
  const [method, setMethod] = useState('mark-recapture');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Mark-Recapture state
  const [mr, setMr] = useState({ marked: '', captured: '', recaptured: '' });

  // Trend state
  const [trendData, setTrendData] = useState([
    { year: 2019, population: 100 },
    { year: 2020, population: 115 },
    { year: 2021, population: 130 },
    { year: 2022, population: 125 },
    { year: 2023, population: 140 },
  ]);

  const handleMarkRecapture = async () => {
    setLoading(true);
    try {
      const res = await estimatePopulationMarkRecapture(
        parseInt(mr.marked), parseInt(mr.captured), parseInt(mr.recaptured)
      );
      setResult(res.data);
    } catch (err) {
      setResult({ error: 'Estimation failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleTrendAnalysis = async () => {
    setLoading(true);
    try {
      const res = await analyzePopulationTrends(trendData);
      setResult(res.data);
    } catch (err) {
      setResult({ error: 'Trend analysis failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1>📊 Population Analytics</h1>

      {/* Method Selector */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        {['mark-recapture', 'trends'].map((m) => (
          <button key={m} onClick={() => { setMethod(m); setResult(null); }}
            style={method === m ? activeBtn : inactiveBtn}>
            {m === 'mark-recapture' ? 'Mark-Recapture' : 'Trend Analysis'}
          </button>
        ))}
      </div>

      {method === 'mark-recapture' && (
        <div style={cardStyle}>
          <h3>Lincoln-Petersen Mark-Recapture</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
            <div>
              <label>Marked (1st capture)</label>
              <input type="number" value={mr.marked} onChange={(e) => setMr({ ...mr, marked: e.target.value })} style={inputStyle} />
            </div>
            <div>
              <label>Captured (2nd)</label>
              <input type="number" value={mr.captured} onChange={(e) => setMr({ ...mr, captured: e.target.value })} style={inputStyle} />
            </div>
            <div>
              <label>Recaptured</label>
              <input type="number" value={mr.recaptured} onChange={(e) => setMr({ ...mr, recaptured: e.target.value })} style={inputStyle} />
            </div>
          </div>
          <button onClick={handleMarkRecapture} disabled={loading} style={btnStyle}>
            {loading ? 'Calculating...' : 'Estimate Population'}
          </button>
        </div>
      )}

      {method === 'trends' && (
        <div style={cardStyle}>
          <h3>Population Trend Analysis</h3>
          <p>Edit population data below:</p>
          {trendData.map((d, i) => (
            <div key={i} style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
              <input type="number" value={d.year} onChange={(e) => {
                const updated = [...trendData]; updated[i] = { ...updated[i], year: parseInt(e.target.value) }; setTrendData(updated);
              }} style={inputStyle} placeholder="Year" />
              <input type="number" value={d.population} onChange={(e) => {
                const updated = [...trendData]; updated[i] = { ...updated[i], population: parseInt(e.target.value) }; setTrendData(updated);
              }} style={inputStyle} placeholder="Population" />
            </div>
          ))}
          <button onClick={() => setTrendData([...trendData, { year: trendData.length + 2019, population: 0 }])} style={{ ...btnStyle, background: '#6b7280', marginTop: '0.5rem' }}>+ Add Year</button>
          <button onClick={handleTrendAnalysis} disabled={loading} style={btnStyle}>Analyze Trends</button>
        </div>
      )}

      {/* Results */}
      {result && !result.error && (
        <div style={{ ...cardStyle, marginTop: '1rem' }}>
          <h3>Results</h3>
          {method === 'mark-recapture' ? (
            <div>
              <p><strong>Estimated Population:</strong> {result.estimated_population?.toLocaleString()}</p>
              <p><strong>Chapman Estimate:</strong> {result.chapman_estimate?.toLocaleString()}</p>
              <p><strong>Standard Error:</strong> {result.standard_error}</p>
              {result.confidence_interval_95 && (
                <p><strong>95% CI:</strong> [{result.confidence_interval_95.lower?.toLocaleString()} — {result.confidence_interval_95.upper?.toLocaleString()}]</p>
              )}
              <p><strong>Method:</strong> {result.method}</p>
            </div>
          ) : (
            <div>
              <p><strong>Trend:</strong> {result.trend_direction}</p>
              <p><strong>Growth Rate:</strong> {(result.average_growth_rate_pct)?.toFixed(2)}%</p>
              <p><strong>Current:</strong> {result.current_population?.toLocaleString()}</p>
              <p><strong>Peak:</strong> {result.peak_population?.toLocaleString()}</p>
              {result.predictions?.next_3_years && (
                <div style={{ marginTop: '0.5rem' }}>
                  <strong>Predictions:</strong>
                  {result.predictions.next_3_years.map((p) => (
                    <span key={p.year} style={{ marginLeft: '0.5rem' }}>{p.year}: {p.predicted_population?.toLocaleString()}</span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
      {result?.error && <p style={{ color: 'red' }}>{result.error}</p>}
    </div>
  );
}

const btnStyle = { marginTop: '0.5rem', padding: '0.5rem 1rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' };
const activeBtn = { ...btnStyle };
const inactiveBtn = { ...btnStyle, background: '#9ca3af' };
const cardStyle = { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' };
const inputStyle = { width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', marginTop: '0.25rem' };