'use client';

import { useState } from 'react';
import type { ChatMessage as ChatMessageType } from '@/store/chatStore';
import { useChatStore } from '@/store/chatStore';
import ConfidenceIndicator from '@/components/ConfidenceIndicator';
import ActionButtons from '@/components/ActionButtons';
import Tooltip, { TERM_DEFINITIONS } from '@/components/Tooltip';

function highlightTerms(text: string): React.ReactNode[] {
  const terms = Object.keys(TERM_DEFINITIONS);
  const regex = new RegExp(`(${terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'g');
  const parts = text.split(regex);
  return parts.map((part, i) => {
    if (TERM_DEFINITIONS[part]) {
      return <Tooltip key={i} term={part} definition={TERM_DEFINITIONS[part]}>{part}</Tooltip>;
    }
    return part;
  });
}

export default function ChatMessageBubble({ message }: { message: ChatMessageType }) {
  const isUser = message.role === 'user';
  const { language, darkMode } = useChatStore();
  const [expanded, setExpanded] = useState(false);

  const content = message.content;
  const hasMore = !isUser;
  const shortContent = content.split('\n').slice(0, 2).join('\n');
  const needsExpand = hasMore && content.split('\n').length > 3 && !expanded;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-slide-up`} role="listitem">
      <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
        isUser
          ? darkMode ? 'bg-emerald-600 text-white rounded-br-md' : 'bg-sage-600 text-white rounded-br-md'
          : darkMode ? 'bg-gray-800 text-gray-100 rounded-bl-md border border-gray-700' : 'bg-white text-warmgray-800 rounded-bl-md shadow-card border border-warmgray-100'
      }`}>
        {!isUser && (
          <div className="flex items-center gap-2 mb-2">
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${darkMode ? 'bg-emerald-600' : 'bg-sage-600'}`} aria-hidden="true">
              <span className="text-white text-xs font-bold">CB</span>
            </div>
            <span className={`text-xs font-medium ${darkMode ? 'text-gray-400' : 'text-warmgray-500'}`}>ComplianceBot+</span>
            {message.confidence && <ConfidenceIndicator level={message.confidence} />}
          </div>
        )}

        {isUser && message.fileName && (
          <div className={`mb-2 px-3 py-2 rounded-lg text-xs flex items-center gap-2 ${darkMode ? 'bg-emerald-700' : 'bg-sage-500/20'}`}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
            {message.fileName}
          </div>
        )}

        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {needsExpand ? highlightTerms(shortContent) : highlightTerms(content)}
        </div>

        {needsExpand && (
          <button onClick={() => setExpanded(true)} className={`mt-2 text-xs font-medium flex items-center gap-1 ${darkMode ? 'text-emerald-400 hover:text-emerald-300' : 'text-sage-600 hover:text-sage-700'}`}>
            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
            </svg>
            {language === 'en' ? 'Show more' : 'थप देखाउनुहोस्'}
          </button>
        )}

        {!isUser && message.sourceCitations && message.sourceCitations.length > 0 && (
          <div className={`flex flex-col gap-1.5 mt-3 pt-3 border-t ${darkMode ? 'border-gray-700' : 'border-warmgray-100'}`}>
            {message.sourceCitations.map((c, i) => (
              <a
                key={`${c.source}-${i}`}
                href={c.url || '#'}
                target={c.url ? '_blank' : undefined}
                rel="noopener noreferrer"
                className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs transition-colors ${
                  c.url
                    ? darkMode ? 'bg-purple-900/50 text-purple-300 hover:bg-purple-800/50' : 'bg-lavender-100 text-lavender-500 hover:bg-lavender-200'
                    : darkMode ? 'bg-gray-700/50 text-gray-400 cursor-default' : 'bg-warmgray-100 text-warmgray-500 cursor-default'
                }`}
                title={c.url ? 'Open verified official source' : 'No verified official link available for this document'}
                onClick={(e) => { if (!c.url) e.preventDefault(); }}
              >
                <svg className="w-3 h-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m9.86-2.813a4.5 4.5 0 00-6.364 0l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
                </svg>
                <span className="font-medium">{c.source}</span>
                <span className="opacity-70">— {c.section}</span>
                <span className="opacity-50">({Math.round(c.confidence * 100)}%)</span>
              </a>
            ))}
          </div>
        )}

        {!isUser && message.sourceUrls && <ActionButtons sources={message.sources} sourceUrls={message.sourceUrls} />}
      </div>
    </div>
  );
}
