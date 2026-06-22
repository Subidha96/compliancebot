'use client';

import { useCallback } from 'react';
import { useChatStore } from '@/store/chatStore';
import { sendChatMessage } from '@/services/api';

export function useChat() {
  const {
    messages,
    isLoading,
    isPrivateMode,
    language,
    error,
    addUserMessage,
    addAssistantMessage,
    setLoading,
    setError,
  } = useChatStore();

  const sendMessage = useCallback(
    async (content: string, fileName?: string, fileUrl?: string) => {
      if (!content.trim() && !fileName) return;
      if (isLoading) return;

      addUserMessage(content, fileName, fileUrl);
      setLoading(true);
      setError(null);

      // Read language/mode directly from store to avoid stale closure
      const currentLanguage = useChatStore.getState().language;
      const currentPrivateMode = useChatStore.getState().isPrivateMode;
      const currentSessionId = useChatStore.getState().sessionId;
      const currentMode = useChatStore.getState().activeSessionMode();

      try {
        const response = await sendChatMessage({
          message: content,
          session_id: currentSessionId ?? undefined,
          language: currentLanguage,
          private_mode: currentPrivateMode,
          mode: currentMode,
        });

        if (!currentSessionId && response.session_id) {
          useChatStore.getState().setSessionId(response.session_id);
        }

        addAssistantMessage({
          content: response.response,
          confidence: response.confidence,
          sources: response.sources,
          sourceUrls: response.source_urls,
          sourceCitations: response.source_citations,
        });
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to get response';
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [isLoading, addUserMessage, addAssistantMessage, setLoading, setError]
  );

  return { messages, isLoading, isPrivateMode, language, error, sendMessage };
}
