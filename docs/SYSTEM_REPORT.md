# ComplianceBot+ — System Report

A plain-but-accurate walkthrough of how the chatbot actually works: tech stack, RAG pipeline, LLM, readability modes, request/response flow, and the supporting safety layers (bias audit, SHAP, translation).

Project: GRC awareness chatbot for women entering Kathmandu's tech workforce — ST6047CEM, Subidha Pandey.

---

## 1. Big picture

```
┌──────────────┐        HTTPS/JSON        ┌──────────────────┐
│   FRONTEND   │ ───────────────────────▶ │     BACKEND      │
│  Next.js 14  │ ◀─────────────────────── │     FastAPI      │
└──────────────┘                          └──────────────────┘
                                                    │
                     ┌──────────────────────────────┼──────────────────────────────┐
                     ▼                              ▼                              ▼
              ┌─────────────┐               ┌──────────────┐              ┌──────────────┐
              │  RAG layer  │               │   LLM layer  │              │  Safety nets  │
              │ ChromaDB +  │──context────▶ │ Ollama /     │──answer────▶ │ Bias audit +  │
              │ BM25 + rerank│               │ Mistral-7B   │              │ SHAP + i18n   │
              └─────────────┘               └──────────────┘              └──────────────┘
```

Nothing leaves the machine. No OpenAI/Anthropic API calls in the chatbot itself — the LLM runs locally via **Ollama** (or a local HuggingFace model as fallback).

---

## 2. Tech stack (what's actually wired up)

| Layer | Technology | Where |
|---|---|---|
| LLM (primary) | Ollama, model `qwen3.5:2b` (local server, `localhost:11434`) | `app/llm/inference.py` |
| LLM (fallback) | `mistralai/Mistral-7B-Instruct-v0.3` → 4-bit on GPU, or `Qwen/Qwen2-0.5B-Instruct` on CPU | `app/llm/model_loader.py` |
| Embeddings | `intfloat/multilingual-e5-base` (English + Nepali) | `app/rag/ingest.py` |
| Vector DB | ChromaDB, persisted at `./chroma_db` | `app/rag/ingest.py` |
| Keyword search | BM25 (`rank_bm25`) over the same corpus | `app/rag/retriever.py` |
| Reranker | `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (multilingual) | `app/rag/retriever.py` |
| Translation | `facebook/nllb-200-distilled-600M` (EN↔NE) | `app/llm/translator.py` |
| Bias/tone audit | Custom regex + `textstat` readability scoring | `app/bias_audit/tone_checker.py` |
| Explainability | SHAP (token attribution) — currently broken, see §8 | `app/llm/shap_explainer.py` |
| Backend | FastAPI + Uvicorn (async) | `backend/app/` |
| Frontend | Next.js 14 (App Router) + Zustand + Tailwind | `frontend/src/` |

---

## 3. The RAG pipeline — how an answer gets its facts

```
 User query
     │
     ▼
┌─────────────────────────────┐
│ 1. semantic_search()        │  multilingual-e5-base embeds the query,
│    cosine similarity vs.    │  ChromaDB returns top-10 nearest chunks
│    ChromaDB (44 chunks)     │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│ 2. keyword_search() (BM25)  │  classic term-overlap search over the
│                              │  same 44 chunks — catches exact terms
└─────────────────────────────┘  embeddings sometimes miss (e.g. "§45")
     │
     ▼
┌─────────────────────────────┐
│ 3. Reciprocal Rank Fusion   │  merges both ranked lists into one
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│ 4. Cross-encoder rerank      │  re-scores the fused candidates with a
│    (mmarco-mMiniLMv2)        │  multilingual cross-encoder — slower but
└─────────────────────────────┘  much more accurate than embeddings alone
     │
     ▼
   top_k = 5 chunks, each tagged with
   {source, section, confidence}
```

**The corpus is closed and finite — 6 real documents, 44 chunks:**

1. National Cyber Security Policy 2023 (Nepal)
2. Electronic Transactions Act 2063 (2006)
3. Cyber Security Bylaw 2077 (2020)
4. Individual Privacy Act 2075 (2018)
5. ISO/IEC 27001:2022 — Annex A control titles
6. NIST Cybersecurity Framework 2.0

All six were re-sourced from official originals (Nepal Law Commission, MoCIT, NTA, NIST CSWP 29) in a prior session — the bot only ever cites these, or says "I don't have enough information."

If retrieval returns nothing relevant, the pipeline stops here and returns a low-confidence "I don't know, try rephrasing" response — **it never lets the LLM freelance outside the corpus.**

---

## 4. The LLM layer — how an answer gets generated

```
build_rag_prompt(query, chunks)
        │
        ▼
