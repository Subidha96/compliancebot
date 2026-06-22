# Known Errors & Items to Verify

## 🔴 Critical (blocks functionality)

- [ERROR-008] PROGRESS.md falsely claimed "39/39 tests passing" / RAG pipeline complete, but ML deps (torch, chromadb, transformers, sentence-transformers, rank-bm25) were never actually installed in the working dev environment, and corpus was never ingested (no chroma_db existed, data/processed/ was empty) | Status: fixed ✅ — 2026-06-22
  - Root cause: tracking docs were updated to reflect intended/expected state, not verified actual state — no venv/requirements install had been run, ingest_corpus.py had never been executed
  - Verification: `pytest` initially showed 17/39 failures (ModuleNotFoundError). After `pip install -r requirements.txt` + running `scripts/ingest_corpus.py --data-dir <abs path to data/raw>`, all 39/39 tests pass and a live `/api/chat` request returns a real grounded answer (verified via curl against running uvicorn server with MODEL_NAME=Qwen/Qwen2-0.5B-Instruct)
  - Note: deps were installed into the global/user pip environment (no venv existed) — this triggered a dependency conflict with an unrelated project "jarvis-ui" (pydantic 1.10.7 → 2.13.4, packaging 23.1 → 26.2). A project-local venv should be created to avoid polluting global site-packages going forward.
  - Note: `scripts/ingest_corpus.py --data-dir data/raw` default is relative and breaks when run from `backend/` (cwd-dependent) — must pass absolute path or always run from repo root.

