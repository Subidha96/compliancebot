'use client';

interface ActionButtonsProps {
  sources?: string[];
  sourceUrls?: string[];
}

export default function ActionButtons({ sources, sourceUrls }: ActionButtonsProps) {
  const verifyUrl = sourceUrls?.[0] || '#';

  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {sources && sources.length > 0 && (
        <a
          href={verifyUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-warmgray-100 text-warmgray-600 text-xs font-medium hover:bg-warmgray-200 transition-colors"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.813a4.5 4.5 0 00-6.364 0l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
          </svg>
          Verify Source
        </a>
      )}
    </div>
  );
}
