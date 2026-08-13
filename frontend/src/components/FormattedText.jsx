import React from 'react';
import ReactMarkdown from 'react-markdown';

export default function FormattedText({ content }) {
  if (!content) return null;

  return (
    <div className="formatted-markdown">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
