'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
}

interface ChatInputProps {
  onSend: (message: string, fileName?: string, fileUrl?: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<{ name: string; url: string } | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<{ stop: () => void; start: () => void; lang: string; interimResults: boolean; continuous: boolean; onresult: ((event: Event) => void) | null; onend: (() => void) | null; onerror: (() => void) | null } | null>(null);
  const { language, darkMode } = useChatStore();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [value]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed && !uploadedFile) return;
    if (disabled) return;
    onSend(trimmed || 'I uploaded a file', uploadedFile?.name, uploadedFile?.url);
    setValue('');
    setUploadedFile(null);
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setUploadedFile({ name: file.name, url });
  };

  const toggleRecording = () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const SpeechRecognitionAPI = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionAPI) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      return;
    }

    const recognition = new SpeechRecognitionAPI();
    recognition.lang = language === 'ne' ? 'ne-NP' : 'en-US';
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onresult = (event: unknown) => {
      const e = event as { results: ArrayLike<{ item: (i: number) => { transcript: string } }> };
      const transcript = Array.from(e.results, (r) => r.item(0).transcript).join('');
      setValue(transcript);
    };

    recognition.onend = () => setIsRecording(false);
    recognition.onerror = () => setIsRecording(false);

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
  };

  return (
    <div className={`border-t px-4 py-3 transition-colors ${darkMode ? 'bg-gray-900 border-gray-700' : 'bg-white border-warmgray-200'}`}>
      <div className="flex items-end gap-2 max-w-3xl mx-auto">
        <input ref={fileInputRef} type="file" className="hidden" onChange={handleFileSelect} accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg" />

        <button onClick={() => fileInputRef.current?.click()} className={`p-2.5 rounded-xl transition-colors flex-shrink-0 ${darkMode ? 'text-gray-400 hover:text-white hover:bg-gray-800' : 'text-warmgray-400 hover:text-warmgray-600 hover:bg-warmgray-100'}`} aria-label="Attach file" title="Attach file">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.939A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.78 7.78a1.5 1.5 0 002.112 2.13" />
          </svg>
        </button>

        <div className="flex-1 relative">
          {uploadedFile && (
            <div className={`mb-2 px-3 py-2 rounded-xl text-xs flex items-center gap-2 ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-warmgray-100 text-warmgray-600'}`}>
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
              <span className="flex-1 truncate">{uploadedFile.name}</span>
              <button onClick={() => setUploadedFile(null)} className="p-0.5 rounded hover:bg-warmgray-200">
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={language === 'en' ? 'Type your question here...' : 'यहाँ आफ्नो प्रश्न टाइप गर्नुहोस्...'}
            disabled={disabled}
            rows={1}
            className={`w-full resize-none rounded-2xl border px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 transition-colors ${
              darkMode
                ? 'border-gray-700 bg-gray-800 text-white placeholder-gray-500 focus:ring-emerald-500 focus:ring-offset-gray-900'
                : 'border-warmgray-200 bg-warmgray-50 text-warmgray-800 placeholder-warmgray-400 focus:ring-sage-400 focus:ring-offset-white'
            }`}
            aria-label="Chat message input"
          />
        </div>

        <button onClick={toggleRecording} className={`p-2.5 rounded-xl transition-colors flex-shrink-0 ${
          isRecording
            ? 'bg-red-500 text-white animate-pulse'
            : darkMode ? 'text-gray-400 hover:text-white hover:bg-gray-800' : 'text-warmgray-400 hover:text-warmgray-600 hover:bg-warmgray-100'
        }`} aria-label={isRecording ? 'Stop recording' : 'Voice input'} title={isRecording ? 'Stop recording' : 'Voice input'}>
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
          </svg>
        </button>

        <button onClick={handleSubmit} disabled={disabled || (!value.trim() && !uploadedFile)} className={`p-2.5 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0 ${
          darkMode ? 'bg-emerald-600 hover:bg-emerald-500 focus:ring-emerald-500 focus:ring-offset-gray-900' : 'bg-sage-600 hover:bg-sage-700 focus:ring-sage-400 focus:ring-offset-white'
        }`} aria-label="Send message">
          {disabled ? (
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          )}
        </button>
      </div>

      <p className={`text-center text-xs mt-2 ${darkMode ? 'text-gray-500' : 'text-warmgray-400'}`}>
        {language === 'en'
          ? 'ComplianceBot+ provides general guidance, not legal advice. Always verify with official sources.'
          : 'ComplianceBot+ ले सामान्य मार्गदर्शन प्रदान गर्दछ, कानुनी सल्लाह होइन। सधैं आधिकारिक स्रोतहरूसँग जाँच गर्नुहोस्।'}
      </p>
    </div>
  );
}
