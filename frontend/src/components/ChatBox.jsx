import React, { useState, useRef, useEffect } from 'react';
import FormattedText from './FormattedText';

export default function ChatBox({ chatHistory, onSendMessage, isAsking, sessionId }) {
  const [inputQuery, setInputQuery] = useState('');
  const chatEndRef = useRef(null);

  // Auto scroll chat to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isAsking]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || isAsking || !sessionId) return;
    onSendMessage(inputQuery.trim());
    setInputQuery('');
  };

  return (
    <div className="col-chat">
      <div className="chat-card">
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem', color: '#ffffff' }}>
            💬 Chat with Video
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--accent-cyan)', fontFamily: 'JetBrains Mono, monospace' }}>
            RAG Active
          </span>
        </div>

        {/* Chat History Messages */}
        <div className="chat-history">
          {chatHistory.length === 0 ? (
            <div style={{ margin: 'auto', textAlign: 'center', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '2.5rem' }}>💬</div>
              <div style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
                {sessionId ? 'Ask any question about your video transcript.' : 'Analyze a media file to start chatting.'}
              </div>
            </div>
          ) : (
            chatHistory.map((msg, index) => (
              <div
                key={index}
                className={msg.role === 'user' ? 'chat-msg-user' : 'chat-msg-bot'}
              >
                <b>{msg.role === 'user' ? 'You:' : '🤖 Assistant:'}</b>
                {msg.role === 'user' ? (
                  <span> {msg.content}</span>
                ) : (
                  <FormattedText content={msg.content} />
                )}
              </div>
            ))
          )}
          {isAsking && (
            <div className="chat-msg-bot" style={{ opacity: 0.8 }}>
              🤖 Assistant is thinking...
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="chat-input-row">
          <input
            type="text"
            className="form-input"
            style={{ flex: 1, minWidth: 0 }}
            placeholder={sessionId ? "Ask about key concepts, specific timestamps, or details..." : "Analyze media to unlock chat..."}
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={isAsking || !sessionId}
          />
          <button
            type="submit"
            className="btn-primary"
            style={{ padding: '0.65rem 1.25rem', width: 'auto', flexShrink: 0, whiteSpace: 'nowrap' }}
            disabled={isAsking || !inputQuery.trim() || !sessionId}
          >
            Send →
          </button>
        </form>
      </div>
    </div>
  );
}
