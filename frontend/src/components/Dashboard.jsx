import React, { useState } from 'react';
import FormattedText from './FormattedText';

export default function Dashboard({ result }) {
  const [activeTab, setActiveTab] = useState('summary');

  if (!result) return null;

  const handleDownloadTranscript = () => {
    const element = document.createElement("a");
    const file = new Blob([result.transcript], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = "meeting_transcript.txt";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="col-dash">
      {/* Session Title Card */}
      <div className="glass-card" style={{ borderLeft: '4px solid var(--accent-purple)' }}>
        <div className="card-title">📌 Session Title</div>
        <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
          {result.title}
        </div>
      </div>

      {/* Tabs Navigation Header */}
      <div className="tabs-header">
        <button
          className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          📋 Executive Summary
        </button>
        <button
          className={`tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveTab('insights')}
        >
          💡 Action & Decisions
        </button>
        <button
          className={`tab-btn ${activeTab === 'transcript' ? 'active' : ''}`}
          onClick={() => setActiveTab('transcript')}
        >
          📝 Full Transcript
        </button>
      </div>

      {/* Tab Content Panels */}
      <div className="tab-content">
        {activeTab === 'summary' && (
          <div className="glass-card" style={{ minHeight: '360px' }}>
            <div className="card-title">📋 Meeting Summary</div>
            <div className="card-body">
              <FormattedText content={result.summary} />
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="glass-card" style={{ borderTop: '3px solid var(--accent-emerald)' }}>
                <div className="card-title" style={{ color: 'var(--accent-emerald)' }}>✅ Action Items</div>
                <div className="card-body">
                  <FormattedText content={result.action_items} />
                </div>
              </div>
              <div className="glass-card" style={{ borderTop: '3px solid var(--accent-cyan)' }}>
                <div className="card-title" style={{ color: 'var(--accent-cyan)' }}>🔑 Key Decisions</div>
                <div className="card-body">
                  <FormattedText content={result.key_decisions} />
                </div>
              </div>
            </div>

            <div className="glass-card" style={{ borderTop: '3px solid var(--accent-amber)' }}>
              <div className="card-title" style={{ color: 'var(--accent-amber)' }}>❓ Open Questions & Follow-ups</div>
              <div className="card-body">
                <FormattedText content={result.open_questions} />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'transcript' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div className="transcript-box">{result.transcript}</div>
            <button
              onClick={handleDownloadTranscript}
              className="btn-primary"
              style={{ background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--panel-border)', textTransform: 'none' }}
            >
              📥 Download Transcript (.txt)
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
