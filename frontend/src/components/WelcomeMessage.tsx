'use client';

import { useChat } from '@/hooks/useChat';
import { useChatStore } from '@/store/chatStore';

const SUGGESTIONS = [
  {
    en: 'What is ISO 27001?',
    ne: 'ISO 27001 के हो?',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
      </svg>
    ),
  },
  {
    en: 'What are the penalties under the ETA?',
    ne: 'ETA अन्तर्गत के के दण्डहरू छन्?',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    ),
  },
  {
    en: 'How does Nepal\'s data protection law work?',
    ne: 'नेपालको डेटा सुरक्षा कानुन कसरी काम गर्छ?',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
      </svg>
    ),
  },
  {
    en: 'Help me start a gap assessment',
    ne: 'ग्याप मूल्याङ्कन सुरु गर्न मद्दत गर्नुहोस्',
    icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5m.75-9l3-3 2.148 2.148A12.061 12.061 0 0116.5 7.605" />
      </svg>
    ),
  },
];

export default function WelcomeMessage() {
  const { language, sendMessage, isLoading } = useChat();
  const { createSession, darkMode } = useChatStore();

  const handleSuggestion = (text: string) => {
    createSession();
    sendMessage(text);
  };

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center animate-fade-in">
      <div className={`w-20 h-20 rounded-3xl flex items-center justify-center mb-6 shadow-soft ${darkMode ? 'bg-emerald-600' : 'bg-sage-600'}`} aria-hidden="true">
        <span className="text-white font-bold text-2xl">CB</span>
      </div>

      <h2 className={`text-2xl font-semibold mb-2 ${darkMode ? 'text-white' : 'text-warmgray-800'}`}>
        {language === 'en' ? "Hello! I'm ComplianceBot+" : 'नमस्ते! म ComplianceBot+ हुँ'}
      </h2>

      <p className={`max-w-lg mb-10 text-sm leading-relaxed ${darkMode ? 'text-gray-400' : 'text-warmgray-500'}`}>
        {language === 'en'
          ? "Your GRC awareness assistant. I can explain Nepal's compliance policies, ISO 27001, NIST CSF, and help you run a gap assessment — all in plain language."
          : 'तपाईंको जीआरसी जागरूकता सहायक। म नेपालको अनुपालन नीतिहरू, ISO 27001, NIST CSF बारे सरल भाषामा बताउन सक्छु र ग्याप मूल्याङ्कन गर्न मद्दत गर्न सक्छु।'}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-xl w-full">
        {SUGGESTIONS.map((s) => (
          <button
            key={s.en}
            onClick={() => handleSuggestion(s[language])}
            disabled={isLoading}
            className={`flex items-center gap-3 text-left px-4 py-3.5 rounded-2xl border text-sm transition-all disabled:opacity-50 shadow-card ${
              darkMode
                ? 'border-gray-700 bg-gray-800 text-gray-200 hover:border-emerald-500 hover:bg-gray-750'
                : 'border-warmgray-200 bg-white text-warmgray-700 hover:border-sage-400 hover:bg-sage-50'
            }`}
          >
            <span className={darkMode ? 'text-emerald-400' : 'text-sage-500'}>{s.icon}</span>
            <span>{s[language]}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
