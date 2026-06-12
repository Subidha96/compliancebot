# CLAUDE.md — ComplianceBot+ Project Brain
# GRC Awareness Chatbot for Women in Kathmandu's Tech Workforce
# BSc Cybersecurity & Ethical Hacking | ST6047CEM | Subidha Pandey

---

## 🚨 CRITICAL RULES — READ BEFORE ANYTHING ELSE

1. **ALWAYS read `docs/PROGRESS.md`, `docs/REMAINING_WORK.md`, and `docs/ERRORS_TO_FIX.md` before writing a single line of code.** If these files do not exist, create them immediately before any other action.
2. **NEVER skip a phase** — complete and test each phase before starting the next.
3. **NEVER hallucinate libraries, APIs, or Nepal-specific regulations.** If uncertain, add a `[VERIFY]` tag inline and log it in `docs/ERRORS_TO_FIX.md`.
4. **NEVER leave dead code, placeholder functions, or TODO stubs in production files.** Every function must be implemented and working.
5. **NEVER use `localStorage` or `sessionStorage`** — the app enforces ephemeral sessions by design.
6. **ALL code must pass linting and type checks** before being marked complete. Run `npm run lint && npm run typecheck` after every file change.
7. **Update the three tracking docs** after completing every task, every session, every bug fix — no exceptions.
8. **If a new chat session starts**, the first action must be: read `docs/PROGRESS.md` to orient yourself, then confirm current state before continuing.
9. **Each feature must have a corresponding test** in `/tests` before it is considered done.
10. **Data minimisation by default** — no PII ever hits the database unless the user explicitly opts in. Verify this on every endpoint.

---

## 🎯 PROJECT CONTEXT

**What:** ComplianceBot+ — an inclusive GRC (Governance-Risk-Compliance) awareness chatbot with policy gap-assessment capability, designed specifically for women aged 18–25 entering Kathmandu's tech workforce.

**Why:** Women constitute only ~7.88% of Nepal's ICT workforce core technical roles. Early-career women face overlapping, poorly explained compliance requirements (Nepal ICT policies, ISO 27001, NIST CSF) with zero accessible guidance in plain language or Nepali.

**Who:** Primary users: women aged 18–25 in Kathmandu SMEs (fintech, e-commerce, agencies). Secondary: GRC professionals, SME managers.

**Academic Context:** BSc (Hons) Ethical Hacking and Cyber Security | Softwarica College / Coventry University | Module ST6047CEM | Supervisor: Manoj Shrestha

**Evaluation Metrics:**
- Technical: policy mapping accuracy (target ≥78%), gap-detection Cohen's kappa (target ≥0.70), response latency (<3s P95)
- Ethical: comprehension gain ≥20% (pre/post quiz), user confidence gain ≥70% after 3 sessions, bias audit pass rate ≥95%

---

## 🗂️ DIRECTORY STRUCTURE

compliancebot-plus/
├── CLAUDE.md                    ← you are here
├── docs/
│   ├── PROGRESS.md              ← completed work log (update every session)
│   ├── REMAINING_WORK.md        ← prioritised backlog by phase
│   └── ERRORS_TO_FIX.md        ← known bugs, [VERIFY] items, TODOs
├── backend/
│   ├── app/
│   │   ├── api/                 ← FastAPI route handlers
│   │   ├── core/                ← config, security, logging
│   │   ├── rag/                 ← retrieval pipeline (ChromaDB + reranker)
│   │   ├── llm/                 ← model loader, inference, SHAP layer
│   │   ├── gap_assessment/      ← rule-based wizard logic
│   │   ├── bias_audit/          ← tone scoring, bias detection
│   │   └── models/              ← Pydantic schemas
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          ← reusable UI components
│   │   ├── pages/               ← route-level pages
│   │   ├── hooks/               ← custom React hooks
│   │   ├── store/               ← Zustand state management
│   │   ├── i18n/                ← en/ne translation files
│   │   └── styles/              ← Tailwind config + global CSS
│   ├── tests/
│   ├── Dockerfile
│   └── package.json
├── data/
│   ├── raw/                     ← source PDFs (Nepal Cyber Security Policy 2023, ETA 2063, ISO 27001 summaries, NIST CSF)
│   ├── processed/               ← chunked + metadata-tagged JSONL
│   └── synthetic/               ← synthetic gap-assessment scenarios
├── scripts/
│   ├── ingest_corpus.py         ← chunk + embed policy documents
│   ├── finetune_qlora.py        ← QLoRA training pipeline
│   ├── bias_audit_runner.py     ← automated tone + bias checks
│   └── eval_pipeline.py        ← comprehension + kappa scoring
├── notebooks/
│   └── exploratory/             ← analysis notebooks (non-production)
├── docker-compose.yml
└── README.md


---

## 🔧 TECH STACK

| Layer | Technology | Version Pin |
|-------|-----------|-------------|
| LLM backbone | Mistral-7B-Instruct-v0.3 (QLoRA via Unsloth) | latest stable |
| Embedding | `sentence-transformers/all-MiniLM-L6-v2` | 2.x |
| Vector DB | ChromaDB | 0.5.x |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | latest |
| Explainability | SHAP | 0.44.x |
| Backend framework | FastAPI + Uvicorn | 0.111.x |
| Frontend framework | Next.js 14 (App Router) | 14.x |
| State management | Zustand | 4.x |
| Styling | Tailwind CSS + shadcn/ui | 3.x / latest |
| Internationalisation | next-i18next | 15.x |
| Accessibility testing | axe-core + jest-axe | latest |
| Containerisation | Docker + Docker Compose | 3.9 |
| Testing (backend) | pytest + pytest-asyncio | latest |
| Testing (frontend) | Vitest + Testing Library | latest |
| Bias auditing | Custom pipeline (see `scripts/bias_audit_runner.py`) | — |
| Readability scoring | textstat (Python) | latest |

