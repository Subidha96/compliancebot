'use client';

import { useState } from 'react';
import type { ChatMessage as ChatMessageType } from '@/store/chatStore';
import { useChatStore } from '@/store/chatStore';
import ConfidenceIndicator from '@/components/ConfidenceIndicator';
import ActionButtons from '@/components/ActionButtons';
import Tooltip, { TERM_DEFINITIONS } from '@/components/Tooltip';
import { getSourceInfo, getColors, cleanSectionName } from '@/lib/sources';

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

        {!isUser && message.sourceCitations && message.sourceCitations.length > 0 && (() => {
          const uniqueSources = new Map<string, typeof message.sourceCitations[0]>();
          message.sourceCitations.forEach((c) => {
            if (!uniqueSources.has(c.source)) uniqueSources.set(c.source, c);
          });
          const citations = Array.from(uniqueSources.values());

          return (
            <div className={`mt-3 pt-3 border-t ${darkMode ? 'border-gray-700' : 'border-warmgray-100'}`}>
              <div className="flex items-center gap-1.5 mb-2">
                <svg className={`w-3.5 h-3.5 ${darkMode ? 'text-gray-500' : 'text-warmgray-400'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                </svg>
                <span className={`text-xs font-medium ${darkMode ? 'text-gray-500' : 'text-warmgray-400'}`}>Sources</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {citations.map((c, i) => {
                  const info = getSourceInfo(c.source);
                  const colors = getColors(info.color, darkMode);
                  const section = cleanSectionName(c.section);
                  return (
                    <a
                      key={`${c.source}-${i}`}
                      href={c.url || '#'}
                      target={c.url ? '_blank' : undefined}
                      rel="noopener noreferrer"
                      className={`group inline-flex items-center gap-2 px-3 py-2 rounded-xl border text-xs transition-all ${
                        c.url
                          ? `${colors.bg} ${colors.text} ${colors.border} hover:shadow-sm`
                          : darkMode ? 'bg-gray-800 text-gray-500 border-gray-700 cursor-default' : 'bg-warmgray-50 text-warmgray-400 border-warmgray-200 cursor-default'
                      }`}
                      title={c.url ? `View ${info.name} — official source` : 'No verified link available'}
                      onClick={(e) => { if (!c.url) e.preventDefault(); }}
                    >
                      <span className="flex items-center gap-1.5 font-semibold">
                        {c.url ? (
                          <svg className={`w-3 h-3 ${colors.text}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                          </svg>
                        ) : (
                          <svg className="w-3 h-3 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                          </svg>
                        )}
                        {info.name}
                      </span>
                      {section !== 'Reference' && (
                        <span className={`px-1.5 py-0.5 rounded-md text-[10px] font-medium ${
                          darkMode ? 'bg-white/10 text-inherit' : 'bg-black/5 text-inherit'
                        }`}>
                          {section}
                        </span>
                      )}
                    </a>
                  );
                })}
              </div>
            </div>
          );
        })()}

        {!isUser && message.sourceUrls && <ActionButtons sources={message.sources} sourceUrls={message.sourceUrls} sourceCitations={message.sourceCitations} />}
      </div>
    </div>
  );
}
