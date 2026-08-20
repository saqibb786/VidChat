import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import ChatBox from './components/ChatBox';

const API_BASE_URL = 'http://localhost:8000/api';

export default function App() {
  const [source, setSource] = useState('');
  const [language, setLanguage] = useState('english');
  const [engine, setEngine] = useState('local');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true);
  const [steps, setSteps] = useState({});
  const [result, setResult] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [errorMsg, setErrorMsg] = useState('');
  const [warningMsg, setWarningMsg] = useState('');

  const toggleSidebar = () => {
    setIsSidebarCollapsed((prev) => !prev);
  };

  const handleAnalyze = async (e) => {
    e?.preventDefault();
    if (!source.trim() || isProcessing) return;

    // Automatically collapse sidebar on mobile when processing starts
    setIsSidebarCollapsed(true);
    setIsProcessing(true);
    setErrorMsg('');
    setWarningMsg('');
    setResult(null);
    setChatHistory([]);
    setSteps({
      audio: 'active',
      transcript: 'pending',
      title: 'pending',
      extract: 'pending',
      rag: 'pending',
    });

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: source.trim(), language, engine }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setSteps({
        audio: 'done',
        transcript: 'done',
        title: 'done',
        extract: 'done',
        rag: 'done',
      });
      setResult(data);

      if (data.fallback_warning) {
        setWarningMsg(data.fallback_warning);
      }
    } catch (err) {
      setErrorMsg(err.message);
      setSteps({
        audio: 'pending',
        transcript: 'pending',
        title: 'pending',
        extract: 'pending',
        rag: 'pending',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSendMessage = async (questionText) => {
    if (!result?.session_id || !questionText || isAsking) return;

    setIsAsking(true);
    const userMessage = { role: 'user', content: questionText };
    setChatHistory((prev) => [...prev, userMessage]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: result.session_id,
          question: questionText,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to get answer');
      }

      const data = await response.json();
      const botMessage = { role: 'assistant', content: data.answer };
      setChatHistory((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorMessage = { role: 'assistant', content: `❌ Error: ${err.message}` };
      setChatHistory((prev) => [...prev, errorMessage]);
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div className="app-container">
      {/* Mobile Drawer Overlay Backdrop */}
      {!isSidebarCollapsed && (
        <div className="mobile-overlay" onClick={toggleSidebar} />
      )}

      {/* Left Sidebar Control Panel */}
      <Sidebar
        source={source}
        setSource={setSource}
        language={language}
        setLanguage={setLanguage}
        engine={engine}
        setEngine={setEngine}
        onAnalyze={handleAnalyze}
        isProcessing={isProcessing}
        steps={steps}
        isCollapsed={isSidebarCollapsed}
        onToggleSidebar={toggleSidebar}
      />

      {/* Main Workspace Area */}
      <div className="content-area">
        <Header
          isProcessing={isProcessing}
          isSidebarCollapsed={isSidebarCollapsed}
          onToggleSidebar={toggleSidebar}
        />

        {warningMsg && (
          <div className="glass-card" style={{ borderLeft: '4px solid #f59e0b', color: '#fbbf24', marginBottom: '0.75rem' }}>
            ⚠️ {warningMsg}
          </div>
        )}

        {errorMsg && (
          <div className="glass-card" style={{ borderLeft: '4px solid #ef4444', color: '#f87171', marginBottom: '0.75rem' }}>
            ⚠️ {errorMsg}
          </div>
        )}

        {result ? (
          <div className="workspace-grid">
            <Dashboard result={result} />
            <ChatBox
              chatHistory={chatHistory}
              onSendMessage={handleSendMessage}
              isAsking={isAsking}
              sessionId={result.session_id}
            />
          </div>
        ) : (
          <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '2rem 1.5rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>🎬</div>
            <div style={{ fontFamily: 'Syne, sans-serif', fontSize: '1.5rem', fontWeight: 800, color: '#fff', marginBottom: '0.5rem' }}>
              Welcome to VidChat
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', maxWidth: '480px', margin: '0 auto 1.5rem auto', lineHeight: '1.6' }}>
              Select your Ingestion Engine (Local or Adversal Cloud) and enter a YouTube URL or local file path to generate summaries and chat with your video.
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
              <span className="badge-tag">⚡ Dual Engine</span>
              <span className="badge-tag">📋 Map-Reduce</span>
              <span className="badge-tag">💬 Real-time RAG</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