┌────────────────────────────────────────────┐
│ SYSTEM_RULES (hard-coded prompt preamble)   │
│ "Answer ONLY using the context below.       │
│  Cite [Source: x, y]. If unsure, say so."   │
├────────────────────────────────────────────┤
│ CONTEXT: <the 5 retrieved chunks>           │
├────────────────────────────────────────────┤
│ QUESTION: <user's query>                    │
└────────────────────────────────────────────┘
        │
        ▼
   mode-specific rewrite instruction appended
   (see §5 — only ONE of these, never more than one)
        │
        ▼
┌────────────────────────────────────────────┐
│ Ollama /api/generate  ("think": false)      │  ← disables hidden
│  model = qwen3.5:2b                         │    chain-of-thought
└────────────────────────────────────────────┘    (was eating the
        │                                          whole token budget)
        ▼
   raw_response → parse_response() → {answer, confidence}
        │
        ▼
   bias/tone audit (§8) → rewrite if score > 0.3
        │
        ▼
   translate to Nepali if query was Nepali
        │
        ▼
   final response_text
```

`generate_response()` is a blocking call (HTTP to Ollama, or a torch forward pass), so it always runs via `asyncio.to_thread()` — otherwise one slow request would freeze the whole FastAPI event loop for every other user.

---

## 5. Readability modes — locked per chat, not per message

**This is the most recently redesigned part of the system.** Earlier versions generated 3–4 full LLM completions per turn (default + simple + professional + legal) "just in case," which was slow and wasteful. The current design:

```
┌─────────────────────────────────────────────────────────────┐
│                     NEW CHAT screen                          │
│                                                                │
│   Pick a mode for THIS conversation:                          │
│                                                                │
│   ( Standard )  ( Simple )  ( Professional )  ( Legal )       │
│        ▲                                                      │
│        └── user clicks one — this is now locked in            │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
        every message in this chat is generated
        SOLELY in that mode — no other mode is
        ever computed for these messages
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  Header toolbar while chatting:                               │
│                                                                │
│   ( Standard )  ( Simple )  ( Professional )  ( Legal )       │
│      ▲ greyed-out, disabled — "Locked, new chat to change"    │
└─────────────────────────────────────────────────────────────┘
```

| Mode | Prompt suffix applied | Audience |
|---|---|---|
| `default` | none — base prompt as-is | general user, balanced detail |
| `simple` | "Rewrite in plain, everyday language… avoid jargon" | non-technical, first-time users |
| `professional` | "Rewrite at a professional level for a compliance officer/IT manager" | SME managers, GRC staff |
| `legal` | "Rewrite with full legal precision, citing exact section/clause numbers" | legal/compliance review |

Want a different mode? **Start a new chat.** That's a deliberate constraint, not a missing feature — it keeps each conversation's tone consistent and keeps inference cost to exactly one generation per message.

```
ChatRequest { message, session_id, language, private_mode, mode }
                                                        │
                                                        ▼
ChatResponse { response, mode, confidence, sources, source_urls,
               source_citations, session_id }
```

(`mode` is echoed back so the frontend can confirm what was actually generated — there is no `plain_language` / `professional` / `legal` field anymore; that was the old multi-variant shape.)

---

## 6. Full request/response sequence

```
 Browser                Next.js (Zustand)            FastAPI /api/chat
    │                          │                             │
    │  type message, hit send │                             │
    ├─────────────────────────▶                             │
    │                          │  POST {message, mode, ...} │
    │                          ├────────────────────────────▶│
    │                          │                             │ greeting? → canned reply
    │                          │                             │ else:
    │                          │                             │   retrieve() — §3
    │                          │                             │   build_rag_prompt()
    │                          │                             │   apply mode suffix — §5
    │                          │                             │   generate_response() — §4
    │                          │                             │   audit_response() — §8
    │                          │                             │   translate() if NE
    │                          │   200 { response, mode,     │
    │                          │     sources, citations }    │
    │                          ◀────────────────────────────┤
    │   render bubble +        │                             │
    │   confidence badge +     │                             │
    │   clickable source links │                             │
    ◀──────────────────────────┤                             │
