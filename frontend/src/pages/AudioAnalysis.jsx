import { useState } from 'react';
import { analyzeAudio } from '../api/intelligence';

export default function AudioAnalysis() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await analyzeAudio(formData);
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || 'Analysis failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1>🔊 Audio Analysis</h1>
      <p>Upload wildlife audio recordings for bioacoustic species identification</p>

      <input type="file" accept="audio/*" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleAnalyze} disabled={!file || loading} style={btnStyle}>
        {loading ? 'Analyzing...' : 'Analyze Audio'}
      </button>

      {result && !result.error && (
        <div style={{ marginTop: '1.5rem' }}>
          <div style={cardStyle}>
            <p><strong>Duration:</strong> {result.duration_seconds?.toFixed(1)}s</p>
            <p><strong>Total Calls:</strong> {result.total_calls_detected}</p>
            <p><strong>Noise Level:</strong> {result.noise_level?.toFixed(6)}</p>
          </div>

          <h3 style={{ marginTop: '1rem' }}>Species Identified</h3>
          {(result.species_identified || []).map((s, i) => (
            <div key={i} style={{ ...cardStyle, marginTop: '0.5rem' }}>
              <strong>{s.species}</strong> — Confidence: {(s.confidence * 100).toFixed(1)}% — Type: {s.call_type}
            </div>
          ))}

          {Object.entries(result.acoustic_events || {}).length > 0 && (
            <div style={{ marginTop: '1rem' }}>
              <h3>Acoustic Events</h3>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {Object.entries(result.acoustic_events).map(([type, count]) => (
                  <span key={type} style={{ padding: '0.3rem 0.8rem', background: '#eff6ff', borderRadius: '9999px', fontSize: '0.8rem' }}>
                    {type}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
      {result?.error && <p style={{ color: 'red' }}>{result.error}</p>}
    </div>
  );
}

const btnStyle = { marginTop: '0.5rem', padding: '0.5rem 1rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' };
const cardStyle = { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' };