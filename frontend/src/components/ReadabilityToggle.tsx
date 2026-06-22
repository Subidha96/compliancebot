'use client';

import { useChatStore, type ReadabilityLevel } from '@/store/chatStore';

const levels: { key: ReadabilityLevel; en: string; ne: string }[] = [
  { key: 'default', en: 'Standard', ne: 'मानक' },
  { key: 'simple', en: 'Simple', ne: 'साधारण' },
  { key: 'professional', en: 'Professional', ne: 'व्यावसायिक' },
  { key: 'legal', en: 'Legal', ne: 'कानुनी' },
];

// Mode is locked once a chat session has its first message — it can only be
// chosen before that, or by starting a new chat. This is intentional: a
// session's answers are generated solely in one mode, never regenerated in
// another, so changing it mid-conversation would be misleading.
export default function ReadabilityToggle() {
  const { readabilityLevel, setReadabilityLevel, language, darkMode, messages, activeSessionMode } = useChatStore();
  const locked = messages.length > 0;
  const activeMode = locked ? activeSessionMode() : readabilityLevel;

  return (
    <div className="flex items-center gap-2">
      <div
        className={`inline-flex rounded-lg p-0.5 ${darkMode ? 'bg-gray-800' : 'bg-warmgray-100'} ${locked ? 'opacity-60' : ''}`}
        role="radiogroup"
        aria-label="Readability mode for this chat"
        aria-disabled={locked}
      >
        {levels.map((level) => (
          <button
            key={level.key}
            onClick={() => !locked && setReadabilityLevel(level.key)}
            disabled={locked}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${locked ? 'cursor-not-allowed' : ''} ${
              activeMode === level.key
                ? darkMode ? 'bg-gray-600 text-white shadow-sm' : 'bg-white text-sage-700 shadow-sm'
                : darkMode ? 'text-gray-400 hover:text-white' : 'text-warmgray-500 hover:text-warmgray-700'
            }`}
            role="radio"
            aria-checked={activeMode === level.key}
          >
            {level[language]}
          </button>
        ))}
      </div>
      {locked && (
        <span className={`text-xs ${darkMode ? 'text-gray-500' : 'text-warmgray-400'}`} title="Start a new chat to change mode">
          {language === 'en' ? 'Locked - new chat to change' : 'लक - मोड बदलनुहोस् नयाँ कुराकानीमा'}
        </span>
      )}
    </div>
  );
}
