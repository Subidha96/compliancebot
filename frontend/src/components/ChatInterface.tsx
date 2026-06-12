'use client';

import { useEffect, useRef } from 'react';
import { useChat } from '@/hooks/useChat';
import { useChatStore } from '@/store/chatStore';
import ChatMessageBubble from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import WelcomeMessage from '@/components/WelcomeMessage';
import QuickEscape from '@/components/QuickEscape';

function TypingIndicator() {
  const { darkMode } = useChatStore();
  return (
    <div className="flex justify-start mb-4 animate-fade-in" role="status" aria-label="Bot is typing">
      <div className={`rounded-2xl rounded-bl-md px-4 py-3 ${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white shadow-card border border-warmgray-100'}`}>
        <div className="flex items-center gap-2">
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${darkMode ? 'bg-emerald-600' : 'bg-sage-600'}`} aria-hidden="true">
            <span className="text-white text-xs font-bold">CB</span>
          </div>
          <div className="flex gap-1.5">
            <span className={`w-2 h-2 rounded-full animate-pulse-soft ${darkMode ? 'bg-emerald-400' : 'bg-sage-400'}`} style={{ animationDelay: '0ms' }} />
            <span className={`w-2 h-2 rounded-full animate-pulse-soft ${darkMode ? 'bg-emerald-400' : 'bg-sage-400'}`} style={{ animationDelay: '200ms' }} />
            <span className={`w-2 h-2 rounded-full animate-pulse-soft ${darkMode ? 'bg-emerald-400' : 'bg-sage-400'}`} style={{ animationDelay: '400ms' }} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ChatInterface() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const { escaped, language, sidebarOpen, toggleSidebar, darkMode } = useChatStore();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  if (escaped) {
    return <QuickEscape />;
  }

  return (
    <div className="flex flex-col h-full">
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-30 lg:hidden" onClick={toggleSidebar} aria-hidden="true" />
      )}

      <div
        ref={scrollRef}
        className={`flex-1 overflow-y-auto px-4 py-6 scrollbar-thin ${darkMode ? 'bg-gray-950' : 'bg-warmgray-50'}`}
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
      >
        {messages.length === 0 ? (
          <WelcomeMessage />
        ) : (
          <div className="max-w-3xl mx-auto space-y-1" role="list" aria-label="Conversation">
            {messages.map((msg) => (
              <ChatMessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && <TypingIndicator />}
          </div>
        )}

        {error && (
          <div className={`max-w-3xl mx-auto mt-4 p-4 rounded-2xl text-sm flex items-start gap-3 animate-fade-in ${darkMode ? 'bg-orange-900/30 border border-orange-700 text-orange-300' : 'bg-orange-50 border border-orange-200 text-orange-700'}`} role="alert">
            <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            <div>
              <p className="font-medium mb-1">{language === 'en' ? 'Could not reach the server' : 'सर्भरमा पुग्न सकेन'}</p>
              <p className={`text-xs ${darkMode ? 'text-orange-400' : 'text-orange-600'}`}>{error}</p>
            </div>
          </div>
        )}
      </div>

      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
