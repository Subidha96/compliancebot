'use client';

import { useEffect } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import ChatInterface from '@/components/ChatInterface';
import { useChatStore } from '@/store/chatStore';

export default function Home() {
  const { darkMode } = useChatStore();

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  return (
    <div className={`flex flex-col h-screen transition-colors ${darkMode ? 'bg-gray-950' : 'bg-warmgray-50'}`}>
      <a
        href="#chat-input"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50 focus:bg-sage-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-xl"
      >
        Skip to content
      </a>

      <Header />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main id="chat-input" className="flex-1 overflow-hidden">
          <ChatInterface />
        </main>
      </div>
    </div>
  );
}
