import React from 'react';
import { Menu } from 'lucide-react';

export default function Header({ isProcessing, isSidebarCollapsed, onToggleSidebar }) {
  return (
    <div className="top-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}>
        <button
          type="button"
          className="icon-btn"
          onClick={onToggleSidebar}
          title="Toggle Controls Panel"
          style={{ padding: '0.4rem 0.6rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
        >
          <Menu size={18} />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, fontFamily: 'Syne, sans-serif' }}>Controls</span>
        </button>
        <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.1rem', color: '#ffffff', whiteSpace: 'nowrap' }}>
          VidChat
        </span>
        <span className="header-subtitle" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
          | AI Video Assistant
        </span>
      </div>
      <div style={{ flexShrink: 0 }}>
        <span className="badge-tag">
          {isProcessing ? '⚡ Analyzing...' : '🧠 RAG Active'}
        </span>
      </div>
    </div>
  );
}
