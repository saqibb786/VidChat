import React from 'react';
import { PanelLeftOpen } from 'lucide-react';

export default function Header({ isProcessing, isSidebarCollapsed, onToggleSidebar }) {
  return (
    <div className="top-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {isSidebarCollapsed && (
          <button
            type="button"
            className="icon-btn"
            onClick={onToggleSidebar}
            title="Expand Sidebar"
            style={{ marginRight: '0.25rem' }}
          >
            <PanelLeftOpen size={18} />
          </button>
        )}
        <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '1.2rem', color: '#ffffff' }}>
          VidChat
        </span>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          | Intelligent Video Assistant
        </span>
      </div>
      <div>
        <span className="badge-tag">
          {isProcessing ? '⚡ Analyzing Media...' : '🧠 RAG Engine Active'}
        </span>
      </div>
    </div>
  );
}
