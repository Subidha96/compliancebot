'use client';

import { useChatStore } from '@/store/chatStore';
import ReadabilityToggle from '@/components/ReadabilityToggle';

export default function Header() {
  const { language, setLanguage, isPrivateMode, togglePrivateMode, toggleSidebar, setEscaped, escaped, darkMode, toggleDarkMode } = useChatStore();

  return (
    <header className={`border-b px-4 py-3 flex items-center justify-between z-20 relative transition-colors ${
      darkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-warmgray-200'
    }`} role="banner">
      <div className="flex items-center gap-3">
        <button onClick={toggleSidebar} className={`p-2 rounded-xl transition-colors lg:hidden ${darkMode ? 'hover:bg-gray-800' : 'hover:bg-warmgray-100'}`} aria-label="Toggle sidebar">
          <svg className={`w-5 h-5 ${darkMode ? 'text-gray-400' : 'text-warmgray-600'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>

        <div className="hidden sm:flex items-center gap-2.5">
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${darkMode ? 'bg-emerald-600' : 'bg-sage-600'}`} aria-hidden="true">
            <span className="text-white font-semibold text-xs">CB</span>
          </div>
          <span className={`font-semibold ${darkMode ? 'text-white' : 'text-warmgray-800'}`}>ComplianceBot+</span>
        </div>
      </div>

      <div className="hidden md:block">
        <ReadabilityToggle />
      </div>

      <div className="flex items-center gap-2">
        <button onClick={() => setEscaped(!escaped)} className={`p-2 rounded-xl transition-colors ${darkMode ? 'text-gray-400 hover:bg-gray-800 hover:text-white' : 'text-warmgray-500 hover:bg-warmgray-100 hover:text-warmgray-700'}`} aria-label="Quick escape to notes view" title="Quick escape">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
          </svg>
        </button>

        <button onClick={toggleDarkMode} className={`p-2 rounded-xl transition-colors ${darkMode ? 'text-gray-400 hover:bg-gray-800 hover:text-yellow-400' : 'text-warmgray-500 hover:bg-warmgray-100 hover:text-warmgray-700'}`} aria-label="Toggle dark mode">
          {darkMode ? (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
            </svg>
          )}
        </button>

        <button onClick={togglePrivateMode} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
          isPrivateMode
            ? darkMode ? 'bg-emerald-900/50 text-emerald-300 ring-1 ring-emerald-600' : 'bg-sage-100 text-sage-700 ring-1 ring-sage-300'
            : darkMode ? 'bg-gray-800 text-gray-400 hover:bg-gray-700' : 'bg-warmgray-100 text-warmgray-500 hover:bg-warmgray-200'
        }`} aria-label={isPrivateMode ? 'Private mode on' : 'Private mode off'} aria-pressed={isPrivateMode}>
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            {isPrivateMode ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5V6.75a4.5 4.5 0 119 0v3.75M3.75 21.75h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H3.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            )}
          </svg>
          <span className="hidden sm:inline">{isPrivateMode ? (language === 'en' ? 'Private' : 'निजी') : (language === 'en' ? 'Public' : 'सार्वजनिक')}</span>
        </button>

        <button onClick={() => setLanguage(language === 'en' ? 'ne' : 'en')} className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${darkMode ? 'bg-gray-800 text-gray-300 hover:bg-gray-700' : 'bg-warmgray-100 text-warmgray-600 hover:bg-warmgray-200'}`} aria-label={`Switch to ${language === 'en' ? 'Nepali' : 'English'}`}>
          {language === 'en' ? 'नेपाली' : 'EN'}
        </button>
      </div>
    </header>
  );
}