```

Typical latency: a few seconds for short questions, ~50s for long/complex ones on CPU-only Ollama (qwen3.5:2b) — token budget is scaled to query length so short questions don't pay for a 1024-token essay (`_max_tokens_for_query()`).

---

## 7. What a response actually looks like (GUI sketch)

```
┌──────────────────────────────────────────────────────────────┐
│  CB  ComplianceBot+                              ● High      │
│                                                                │
│  ISO 27001 is a globally recognized standard that helps       │
│  organizations manage and protect their information assets... │
│                                                                │
│  ┌──────────────────────────────┐  ┌─────────────────────┐    │
│  │ 🔗 iso_27001_2022 — Annex A  │  │ 🔗 ETA 2063 — §44-59 │    │
│  │    Organizational (92%)      │  │    Ch.9 (55%)         │    │
│  └──────────────────────────────┘  └─────────────────────┘    │
│                                                                │
│  [ Copy ]  [ Was this helpful? 👍 👎 ]                         │
└──────────────────────────────────────────────────────────────┘
```

- **Confidence badge** (●High / ●Medium / ●Low) comes from the parsed LLM self-rating + retrieval score, not a guess.
- **Source chips** are only clickable if a verified official URL exists for that document (`_SOURCE_URLS` map in `chat.py`) — if not, the chip is shown but inert, never a fabricated link.
- **No raw chunk dumps** — the LLM is instructed to write a real answer, not paste retrieved text.

---

## 8. Safety nets that run on every answer

```
              LLM draft answer
                    │
                    ▼
       ┌─────────────────────────┐
       │   Bias / Tone Checker    │   regex for gendered/patronising/
       │   (tone_checker.py)      │   exclusionary language + textstat
       └─────────────────────────┘   readability scoring
            │              │
      score ≤ 0.3      score > 0.3
            │              │
            ▼              ▼
      send as-is     rewrite_biased_response()
                      (softer phrasing, re-check)
```

- **Bias threshold:** 0.3 (configurable, `settings.BIAS_THRESHOLD`).
- **SHAP explainability** is wired in but currently broken on both backends tested (`masker cannot be None` on Ollama, shape mismatch on HF) — caught internally so it never breaks the chat response, just omits `shap_summary`. Logged as ERROR-009, open.
- **Translation:** if the query is detected as Nepali and `TRANSLATE_OUTPUT=true`, the English answer is machine-translated to Nepali via NLLB-200 before being sent back.
- **Privacy:** sessions are in-memory only (`_sessions` dict), nothing is written to disk; no PII is persisted; closing the tab discards everything.

---

## 9. Other API surface (not chat)

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | liveness + model/ChromaDB status, used by the frontend and this report's curl checks |
| `POST /api/gap/start` | begins the 25-question gap-assessment wizard (5 GRC domains) |
| `POST /api/gap/answer` | submits one wizard answer, returns next question or final report |

The gap-assessment wizard is rule-based (no LLM call per question) — fast and deterministic, separate from the RAG/LLM chat flow.

---

## 10. Known limitations (honest, not hidden)

| Item | Status |
|---|---|
| SHAP explainability | broken on all tested backends — `shap_summary` is always `null` in practice |
| GPU inference | untested in this environment — falls back to CPU (slow: ~50s/answer with Ollama qwen3.5:2b) |
| Browser click-through of mode-lock UI | verified by code review + `tsc --noEmit` + curl, not by driving an actual browser session |
| Corpus size | 44 chunks from 6 documents — deliberately small/closed; the bot will say "I don't know" rather than guess on anything outside it |

---

## 11. One-paragraph summary

A user picks a readability mode once when starting a chat. Every message in that chat is answered by retrieving the most relevant passages from a small, verified corpus of Nepal cyber law + ISO 27001 + NIST CSF (via embeddings + BM25 + cross-encoder reranking), handing those passages plus a mode-specific rewrite instruction to a locally-running LLM (Ollama), auditing the draft for biased/exclusionary tone, translating it if the question was in Nepali, and returning a single answer with real, clickable citations — never a fabricated source, never a different mode than the one the session locked in, and never any data persisted beyond the session.
