import React, { useState, useRef } from 'react';
import { PanelLeftClose, UploadCloud, FileVideo, CheckCircle2 } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

export default function Sidebar({
  source,
  setSource,
  language,
  setLanguage,
  engine,
  setEngine,
  onAnalyze,
  isProcessing,
  steps,
  isCollapsed,
  onToggleSidebar
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const fileInputRef = useRef(null);

  const stepItems = [
    { key: 'audio', label: '🔊 Media Ingestion' },
    { key: 'transcript', label: '📝 Speech / AI Extraction' },
    { key: 'title', label: '🏷️ Title & Summary' },
    { key: 'extract', label: '🔍 Insight Extraction' },
    { key: 'rag', label: '🧠 Vector RAG Engine' },
  ];

  const handleFileUpload = async (file) => {
    if (!file) return;
    setIsUploading(true);
    setUploadedFileName(file.name);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('File upload failed');
      }

      const data = await response.json();
      setSource(data.filepath);
    } catch (err) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (isProcessing || isUploading) return;
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!isDragging) setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div className="brand-title">🎬 VidChat</div>
          <div className="brand-subtitle">AI Video & Audio Assistant</div>
        </div>
        <button
          type="button"
          className="icon-btn"
          onClick={onToggleSidebar}
          title="Collapse Sidebar"
        >
          <PanelLeftClose size={18} />
        </button>
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
            disabled={isProcessing || isUploading}
          />
        </div>

        {/* Drag and Drop Local Video Upload Zone */}
        <div className="form-group">
          <label className="form-label">Upload Local Video / Audio</label>
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
              border: `2px dashed ${isDragging ? 'var(--accent-purple)' : 'var(--panel-border)'}`,
              borderRadius: '10px',
              padding: '1rem 0.75rem',
              textAlign: 'center',
              background: isDragging ? 'rgba(139, 92, 246, 0.12)' : 'rgba(255, 255, 255, 0.02)',
              cursor: isProcessing || isUploading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*,audio/*"
              style={{ display: 'none' }}
              onChange={handleFileSelect}
              disabled={isProcessing || isUploading}
            />
            {isUploading ? (
              <div style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)' }}>
                ⚡ Uploading {uploadedFileName}...
              </div>
            ) : source && uploadedFileName ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem', fontSize: '0.82rem', color: 'var(--accent-emerald)' }}>
                <CheckCircle2 size={16} />
                <span>{uploadedFileName}</span>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.35rem' }}>
                <UploadCloud size={24} style={{ color: 'var(--accent-purple)' }} />
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  Drag & drop video file here
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  or click to browse (.mp4, .mov, .mp3, .wav)
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Ingestion Engine</label>
          <select
            className="form-select"
            value={engine}
            onChange={(e) => setEngine(e.target.value)}
            disabled={isProcessing || isUploading}
          >
            <option value="local">Local Pipeline (Whisper / Sarvam)</option>
            <option value="adversal">Adversal.ai Cloud (Remote MCP)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Language Mode</label>
          <select
            className="form-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={isProcessing || isUploading}
          >
            <option value="english">English (OpenAI Whisper)</option>
            <option value="hinglish">Hinglish (Sarvam AI STT)</option>
          </select>
        </div>

        <button type="submit" className="btn-primary" disabled={isProcessing || isUploading || !source.trim()}>
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
