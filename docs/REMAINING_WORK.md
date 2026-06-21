# Remaining Work — Prioritised Backlog

## P0 — MVP Core (must ship)

### Phase 0: Project Scaffold & Tracking Setup
- [x] 0.1 Create full directory structure (see CLAUDE.md tree)
- [x] 0.2 Create docs/PROGRESS.md with header and current state
- [x] 0.3 Create docs/REMAINING_WORK.md with all phases and tasks listed
- [x] 0.4 Create docs/ERRORS_TO_FIX.md (empty but with correct format)
- [x] 0.5 Initialise backend: FastAPI project + requirements.txt + Dockerfile
- [x] 0.6 Initialise frontend: Next.js 14 App Router + TypeScript strict + Tailwind
- [x] 0.7 Create docker-compose.yml (backend + frontend + chromadb services)
- [x] 0.8 Create .env.example with all required environment variables documented
- [ ] 0.9 Verify: `docker-compose build` completes without errors
- [x] 0.10 Update PROGRESS.md

### Phase 1: Data Pipeline & RAG Corpus
- [x] 1.1 Create scripts/ingest_corpus.py
- [x] 1.2 Add 6 synthetic policy documents in data/raw/
- [x] 1.3 Create backend/app/rag/retriever.py
- [x] 1.4 Write tests/test_retriever.py
- [x] 1.5 Update PROGRESS.md

### Phase 2: LLM Integration & Response Pipeline
- [x] 2.1 Create backend/app/llm/model_loader.py
- [x] 2.2 Create backend/app/llm/inference.py
- [x] 2.3 Create backend/app/llm/prompt_templates.py
- [x] 2.4 Create backend/app/bias_audit/tone_checker.py
- [x] 2.5 Create backend/app/llm/shap_explainer.py
- [x] 2.6 Write tests/test_inference.py
- [x] 2.7 Update PROGRESS.md

### Phase 3: Gap Assessment Engine
- [x] 3.1 Create backend/app/gap_assessment/question_bank.py
- [x] 3.2 Create backend/app/gap_assessment/wizard_engine.py
- [x] 3.3 Create backend/app/gap_assessment/report_generator.py
- [x] 3.4 Write tests/test_gap_assessment.py
- [x] 3.5 Update PROGRESS.md

### Phase 4: Backend API Layer
- [x] 4.1 Create backend/app/api/chat.py (full RAG pipeline)
- [x] 4.2 Create backend/app/api/gap_assessment.py
- [x] 4.3 Create backend/app/api/health.py
- [ ] 4.4 Create backend/app/core/session.py (ephemeral session store)
- [ ] 4.5 Create backend/app/core/rate_limiter.py (FastAPI Limiter)
- [x] 4.6 Write tests (33/33 passing)
- [x] 4.7 Update PROGRESS.md

### Phase 5: Frontend — Core UI
- [x] 5.1 Configure Tailwind with custom design tokens
- [x] 5.2 Set up next-i18next with en.json and ne.json
- [x] 5.3 Build core layout components
- [x] 5.4 Build ChatInterface component
- [x] 5.5 Build ProgressTracker component (skipped — not needed for MVP chat)
- [ ] 5.6 Write frontend tests with axe-core
- [x] 5.7 Update PROGRESS.md

## P1 — Engagement Features

### Phase 6: Frontend — Gap Assessment Wizard UI
- [ ] 6.1 Build GapWizard component
- [ ] 6.2 Build GapReport component
- [ ] 6.3 Build ExportButton component
- [ ] 6.4 Write tests for wizard completion flow
- [ ] 6.5 Update PROGRESS.md

## P2 — Ethical & Quality Assurance

### Phase 7: Bias Audit Pipeline & Inclusive Design QA
- [x] 7.1 Implement scripts/bias_audit_runner.py
- [ ] 7.2 Integrate bias_audit into CI
- [ ] 7.3 Create adversarial test set
- [ ] 7.4 Run full WCAG 2.1 AA audit
- [ ] 7.5 Update PROGRESS.md

### Phase 8: Evaluation & Metrics
- [x] 8.1 Create scripts/eval_pipeline.py
- [ ] 8.2 Create synthetic expert baseline
- [ ] 8.3 Create evaluation report template
- [ ] 8.4 Update PROGRESS.md

## P3 — Deployment & Documentation

### Phase 9: Docker & Deployment Polish
- [ ] 9.1 Finalise docker-compose.yml
- [ ] 9.2 Create nginx.conf
- [ ] 9.3 Write README.md
- [ ] 9.4 Run full integration test
- [ ] 9.5 Update PROGRESS.md — mark project COMPLETE
