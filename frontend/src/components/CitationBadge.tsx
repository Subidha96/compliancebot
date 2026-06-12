'use client';

interface CitationBadgeProps {
  source: string;
}

export default function CitationBadge({ source }: CitationBadgeProps) {
  return (
    <span className="citation-badge" title={source}>
      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.813a4.5 4.5 0 00-6.364 0l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
      </svg>
      {source.length > 35 ? source.slice(0, 35) + '...' : source}
    </span>
  );
}
