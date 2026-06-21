# Known Errors & Items to Verify

## 🔴 Critical (blocks functionality)

_No critical errors yet._

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