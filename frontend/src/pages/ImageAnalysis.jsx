import { useState } from 'react';
import { analyzeImage, batchAnalyzeImages } from '../api/intelligence';

export default function ImageAnalysis() {
  const [file, setFile] = useState(null);
  const [batchFiles, setBatchFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [batchResults, setBatchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('single');

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await analyzeImage(formData);
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || 'Analysis failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleBatchAnalyze = async () => {
    if (batchFiles.length === 0) return;
    setLoading(true);
    setBatchResults(null);
    try {
      const formData = new FormData();
      batchFiles.forEach((f) => formData.append('files', f));
      const res = await batchAnalyzeImages(formData);
      setBatchResults(res.data);
    } catch (err) {
      setBatchResults({ error: 'Batch analysis failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1>📷 Image Analysis</h1>
      <p>Upload camera trap or drone images for AI-powered wildlife detection</p>

      {/* Mode Toggle */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <button onClick={() => setMode('single')} style={mode === 'single' ? activeBtn : inactiveBtn}>Single Image</button>
        <button onClick={() => setMode('batch')} style={mode === 'batch' ? activeBtn : inactiveBtn}>Batch Upload</button>
      </div>

      {mode === 'single' ? (
        <div>
          <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
          <button onClick={handleAnalyze} disabled={!file || loading} style={btnStyle}>
            {loading ? 'Analyzing...' : 'Analyze Image'}
          </button>

          {result && !result.error && (
            <div style={{ marginTop: '1.5rem' }}>
              <h3>Results</h3>
              <div style={cardStyle}>
                <p><strong>Image Quality:</strong> {result.image_quality}</p>
                <p><strong>Total Animals:</strong> {result.total_animals}</p>
                <p><strong>Detections:</strong> {result.num_detections}</p>
                {result.endangered_species_found?.length > 0 && (
                  <p style={{ color: '#dc2626' }}><strong>⚠️ Endangered:</strong> {result.endangered_species_found.join(', ')}</p>
                )}
              </div>
              {Object.entries(result.species_counts || {}).map(([species, count]) => (
                <div key={species} style={{ ...cardStyle, marginTop: '0.5rem' }}>
                  <strong>{species}</strong>: {count} detected
                </div>
              ))}
              {result.behaviors_detected?.length > 0 && (
                <div style={{ marginTop: '0.5rem' }}>
                  <strong>Behaviors:</strong> {result.behaviors_detected.join(', ')}
                </div>
              )}
            </div>
          )}
          {result?.error && <p style={{ color: 'red' }}>{result.error}</p>}
        </div>
      ) : (
        <div>
          <input type="file" accept="image/*" multiple onChange={(e) => setBatchFiles(Array.from(e.target.files))} />
          <button onClick={handleBatchAnalyze} disabled={batchFiles.length === 0 || loading} style={btnStyle}>
            {loading ? 'Analyzing...' : `Analyze ${batchFiles.length} Images`}
          </button>
          {batchResults && (
            <div style={{ marginTop: '1rem' }}>
              <p>Processed: {batchResults.total_processed}</p>
              {batchResults.results?.map((r, i) => (
                <div key={i} style={{ ...cardStyle, marginTop: '0.5rem' }}>
                  <strong>{r.filename}</strong>: {r.status === 'success' ? `${r.total_animals} animals` : r.error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const btnStyle = { marginTop: '0.5rem', padding: '0.5rem 1rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' };
const activeBtn = { ...btnStyle, background: '#2563eb' };
const inactiveBtn = { ...btnStyle, background: '#9ca3af' };
const cardStyle = { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' };