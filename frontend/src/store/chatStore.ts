import { create } from 'zustand';

// The readability mode is chosen once when a chat session is created and
// locked for that session's entire lifetime — every message in that session
// is answered solely in this mode. To get a different mode, the user starts
// a new chat.
export type ReadabilityLevel = 'default' | 'simple' | 'professional' | 'legal';

export interface SourceCitation {
  source: string;
  section: string;
  confidence: number;
  url?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  confidence?: 'high' | 'medium' | 'low';
  sources?: string[];
  sourceUrls?: string[];
  sourceCitations?: SourceCitation[];
  timestamp: Date;
  fileName?: string;
  fileUrl?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  mode: ReadabilityLevel;
}

interface ChatState {
  sessions: ChatSession[];
  activeSessionId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  isPrivateMode: boolean;
  language: 'en' | 'ne';
  sessionId: string | null;
  error: string | null;
  // The mode picked in the UI for the *next* chat to be created. Once a
  // session exists, its locked mode lives on the ChatSession itself.
  readabilityLevel: ReadabilityLevel;
  sidebarOpen: boolean;
  escaped: boolean;
  darkMode: boolean;
  username: string;

  createSession: () => void;
  switchSession: (id: string) => void;
  deleteSession: (id: string) => void;
  addUserMessage: (content: string, fileName?: string, fileUrl?: string) => void;
  addAssistantMessage: (message: Omit<ChatMessage, 'id' | 'timestamp' | 'role'>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  togglePrivateMode: () => void;
  setLanguage: (lang: 'en' | 'ne') => void;
  setSessionId: (id: string) => void;
  setReadabilityLevel: (level: ReadabilityLevel) => void;
  toggleSidebar: () => void;
  setEscaped: (escaped: boolean) => void;
  toggleDarkMode: () => void;
  setUsername: (name: string) => void;
  clearMessages: () => void;
  activeSessionMode: () => ReadabilityLevel;
}

const generateId = (): string => crypto.randomUUID?.() ?? Math.random().toString(36).slice(2);

const generateTitle = (msg: string): string => {
  const words = msg.split(' ').slice(0, 5).join(' ');
  return words.length > 30 ? words.slice(0, 30) + '...' : words;
};

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  messages: [],
  isLoading: false,
  isPrivateMode: true,
  language: 'en',
  sessionId: null,
  error: null,
  readabilityLevel: 'default',
  sidebarOpen: false,
  escaped: false,
  darkMode: true,
  username: 'Lunar Smith',

  createSession: () => {
    const id = generateId();
    const session: ChatSession = {
      id,
      title: 'New chat',
      messages: [],
      createdAt: new Date(),
      mode: get().readabilityLevel,
    };
    set((state) => ({
      sessions: [session, ...state.sessions],
      activeSessionId: id,
      messages: [],
      sessionId: null,
      error: null,
    }));
  },

  switchSession: (id) => {
    const session = get().sessions.find((s) => s.id === id);
    set({
      activeSessionId: id,
      messages: session?.messages ?? [],
      readabilityLevel: session?.mode ?? get().readabilityLevel,
      error: null,
    });
  },

  deleteSession: (id) => {
    set((state) => {
      const sessions = state.sessions.filter((s) => s.id !== id);
      const isActive = state.activeSessionId === id;
      return {
        sessions,
        activeSessionId: isActive ? (sessions[0]?.id ?? null) : state.activeSessionId,
        messages: isActive ? (sessions[0]?.messages ?? []) : state.messages,
      };
    });
  },

  addUserMessage: (content, fileName, fileUrl) => {
    const msg: ChatMessage = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date(),
      fileName,
      fileUrl,
    };

    set((state) => {
      const activeId = state.activeSessionId ?? generateId();
      const existingSession = state.sessions.find((s) => s.id === activeId);

      const updatedSessions = existingSession
        ? state.sessions.map((s) =>
            s.id === activeId
              ? { ...s, title: s.messages.length === 0 ? generateTitle(content) : s.title, messages: [...s.messages, msg] }
              : s
          )
        : [
            { id: activeId, title: generateTitle(content), messages: [msg], createdAt: new Date(), mode: state.readabilityLevel },
            ...state.sessions,
          ];

      return {
        activeSessionId: activeId,
        messages: [...state.messages, msg],
        sessions: updatedSessions,
      };
    });
  },

  addAssistantMessage: (message) => {
    const msg: ChatMessage = {
      ...message,
      id: generateId(),
      role: 'assistant',
      timestamp: new Date(),
    };

    set((state) => {
      const updatedSessions = state.sessions.map((s) =>
        s.id === state.activeSessionId ? { ...s, messages: [...s.messages, msg] } : s
      );

      return {
        messages: [...state.messages, msg],
        sessions: updatedSessions,
      };
    });
  },

  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  togglePrivateMode: () => set((state) => ({ isPrivateMode: !state.isPrivateMode })),
  setLanguage: (language) => set({ language }),
  setSessionId: (sessionId) => set({ sessionId }),
  setReadabilityLevel: (readabilityLevel) => set({ readabilityLevel }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setEscaped: (escaped) => set({ escaped }),
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
  setUsername: (username) => set({ username }),
  clearMessages: () => set({ messages: [], sessionId: null, error: null }),

  // The mode actually in force for the active session — falls back to the
  // picker value when no session has been created yet.
  activeSessionMode: () => {
    const state = get();
    const session = state.sessions.find((s) => s.id === state.activeSessionId);
    return session?.mode ?? state.readabilityLevel;
  },
}));
