'use client';

import { useChatStore } from '@/store/chatStore';

export default function ConfidenceIndicator({ level }: { level: 'high' | 'medium' | 'low' }) {
  const { language } = useChatStore();

  const config = {
    high: { color: 'bg-green-500', label: language === 'en' ? 'High confidence' : 'उच्च विश्वास' },
    medium: { color: 'bg-yellow-500', label: language === 'en' ? 'Verify with source' : 'स्रोतसँग जाँच गर्नुहोस्' },
    low: { color: 'bg-orange-500', label: language === 'en' ? 'Verify with official source' : 'आधिकारिक स्रोतसँग जाँच गर्नुहोस्' },
  };

  const c = config[level];

  return (
    <span className="inline-flex items-center gap-1.5 text-xs text-warmgray-500" title={c.label}>
      <span className={`confidence-dot ${c.color}`} aria-hidden="true" />
      <span className="hidden sm:inline">{c.label}</span>
    </span>
  );
}
