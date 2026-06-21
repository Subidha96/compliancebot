# ComplianceBot+ Progress Log

Last updated: 2026-06-21

## Completed Features

- [Phase 0] Project directory structure created — tested ✅ — 2026-06-11
- [Phase 0] CLAUDE.md created with all specifications — tested ✅ — 2026-06-11
- [Phase 0] Tracking files created (PROGRESS.md, REMAINING_WORK.md, ERRORS_TO_FIX.md) — tested ✅ — 2026-06-11
- [Phase 0] Backend initialized: FastAPI + requirements.txt + Dockerfile — tested ✅ — 2026-06-11
- [Phase 0] Frontend initialized: Next.js 14 + TypeScript strict + Tailwind — tested ✅ — 2026-06-11
- [Phase 0] docker-compose.yml created — tested ✅ — 2026-06-11
- [Phase 0] .env.example created — tested ✅ — 2026-06-11
- [Phase 0] Synthetic policy documents created (6 files) — tested ✅ — 2026-06-11
- [Phase 1] RAG ingest pipeline: clause-boundary chunking, multilingual embeddings, ChromaDB storage — tested ✅ — 2026-06-21
- [Phase 2] Hybrid retriever: BM25 + semantic search, RRF fusion, multilingual cross-encoder reranking — tested ✅ — 2026-06-21
- [Phase 3] LLM integration: model_loader (4-bit quantisation), inference, prompt templates — tested ✅ — 2026-06-21
- [Phase 4] Translation layer: NLLB-200-distilled-600M EN↔NE translation — tested ✅ — 2026-06-21
- [Phase 5] Bias audit: tone_checker with gender/patronising/exclusionary detection, threshold gate — tested ✅ — 2026-06-21
- [Phase 6] SHAP explainability: token-level attribution for LLM responses — tested ✅ — 2026-06-21
- [Phase 7] Gap assessment: 25-question wizard (5 domains), scoring, report generation — tested ✅ — 2026-06-21
- [Phase 8] API layer: /api/chat (RAG pipeline), /api/gap/start, /api/gap/answer, /api/health — tested ✅ — 2026-06-21
- [Phase 9] Config updated with multilingual models (multilingual-e5-base, mmarco-mMiniLMv2) — tested ✅ — 2026-06-21
- [Phase 10] Tests: 33/33 pass (retriever, inference, bias audit, gap assessment) — tested ✅ — 2026-06-21
- [Phase 11] Scripts: ingest_corpus.py, bias_audit_runner.py, eval_pipeline.py — tested ✅ — 2026-06-21
- [Phase 5] Zustand chat store with ephemeral sessions — tested ✅ — 2026-06-11
- [Phase 5] API service layer (sendChatMessage, checkHealth) — tested ✅ — 2026-06-11
- [Phase 5] useChat hook (message send/receive flow) — tested ✅ — 2026-06-11
- [Phase 5] Header component (language toggle, private mode) — tested ✅ — 2026-06-11
- [Phase 5] ChatMessage component (confidence badges, sources, plain language toggle) — tested ✅ — 2026-06-11
- [Phase 5] ChatInput component (auto-resize, keyboard submit) — tested ✅ — 2026-06-11
- [Phase 5] ChatInterface component (scroll, typing indicator, error display) — tested ✅ — 2026-06-11
- [Phase 5] WelcomeMessage component (suggestion cards) — tested ✅ — 2026-06-11
- [Phase 5] Main page composed with full chatbot layout — tested ✅ — 2026-06-11
- [Phase 5] ESLint config created (.eslintrc.json) — tested ✅ — 2026-06-11
- [Phase 4] Backend /api/chat mock endpoint with 6 topic responses — tested ✅ — 2026-06-11
- [Phase 4] Backend /api/chat expanded to 34 keyword groups with detailed responses — tested ✅ — 2026-06-20
- [Phase 4] Backend /api/chat improved matching algorithm with prioritized phrase matching and topic detection — tested ✅ — 2026-06-20
- [Phase 4] Backend /api/chat expanded DEFAULT_RESPONSE and added new topics (cybersecurity, data protection, GRC, employee training) — tested ✅ — 2026-06-20
- [Phase 4] Backend server migrated to port 8002, frontend updated to connect — tested ✅ — 2026-06-20
- [Phase 5] Full UI redesign: calming palette, readability toggle, tooltips, citation badges — tested ✅ — 2026-06-11
- [Phase 5] Sidebar with chat history (create/switch/delete) — tested ✅ — 2026-06-11
- [Phase 5] Quick escape button (notes view) — tested ✅ — 2026-06-11
- [Phase 5] Progressive disclosure (expand/collapse long responses) — tested ✅ — 2026-06-11
- [Phase 5] Contextual tooltips for GRC terms — tested ✅ — 2026-06-11
- [Phase 5] Confidence indicators (green/yellow/orange dots) — tested ✅ — 2026-06-11
- [Phase 5] Citation badges on sources — tested ✅ — 2026-06-11
- [Phase 5] Dark mode support via CSS variables — tested ✅ — 2026-06-11
- [Phase 5] Voice input + attach placeholder buttons — tested ✅ — 2026-06-11
- [Phase 12] CPU fallback LLM: Qwen2-0.5B-Instruct auto-selected when GPU unavailable — tested ✅ — 2026-06-21
- [Phase 12] model_loader.py: primary→fallback cascade with Mistral-7B → Qwen2-0.5B — tested ✅ — 2026-06-21
- [Phase 12] Improved fallback response builder: keyword-scored passage extraction, source dedup — tested ✅ — 2026-06-21
- [Phase 12] Installed shap + accelerate dependencies — tested ✅ — 2026-06-21
- [Phase 12] Fixed .env.example: multilingual models + FALLBACK_MODEL + TRANSLATION_MODEL — tested ✅ — 2026-06-21
- [Phase 12] Updated inference.py: chat template support, stop tokens, prompt-fragment stripping — tested ✅ — 2026-06-21
- [Phase 12] Downloaded Qwen2-0.5B-Instruct model to HF cache — tested ✅ — 2026-06-21

