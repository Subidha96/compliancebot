'use client';

import { useChatStore, type ReadabilityLevel } from '@/store/chatStore';

const levels: { key: ReadabilityLevel; en: string; ne: string }[] = [
  { key: 'simple', en: 'Simple', ne: 'साधारण' },
  { key: 'professional', en: 'Professional', ne: 'व्यावसायिक' },
  { key: 'legal', en: 'Legal', ne: 'कानुनी' },
];

export default function ReadabilityToggle() {
  const { readabilityLevel, setReadabilityLevel, language, darkMode } = useChatStore();

  return (
    <div className={`inline-flex rounded-lg p-0.5 ${darkMode ? 'bg-gray-800' : 'bg-warmgray-100'}`} role="radiogroup" aria-label="Readability level">
      {levels.map((level) => (
        <button
          key={level.key}
          onClick={() => setReadabilityLevel(level.key)}
          className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
            readabilityLevel === level.key
              ? darkMode ? 'bg-gray-600 text-white shadow-sm' : 'bg-white text-sage-700 shadow-sm'
              : darkMode ? 'text-gray-400 hover:text-white' : 'text-warmgray-500 hover:text-warmgray-700'
          }`}
          role="radio"
          aria-checked={readabilityLevel === level.key}
        >
          {level[language]}
        </button>
      ))}
    </div>
  );
}
