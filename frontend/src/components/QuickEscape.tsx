'use client';

import { useChatStore } from '@/store/chatStore';

export default function QuickEscape() {
  const { setEscaped, language, darkMode } = useChatStore();

  return (
    <div className={`flex flex-col items-center justify-center h-full p-8 text-center ${darkMode ? 'bg-gray-950' : 'bg-warmgray-50'}`}>
      <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 ${darkMode ? 'bg-gray-800' : 'bg-warmgray-200'}`}>
        <svg className={`w-8 h-8 ${darkMode ? 'text-gray-400' : 'text-warmgray-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
        </svg>
      </div>
      <h2 className={`text-xl font-semibold mb-2 ${darkMode ? 'text-white' : 'text-warmgray-700'}`}>
        {language === 'en' ? 'My Notes' : 'मेरो नोट्स'}
      </h2>
      <p className={`text-sm max-w-md ${darkMode ? 'text-gray-400' : 'text-warmgray-500'}`}>
        {language === 'en'
          ? 'This is a private notes view. No chat data is visible here.'
          : 'यो एक निजी नोट्स दृश्य हो। यहाँ कुनै च्याट डेटा देखिँदैन।'}
      </p>
      <button onClick={() => setEscaped(false)} className={`mt-6 px-6 py-2.5 rounded-xl text-sm font-medium transition-colors ${darkMode ? 'bg-emerald-600 text-white hover:bg-emerald-500' : 'bg-sage-600 text-white hover:bg-sage-700'}`}>
        {language === 'en' ? 'Return to Chat' : 'च्याटमा फर्कनुहोस्'}
      </button>
    </div>
  );
}
