'use client';

import { useChatStore } from '@/store/chatStore';

export default function Sidebar() {
  const { sessions, activeSessionId, sidebarOpen, toggleSidebar, createSession, switchSession, deleteSession, language, darkMode, username } = useChatStore();

  return (
    <>
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-30 lg:hidden" onClick={toggleSidebar} aria-hidden="true" />
      )}

      <aside
        className={`fixed top-0 left-0 z-40 h-full w-72 flex flex-col border-r transition-colors duration-300 transform ${
          darkMode
            ? 'bg-gray-900 border-gray-700'
            : 'bg-warmgray-50 border-warmgray-200'
        } ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 lg:static lg:z-auto`}
        aria-label="Chat history"
      >
        <div className="p-4 border-b border-inherit">
          <button onClick={createSession} className={`w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-colors ${
            darkMode ? 'bg-emerald-600 hover:bg-emerald-500 text-white' : 'bg-sage-600 hover:bg-sage-700 text-white'
          }`}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            {language === 'en' ? 'New Chat' : 'नयाँ च्याट'}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-1 scrollbar-thin">
          {sessions.length === 0 ? (
            <p className={`text-xs text-center py-8 ${darkMode ? 'text-gray-500' : 'text-warmgray-400'}`}>
              {language === 'en' ? 'No conversations yet' : 'अझै कुनै कुराकानी छैन'}
            </p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`group flex items-center gap-2 px-3 py-2 rounded-xl text-sm cursor-pointer transition-colors truncate ${
                  session.id === activeSessionId
                    ? darkMode ? 'bg-gray-700 text-white font-medium' : 'bg-sage-100 text-sage-700 font-medium'
                    : darkMode ? 'text-gray-400 hover:bg-gray-800' : 'text-warmgray-600 hover:bg-warmgray-100'
                }`}
                onClick={() => switchSession(session.id)}
              >
                <svg className="w-4 h-4 flex-shrink-0 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
                </svg>
                <span className="flex-1 truncate">{session.title}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }}
                  className={`opacity-0 group-hover:opacity-100 p-1 rounded transition-opacity ${darkMode ? 'hover:bg-gray-600' : 'hover:bg-warmgray-200'}`}
                  aria-label={`Delete ${session.title}`}
                >
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>

        <div className={`p-4 border-t ${darkMode ? 'border-gray-700' : 'border-warmgray-200'}`}>
          <div className={`flex items-center gap-3 ${darkMode ? 'text-gray-400' : 'text-warmgray-500'}`}>
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold ${darkMode ? 'bg-emerald-600 text-white' : 'bg-sage-600 text-white'}`}>
              {username.charAt(0)}
            </div>
            <div>
              <p className="text-sm font-medium">{username}</p>
              <p className="text-xs opacity-60">{language === 'en' ? 'Free Plan' : 'निःशुल्क योजना'}</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