- [ERROR-009] SHAP explainability fails on every real LLM call: "SHAP analysis unavailable: The model produced 81 output rows when given 1 input rows" (HF/transformers path) / "masker cannot be None" (Ollama path) | File: backend/app/llm/shap_explainer.py | Status: open — 2026-06-22
  - Observed during live verification of /api/chat with both Qwen2-0.5B-Instruct fallback and Ollama mistral:latest
  - Caught internally (doesn't break the chat response, shap_summary just reports the error string) but Phase 6 (SHAP explainability) is not actually functional under any backend tested so far

- [ERROR-010] Source citations showed generic "part-N" labels instead of genuine section names | File: backend/app/rag/ingest.py | Status: fixed ✅ — 2026-06-22
  - Root cause: `_SECTION_PATTERN`/`_LABEL_PATTERN` only matched "Section/Clause/Article/Bylaw N" style legal markers, but all 6 actual source docs in data/raw/ use numbered ALL-CAPS headings (e.g. "1. ORGANIZATIONAL CONTROLS (A.5)") — the regex never matched, so every chunk fell back to `part-{i+1}`
  - Solution: added `_HEADING_PATTERN` (`^\d+\.\s+(.+)`) to extract the real heading text when no legal-keyword label is found; updated `_SECTION_PATTERN` to also split on these numbered headings (anchored to line start via MULTILINE) instead of only paragraph breaks
  - Also fixed: a prior ingest run had been executed from the repo root instead of `backend/`, silently creating a duplicate `chroma_db` at the wrong path that the running app never reads from — deleted the stray directory, re-ingested correctly from `backend/`
  - Verified: citations now show e.g. "ORGANIZATIONAL CONTROLS (A.5)" instead of "part-1"; only each document's intro/title paragraph (before the first numbered heading) still falls back to `part-1`, which is correct since it isn't a real clause; 39/39 tests pass

- [ERROR-011] Switching default Ollama model to `qwen3.5:2b` caused empty `response` text on every real `/api/chat` request despite 200 OK and ~58s latency | File: backend/app/llm/inference.py | Status: fixed ✅ — 2026-06-22
  - Root cause: `qwen3.5:2b` is a hybrid reasoning ("thinking") model — by default it spends the whole `num_predict` budget on a hidden chain-of-thought emitted in a separate `"thinking"` JSON field, leaving nothing for the actual `"response"` field once the budget is exhausted on longer/more complex RAG prompts
  - Diagnosis: confirmed via raw `curl` against Ollama's `/api/generate` directly — a short test prompt returned a good `response`, but adding `"think": false` was required to reliably get a complete `response` instead of an empty one
  - Solution: added `"think": false` to the JSON body in `_generate_with_ollama()` to disable hidden reasoning tokens
  - Verified: live `/api/chat` request for "What is ISO 27001?" now returns a full, well-cited, non-empty answer in ~50s; `pytest -q` 39/39 passed

- [ERROR-012] All 6 files in data/raw/ were "SYNTHETIC EDUCATIONAL SUMMARY" placeholders with fabricated specifics presented as if verified — e.g. nepal_cyber_security_policy invented "NP-CERT" and "24-hour breach reporting" (not in the real policy), privacy_act_2075_summary described a GDPR-style framework (Data Protection Officer, 72-hour breach notice, right to data portability) that does not exist in Nepal's actual Privacy Act 2075, cyber_security_bylaw invented "quarterly IS audits" (real cadence: 6-monthly internal audit, 3-monthly pentest, annual IS audit per Clause 53-55), and the CLAUDE.md-stated "ETA penalty: 3yrs/NPR 30,000" actually belongs to the Privacy Act 2075 §29(2), not the ETA (ETA §48 confidentiality breach is NPR 10,000/2yrs) | Files: data/raw/*.txt | Status: fixed ✅ — 2026-06-22
  - Root cause: corpus was originally written as plausible-sounding placeholder text rather than sourced from the actual laws/standards, despite CLAUDE.md's "never hallucinate Nepal-specific regulations" rule
  - Solution: re-sourced all 6 documents from official government/standards-body originals — Nepal Law Commission and MoCIT/NTA gov.np PDFs (via WebSearch + curl, extracted with pypdf since they're scanned/compressed PDFs WebFetch couldn't parse) for the 4 Nepal documents, the NIST CSWP 29 official PDF (public-domain US gov work) for NIST CSF 2.0, and a verified 93-control Annex A title list for ISO 27001:2022 (ISO doesn't publish full control text for free, only titles are reproduced). Each file now states verbatim section/clause numbers and quotes, with [VERIFY] tags for anything abbreviated for length.
  - Re-ingested corpus: 44 chunks (up from 40) via `scripts/ingest_corpus.py`; backend restarted to clear stale BM25 cache; verified live query "What is the penalty for a privacy violation under Nepal law?" now correctly cites Privacy Act 2075 §29-32 with the real 3yr/NPR 30,000 penalty instead of the old fabricated NPR 100,000/500,000 figures
  - 39/39 tests still pass
  - **Fixed 2026-06-22**: corrected CLAUDE.md's "Nepal Regulatory Landscape" section — the ETA entry now cites its real §44/§45/§48 penalties instead of the misattributed 3yr/30,000 figure, the Privacy Act entry now correctly states the 3yr/NPR 30,000 penalty (§29(2)), and the Bylaw entry now states the real audit cadence (6-monthly internal, 3-monthly pentest, annual IS audit) instead of "quarterly IS audits"

- [ERROR-013] Readability-mode architecture let a user view any already-answered message in any of the 4 modes via a global per-message toggle, lazily generating missing variants mid-conversation | Files: backend/app/api/chat.py, backend/app/models/schemas.py, frontend/src/store/chatStore.ts, frontend/src/components/ChatMessage.tsx, frontend/src/components/ReadabilityToggle.tsx, frontend/src/hooks/useChat.ts, frontend/src/services/api.ts | Status: fixed ✅ — 2026-06-22
  - Root cause: Session 7 built a "free default + lazy on-demand variant" toggle to cut LLM/RAM load, but this still let the same conversation be re-answered in a different register at any point, which the user explicitly does not want
  - Fix: mode is now chosen once at chat-session creation (`ChatSession.mode`), sent on every turn via `ChatRequest.mode`, and the backend generates exactly one answer in that mode per turn (`_generate_main_answer` picks the prompt template up front). Removed `/api/chat/variant`, `ChatVariantRequest/Response`, the per-session `contexts` cache, and all per-message variant fields/state. `ReadabilityToggle` now locks after a session's first message; switching modes requires starting a new chat.
  - Verified: `tsc --noEmit` clean, `pytest -q` 39/39, live curl with `mode:"legal"` returns a single legal-register answer with no other variant ever generated

## 🟡 Non-critical (degrades quality)

- [FIX-001] Chatbot returning same generic response for all questions | File: backend/app/api/chat.py | Status: fixed ✅ — 2026-06-20
  - Root cause: Only 9 keyword groups with single DEFAULT_RESPONSE fallback
  - Solution: Expanded to 34 keyword groups with topic-specific detailed responses (10-12 lines each)
  - Added: Follow-up handling, policy communication, MFA, least privilege, phishing, cloud security, startup compliance, gender inclusion
  
- [FIX-002] Keyword matching too strict for natural language queries | File: backend/app/api/chat.py | Status: fixed ✅ — 2026-06-20
  - Root cause: Simple substring matching failed for natural language variations
  - Solution: Implemented 3-tier matching: (1) Prioritized phrase matching, (2) Word-by-word scoring, (3) Topic detection with contextual defaults
  - Added more keyword variations for common queries

- [FIX-003] DEFAULT_RESPONSE too generic and unhelpful | File: backend/app/api/chat.py | Status: fixed ✅ — 2026-06-20
  - Root cause: Default response said "I'm not sure" and didn't provide useful information
  - Solution: Updated DEFAULT_RESPONSE with comprehensive list of available topics and examples
  - Added new topic groups: cybersecurity definition, data protection methods, employee training, GRC explanation

- [FIX-004] RAG fallback returning raw chunk dumps, identical for different queries | File: backend/app/api/chat.py | Status: fixed ✅ — 2026-06-21
  - Root cause: _format_response_from_chunks just concatenated raw chunk text with source labels
  - Solution: Rewrote to extract keyword-scored passages, deduplicate by source, format as structured answers

- [FIX-005] LLM not loading (no GPU/bitsandbytes) causing retrieval-only fallback | File: backend/app/llm/model_loader.py | Status: fixed ✅ — 2026-06-21
  - Root cause: Mistral-7B requires GPU + bitsandbytes, unavailable on CPU-only machines
  - Solution: Added fallback cascade — tries Mistral-7B first, falls back to Qwen2-0.5B-Instruct (CPU-friendly, 0.5B params)

- [FIX-006] .env.example had English-only models while config.py used multilingual | File: .env.example | Status: fixed ✅ — 2026-06-21
  - Root cause: .env.example listed all-MiniLM-L6-v2 and ms-marco-MiniLM-L-6-v2 (English-only)
  - Solution: Updated to multilingual-e5-base and mmarco-mMiniLMv2 to match config.py defaults

- [FIX-007] shap package not installed | File: backend/app/llm/shap_explainer.py | Status: fixed ✅ — 2026-06-21
  - Root cause: shap was in requirements.txt but not installed
  - Solution: Installed shap + accelerate packages

## 🔵 [VERIFY] Items (uncertain facts to confirm)

- [VERIFY-001] Confirm exact clause numbers for Nepal Cyber Security Policy 2023 when adding to RAG corpus | Status: pending
- [VERIFY-002] Verify current status of proposed Digital Privacy and Data Protection Act (as of 2026) | Status: pending
- [VERIFY-003] Confirm NTA monitoring requirements under Cyber Security Bylaw 2077 | Status: pending