**Do NOT use:** OpenAI API, Anthropic API (in production app), any paid proprietary model. All inference must run locally on the QLoRA-adapted model.

---

## 📋 CODING STANDARDS

### Python (backend)
- Python 3.11+, strict type hints everywhere
- Black formatting, isort imports, flake8 linting
- Pydantic v2 for all request/response models
- Async-first: all I/O-bound routes must be `async def`
- No bare `except:` — always catch specific exceptions and log them
- Every module must have a docstring explaining its purpose

### TypeScript (frontend)
- Strict mode: `"strict": true` in tsconfig
- No `any` types — use proper generics or unknown + type guards
- Components: functional only, no class components
- All API calls through a typed service layer in `src/services/`
- Accessibility: every interactive element must have aria attributes

### Git discipline
- Commit after every completed feature or bug fix
- Commit message format: `feat(scope): description` / `fix(scope): description` / `test(scope): description`
- Never commit broken code to main

---

## 🔒 SECURITY & PRIVACY RULES

1. **Ephemeral sessions by default** — no conversation data persists after session end unless user explicitly opts in
2. **No PII collection** — user inputs never stored; only anonymised usage metadata (query category, session length) if user consents
3. **All API endpoints** must validate input with Pydantic before processing
4. **CORS** must be locked to allowed origins only
5. **Rate limiting** on all public endpoints (FastAPI Limiter)
6. **No sensitive data in logs** — mask any content that could identify a user
7. **Bias audit flag** — any response scoring >0.3 on the bias checker must be intercepted and rewritten before delivery

---

## 🌐 NEPAL REGULATORY CORPUS (do not hallucinate these)

The RAG corpus is built from these verified source documents (in `data/raw/`):
- National Cyber Security Policy 2023 (Nepal Cabinet, August 2023)
- Electronic Transactions Act 2063 (2006) — primary cybercrime law
- Cyber Security Bylaw 2077 (2020) — NTA mandatory for TSPs/ISPs
- Individual Privacy Act 2075 (2018)
- Data Act 2079 (2022)
- ISO/IEC 27001:2022 — public summary clauses
- NIST Cybersecurity Framework 2.0 — public summary
- D4D Nepal 2024 Report (digital rights & gender)

**IMPORTANT:** When the model is uncertain about a specific clause, it MUST respond with its confidence score and link to the official source. It must NOT invent regulatory text.

---

## 🧪 TESTING REQUIREMENTS

Every feature is incomplete until:
1. Unit tests pass (`pytest` / `vitest`)
2. Integration test passes (API contract + frontend interaction)
3. Accessibility check passes (`axe-core` scan returns 0 critical violations)
4. Bias audit passes (automated tone check <0.3 threshold)
5. `docs/PROGRESS.md` is updated

---

## 📊 TRACKING FILE FORMATS

### docs/PROGRESS.md format:

```
ComplianceBot+ Progress Log

Last updated: [DATE]

## Completed Features

- [PHASE-FEATURE] Description — tested ✅ — [DATE]

## Current Phase

Phase X: [Name] — [X/Y tasks complete]

## Session Log

### Session [N] — [DATE]
- What was done
- Files changed
- Tests added
```

### docs/REMAINING_WORK.md format:

```
Remaining Work — Prioritised Backlog

## P0 — MVP Core (must ship)

- [FR-01] Description
...

## P1 — Engagement Features

...
```

### docs/ERRORS_TO_FIX.md format:

```
Known Errors & Items to Verify

## 🔴 Critical (blocks functionality)

- [ERROR-001] Description | File: | Line: | Status: open

## 🟡 Non-critical (degrades quality)

...

## 🔵 [VERIFY] Items (uncertain facts to confirm)

...
```

---

## 📜 NEPAL REGULATORY LANDSCAPE (verified sources)

### National Cyber Security Policy 2023
Nepal's Cabinet endorsed this in August 2023 — the country's first dedicated cybersecurity policy. It established the National Cyber Security Center under MoCIT and introduced strategic objectives for protecting critical information infrastructure.

### Electronic Transactions Act 2063 (2006)
The primary cybercrime law. Covers unauthorized access, data alteration, privacy violations. Penalty for privacy breach: up to 3 years imprisonment or NPR 30,000 fine (or both).

### Cyber Security Bylaw 2077 (2020)
Mandatory for all Telecoms/ISPs. Requires quarterly IS audits, 24x7 security monitoring, incident response teams. Monitored by NTA.

### Individual Privacy Act 2075 (2018)
Nepal's first privacy legislation. Covers personal data of individuals in Nepal.

### Data Act 2079 (2022)
Additional data governance provisions.

### Proposed IT Bill / Digital Privacy and Data Protection Act
A pending bill that would introduce 48-hour breach notification and establish a Data Protection Authority of Nepal (as of 2025, still pending).

---

## 📊 GENDER GAP DATA (verified)

- Women constitute 7.88% of Nepal's ICT company workforce in core technical roles (WIIT study, cited in Annapurna Express, June 2025)
- Women hold less than 20% of leadership roles in Nepal's tech sector (New Business Age, October 2024)
- Globally, women account for 22–24% of the cybersecurity workforce (ISC2 2024; GCF 2024)
- UN Women Gender Snapshot 2022: Nepal's digital gender exclusion costs Rs 13 billion, projected to reach Rs 15 billion by 2025
- Women in South Asia are 36% less likely than men to use mobile internet, with 38% reporting online harassment

---

*Generated for: Subidha Pandey | ST6047CEM | Softwarica College / Coventry University*
*Last updated: May 2026*