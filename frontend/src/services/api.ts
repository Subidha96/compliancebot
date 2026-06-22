const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8002';

export type ReadabilityMode = 'default' | 'simple' | 'professional' | 'legal';

export interface ChatRequest {
  message: string;
  session_id?: string;
  language: 'en' | 'ne';
  private_mode: boolean;
  mode: ReadabilityMode;
}

export interface SourceCitation {
  source: string;
  section: string;
  confidence: number;
  url?: string;
}

export interface ChatResponse {
  response: string;
  mode: ReadabilityMode;
  confidence: 'high' | 'medium' | 'low';
  sources: string[];
  source_urls: string[];
  source_citations: SourceCitation[];
  session_id: string;
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => 'Unknown error');
    throw new Error(`Chat request failed (${res.status}): ${errorBody}`);
  }

  return res.json();
}
