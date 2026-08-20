import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function FormattedText({ content }) {
  if (!content) return null;

  return (
    <div className="formatted-markdown">
      <ReactMarkdown
        components={{
          a: ({ node, ...props }) => (
            <a
              {...props}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: 'var(--accent-cyan)',
                textDecoration: 'underline',
                fontWeight: 600,
                wordBreak: 'break-word'
              }}
            />
          ),
          img: ({ node, ...props }) => (
            <span style={{ display: 'block', margin: '0.75rem 0', textAlign: 'center' }}>
              <img
                {...props}
                style={{
                  maxWidth: '100%',
                  height: 'auto',
                  borderRadius: '10px',
                  border: '1px solid var(--panel-border)',
                  boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
                }}
                alt={props.alt || 'Extracted Frame'}
              />
              {props.alt && (
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                  {props.alt}
                </span>
              )}
            </span>
          )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
