import { useState } from 'react';
import { assessHabitat } from '../api/intelligence';

export default function HabitatAssessment() {
  const [form, setForm] = useState({
    survey_id: '', habitat_type: 'forest',
    vegetation_cover_pct: 60, water_availability_score: 7,
    food_availability_score: 7, human_disturbance_score: 3,
    fragmentation_index: 0.1, assessment_date: new Date().toISOString().split('T')[0],
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAssess = async () => {
    setLoading(true);
    setResult(null);
    try {
      const payload = { ...form, survey_id: form.survey_id, assessment_date: form.assessment_date };
      const res = await assessHabitat(payload);
      setResult(res.data);
    } catch (err) {
      setResult({ error: 'Assessment failed' });
    } finally {
      setLoading(false);
    }
  };

  const update = (key, val) => setForm({ ...form, [key]: val });

  return (
    <div style={{ padding: '1.5rem' }}>
      <h1>🌍 Habitat Assessment</h1>

      <div style={cardStyle}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div><label>Survey ID</label><input value={form.survey_id} onChange={(e) => update('survey_id', e.target.value)} style={inputStyle} /></div>
          <div><label>Habitat Type</label>
            <select value={form.habitat_type} onChange={(e) => update('habitat_type', e.target.value)} style={inputStyle}>
              {['forest','grassland','wetland','desert','coastal','marine','mountain','savanna','tundra'].map((h) => <option key={h} value={h}>{h}</option>)}
            </select>
          </div>
          <div><label>Vegetation Cover (%)</label><input type="number" min="0" max="100" value={form.vegetation_cover_pct} onChange={(e) => update('vegetation_cover_pct', parseFloat(e.target.value))} style={inputStyle} /></div>
          <div><label>Water Availability (0-10)</label><input type="number" min="0" max="10" value={form.water_availability_score} onChange={(e) => update('water_availability_score', parseFloat(e.target.value))} style={inputStyle} /></div>
          <div><label>Food Availability (0-10)</label><input type="number" min="0" max="10" value={form.food_availability_score} onChange={(e) => update('food_availability_score', parseFloat(e.target.value))} style={inputStyle} /></div>
          <div><label>Human Disturbance (0-10)</label><input type="number" min="0" max="10" value={form.human_disturbance_score} onChange={(e) => update('human_disturbance_score', parseFloat(e.target.value))} style={inputStyle} /></div>
          <div><label>Fragmentation Index (0-1)</label><input type="number" min="0" max="1" step="0.01" value={form.fragmentation_index} onChange={(e) => update('fragmentation_index', parseFloat(e.target.value))} style={inputStyle} /></div>
          <div><label>Assessment Date</label><input type="date" value={form.assessment_date} onChange={(e) => update('assessment_date', e.target.value)} style={inputStyle} /></div>
        </div>
        <button onClick={handleAssess} disabled={loading} style={btnStyle}>{loading ? 'Assessing...' : 'Assess Habitat'}</button>
      </div>

      {result && !result.error && (
        <div style={{ marginTop: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
          {/* Quality */}
          <div style={cardStyle}>
            <h3>Quality</h3>
            <p><strong>Score:</strong> {result.quality?.overall_quality_score}/10</p>
            <p><strong>Rating:</strong> {result.quality?.quality_rating}</p>
            <p><strong>Suitability:</strong> {result.quality?.suitability_score}/10</p>
          </div>
          {/* Degradation */}
          <div style={cardStyle}>
            <h3>Degradation</h3>
            <p><strong>Score:</strong> {result.degradation?.degradation_score}/10</p>
            <p><strong>Level:</strong> {result.degradation?.degradation_level?.replace(/_/g, ' ')}</p>
            <p><strong>Needs Restoration:</strong> {result.degradation?.requires_restoration ? '🔴 Yes' : '✅ No'}</p>
          </div>
          {/* Classification */}
          <div style={cardStyle}>
            <h3>Classification</h3>
            <p><strong>Type:</strong> {result.classification?.classified_habitat?.replace(/_/g, ' ')}</p>
            <p><strong>Confidence:</strong> {result.classification?.confidence}</p>
          </div>
        </div>
      )}
      {result?.error && <p style={{ color: 'red' }}>{result.error}</p>}
    </div>
  );
}

const btnStyle = { marginTop: '1rem', padding: '0.5rem 1rem', background: '#2563eb', color: 'white', border: 'none', borderRadius: '0.375rem', cursor: 'pointer' };
const cardStyle = { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1rem' };
const inputStyle = { width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem', marginTop: '0.25rem' };