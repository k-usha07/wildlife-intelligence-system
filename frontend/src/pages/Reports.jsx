import { useState } from 'react';
import { getSurveyPdf, getSurveyExcel, getBiodiversityReport } from '../api/intelligence';

export default function Reports() {
  const [surveyId, setSurveyId] = useState('');
  const [biodiversity, setBiodiversity] = useState(null);
  const [loading, setLoading] = useState(false);

  const downloadFile = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePdf = async () => {
    if (!surveyId) return;
    setLoading(true);
    try {
      const res = await getSurveyPdf(surveyId);
      downloadFile(res.data, `survey_${surveyId}_report.pdf`);
    } catch (err) {
      alert('Failed to generate PDF');
    } finally {
      setLoading(false);
    }
  };

  const handleExcel = async () => {
    if (!surveyId) return;
    setLoading(true);
    try {
      const res = await getSurveyExcel(surveyId);
      downloadFile(res.data, `survey_${surveyId}_report.xlsx`);
    } catch (err) {
      alert('Failed to generate Excel');
    } finally {
      setLoading(false);
    }
  };

  const handleBiodiversity = async () => {
    if (!surveyId) return;
    setLoading(true);
    try {
      const res = await getBiodiversityReport(surveyId);
      setBiodiversity(res.data);
    } catch (err) {
      setBiodiversity({ error: 'Failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1>📋 Reports & Export</h1>

      <div style={cardStyle}>
        <label>Survey ID</label>
        <input type="text" value={surveyId} onChange={(e) => setSurveyId(e.target.value)} style={inputStyle} placeholder="Enter survey UUID" />

        <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
          <button onClick={handlePdf} disabled={!surveyId || loading} style={btnStyle}>📥 Export PDF</button>
          <button onClick={handleExcel} disabled={!surveyId || loading} style={{ ...btnStyle, background: '#22c55e' }}>📥 Export Excel</button>
          <button onClick={handleBiodiversity} disabled={!surveyId || loading} style={{ ...btnStyle, background: '#8b5cf6' }}>🌿 Biodiversity Report</button>
        </div>
      </div>

      {biodiversity && !biodiversity.error && (
        <div style={{ marginTop: '1rem' }}>
          <h3>Biodiversity Report</h3>
          {biodiversity.biodiversity_records?.map((b, i) => (
            <div key={i} style={{ ...cardStyle, marginTop: '0.5rem' }}>
              <p><strong>Shannon:</strong> {b.shannon_index?.toFixed(4)} | <strong>Simpson:</strong> {b.simpson_index?.toFixed(4)} | <strong>Richness:</strong> {b.species_richness} | <strong>Evenness:</strong> {b.evenness?.toFixed(4)}</p>
              <p style={{ fontSize: '0.8rem', color: '#6b7280' }}>Date: {b.date}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const btnStyle = { padding: '0.5rem 1rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' };
const cardStyle = { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' };
const inputStyle = { width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', marginTop: '0.25rem' };