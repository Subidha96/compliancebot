# ComplianceBot+ Quick Start

## 🚀 30-Second Setup

### Docker (Recommended)
```bash
docker-compose up
```
Open browser → http://localhost:3000

### Native (Local Dev)
```bash
bash scripts/setup.sh
# Then run 3 commands in separate terminals:
cd backend && source venv/bin/activate && uvicorn app.main:app --port 8002
cd frontend && npm run dev
ollama serve
```

---

## 📖 First Query

1. Open http://localhost:3000
2. Select readability mode (default/simple/professional/legal)
3. Type: "What is ISO 27001?"
4. Hit Enter or Send button
5. Get RAG-grounded answer with source citations

---

## 🔗 Key URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | The chatbot UI |
| API Docs | http://localhost:8002/docs | OpenAPI Swagger docs |
| Health | http://localhost:8002/api/health | Backend status |
| ChromaDB | http://localhost:8001 | Vector DB admin |

---

## 🛠️ Common Commands

```bash
# Docker
docker-compose up                    # Start all services
docker-compose down                  # Stop all services
docker-compose logs -f backend       # Stream backend logs
docker-compose up --build            # Rebuild images

# Backend (native)
cd backend && source venv/bin/activate
pytest -v                            # Run tests
mypy app/                            # Type check
flake8 app/                          # Lint
uvicorn app.main:app --port 8002    # Start server

# Frontend (native)
cd frontend
npm run dev                          # Dev server (port 3000)
npm run build                        # Production build
npm run lint                         # Lint
npm run typecheck                    # Type check

# Ollama
ollama serve                         # Start Ollama
ollama pull mistral:latest          # Download model
curl http://localhost:11434/api/tags  # List models
```

---

## 🆘 Debug Checklist

- [ ] Backend running? `curl http://localhost:8002/api/health`
- [ ] Ollama running? `curl http://localhost:11434/api/tags`
- [ ] ChromaDB has corpus? Check `/api/health` response (`corpus_size > 0`)
- [ ] CORS? Check browser console for `Access-Control-Allow-Origin` errors
- [ ] Frontend `.env.local`? Check `NEXT_PUBLIC_API_URL=http://localhost:8002`
- [ ] Backend `.env`? Check `USE_OLLAMA=true`, `OLLAMA_HOST=http://localhost:11434`

---

## 📂 Project Structure

```
compliancebot/
├── backend/              # FastAPI + RAG + LLM
├── frontend/             # Next.js 14 + TypeScript
├── data/
│   └── raw/             # Policy documents (6 PDFs)
├── scripts/
│   ├── setup.sh         # One-command native setup
│   └── ingest_corpus.py # RAG ingestion
├── docker-compose.yml   # All services in one file
├── SETUP.md             # Detailed setup guide
└── PROGRESS.md          # Project status & history
```

---

## 🎯 Next Steps After Setup

1. **Read** `PROGRESS.md` — see what's been built
2. **Check** `REMAINING_WORK.md` — see what's left
3. **Review** `ERRORS_TO_FIX.md` — known issues
4. **Test** with sample queries:
   - "What is ISO 27001?"
   - "What does the Electronic Transactions Act say?"
   - "How do I start a gap assessment?"

---

For full details, see **SETUP.md** or **CLAUDE.md**.
