import React from 'react';
import { PanelLeftOpen } from 'lucide-react';

export default function Header({ isProcessing, isSidebarCollapsed, onToggleSidebar }) {
  return (
    <div className="top-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: 0 }}>
        {isSidebarCollapsed && (
          <button
            type="button"
            className="icon-btn desktop-only"
            onClick={onToggleSidebar}
            title="Expand Sidebar"
            style={{ padding: '0.4rem', marginRight: '0.25rem' }}
          >
            <PanelLeftOpen size={18} />
          </button>
        )}
        <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.2rem', color: '#ffffff', whiteSpace: 'nowrap' }}>
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
