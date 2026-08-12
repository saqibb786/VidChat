import React from 'react';

export default function Sidebar({ source, setSource, language, setLanguage, onAnalyze, isProcessing, steps }) {
  const stepItems = [
    { key: 'audio', label: '🔊 Audio Processing' },
    { key: 'transcript', label: '📝 Transcription' },
    { key: 'title', label: '🏷️ Title & Summary' },
    { key: 'extract', label: '🔍 Insight Extraction' },
    { key: 'rag', label: '🧠 Vector RAG Engine' },
  ];

  return (
    <div className="sidebar">
      <div>
        <div className="brand-title">🎬 VidChat</div>
        <div className="brand-subtitle">Meeting Intelligence</div>
      </div>

      <hr style={{ borderColor: 'var(--panel-border)', borderStyle: 'solid' }} />

      <form onSubmit={onAnalyze} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div className="form-group">
          <label className="form-label">Media Source</label>
          <input
            type="text"
            className="form-input"
            placeholder="YouTube URL or local file path..."
            value={source}
            onChange={(e) => setSource(e.target.value)}
            disabled={isProcessing}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Language Mode</label>
          <select
            className="form-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={isProcessing}
          >
            <option value="english">English (OpenAI Whisper)</option>
            <option value="hinglish">Hinglish (Sarvam AI STT)</option>
          </select>
        </div>

        <button type="submit" className="btn-primary" disabled={isProcessing || !source.trim()}>
          {isProcessing ? '⚡ Processing...' : '⚡ Start Analysis'}
        </button>
      </form>

      {Object.keys(steps).length > 0 && (
        <div style={{ marginTop: '0.5rem' }}>
          <div className="form-label" style={{ marginBottom: '0.5rem' }}>Pipeline Progress</div>
          <div className="status-list">
            {stepItems.map((step) => {
              const status = steps[step.key] || 'pending';
              const dotClass = status === 'done' ? 'dot-done' : status === 'active' ? 'dot-active' : 'dot-pending';
              return (
                <div key={step.key} className="status-item">
                  <span className={`dot ${dotClass}`} />
                  <span>{step.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