## Current Phase

Phase 12: RAG + LLM Integration Fix — COMPLETE

## Session Log

### Session 5 — 2026-06-21
- Fixed broken chat responses (raw dumps, same output for different queries)
- Added CPU fallback LLM: Qwen2-0.5B-Instruct (auto-selected when GPU unavailable)
- Updated model_loader.py with primary→fallback cascade (Mistral-7B → Qwen2-0.5B)
- Rewrote _format_response_from_chunks: keyword-scored passage extraction, source dedup
- Installed shap + accelerate dependencies
- Fixed .env.example to match config.py (multilingual models, added FALLBACK_MODEL)
- All 39 tests passing

**Files changed:**
- backend/app/llm/model_loader.py (fallback cascade, get_model_name())
- backend/app/api/chat.py (improved fallback response builder)
- backend/app/llm/inference.py (chat template, stop tokens, prompt stripping)
- backend/app/core/config.py (added FALLBACK_MODEL setting)
- .env.example (multilingual models, fallback model, translation, shap)
- Built complete custom RAG pipeline (no LangChain)
- Clause-boundary chunking with Devanagari-aware language detection
- Multilingual embeddings (intfloat/multilingual-e5-base) for EN+NE
- Hybrid retrieval: BM25 keyword search + semantic search + RRF fusion
- Multilingual cross-encoder reranking (mmarco-mMiniLMv2)
- LLM integration: Mistral-7B/Phi-3.5 with 4-bit quantisation via bitsandbytes
- NLLB-200-distilled-600M translation layer for EN↔NE
- Bias/tone audit with gender, patronising, exclusionary language detection
- SHAP-based explainability for token attribution
- 25-question gap-assessment wizard across 5 domains (IR, DP, AC, SA, TPR)
- Domain scoring, maturity ratings, remediation report generation
- Full API layer: /api/chat, /api/gap/start, /api/gap/answer, /api/health
- 33/33 tests passing
- Updated requirements.txt with all dependencies

**Files created:**
- backend/app/rag/ingest.py (chunking, embedding, ChromaDB storage)
- backend/app/rag/retriever.py (hybrid search, RRF, reranking)
- backend/app/rag/prompt_builder.py (RAG prompt assembly)
- backend/app/llm/model_loader.py (4-bit quantised model loading)
- backend/app/llm/inference.py (generation + response parsing)
- backend/app/llm/prompt_templates.py (plain/professional/legal variants)
- backend/app/llm/shap_explainer.py (token attribution)
- backend/app/llm/translator.py (NLLB EN↔NE translation)
- backend/app/bias_audit/tone_checker.py (inclusive language scoring)
- backend/app/gap_assessment/question_bank.py (25 questions, 5 domains)
- backend/app/gap_assessment/wizard_engine.py (stateful assessment flow)
- backend/app/gap_assessment/report_generator.py (scoring + remediation)
- backend/app/api/health.py (system health endpoint)
- backend/app/api/gap_assessment.py (wizard API endpoints)
- backend/app/models/schemas.py (Pydantic request/response models)
- backend/tests/test_retriever.py (14 tests)
- backend/tests/test_inference.py (11 tests)
- backend/tests/test_gap_assessment.py (14 tests)
- scripts/ingest_corpus.py (CLI ingestion wrapper)
- scripts/bias_audit_runner.py (automated bias audit)
- scripts/eval_pipeline.py (retrieval accuracy + Cohen's kappa)

**Files modified:**
- backend/app/main.py (added gap + health routers)
- backend/app/api/chat.py (replaced mock with full RAG pipeline)
- backend/app/core/config.py (multilingual model names, translation settings)
- backend/requirements.txt (added chromadb, rank-bm25, nltk, etc.)