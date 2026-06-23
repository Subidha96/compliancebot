# ComplianceBot+ Docker Setup Guide

## 🚀 Quick Start with Auto Model Download

### One Command to Start Everything

```bash
docker-compose up
```

This will:
1. ✅ Build and start Ollama with **mistral:latest** auto-pull
2. ✅ Start ChromaDB (vector database)
3. ✅ Build and start Backend (FastAPI)
4. ✅ Build and start Frontend (Next.js)
5. ✅ Ingest RAG corpus automatically

**Wait time:** ~2-5 minutes (first time: includes mistral:latest download)

---

## 📊 What Gets Downloaded

```
mistral:latest
├── Size: 4.4 GB
├── Type: Mistral-7B Instruct model
├── Auto-downloaded: Yes ✅
└── Ready in: ~5-10 minutes (depends on internet)
```

---

## 🔍 Monitor the Process

### Watch all services starting:
```bash
docker-compose logs -f
```

### Watch just Ollama model pull:
```bash
docker-compose logs -f ollama
```

### Check when services are ready:
```bash
docker-compose ps
```

---

## ✅ When Ready, You'll See:

```
NAME          STATUS
ollama        Up 2 minutes (healthy) ← Model download complete
chromadb      Up 2 minutes (healthy)
backend       Up 1 minute (healthy)
frontend      Up 30 seconds (healthy)
```

---

## 🌐 Access Points

| Service | URL | Status |
|---------|-----|--------|
| Frontend | http://localhost:3000 | Open in browser |
| API Docs | http://localhost:8002/docs | Swagger UI |
| Health | http://localhost:8002/api/health | Health status |
| Ollama | http://localhost:11434/api/tags | List models |

---

## 🔧 Common Commands

```bash
# Start everything
docker-compose up

# Start in background
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f backend

# Rebuild without cache
docker-compose up --build --no-cache

# Clean everything (remove volumes too)
docker-compose down -v

# Check service status
docker-compose ps

# Enter a container shell
docker exec -it compliancebot-backend-1 bash
```

---

## 🎯 Change the Model

Edit `.env` file:

```bash
OLLAMA_MODEL=llama3.1:latest
```

Or pass as environment variable:

```bash
OLLAMA_MODEL=gemma4:e4b docker-compose up
```

Available models on your system:
- `mistral:latest` (4.4 GB) — default
- `llama3.1:latest` (4.9 GB)
- `qwen3.5:2b` (2.7 GB) — lightweight
- `gemma4:e4b` (9.6 GB) — highest quality

---

## ⚡ Performance Tips

### First Run (Slow)
- Download mistral:latest: ~5-10 min
- Build images: ~2 min
- Total: 7-12 minutes

### Subsequent Runs (Fast)
- Just starts containers: ~30 seconds

### Speed Up Development
- Use `docker-compose up -d` (background mode)
- Keep containers running between sessions
- Use `docker-compose restart` instead of `up` to restart faster

---

## 🆘 Troubleshooting

### Backend can't reach Ollama?
```bash
# Check Ollama is running
docker exec compliancebot-ollama-1 ollama list

# Check connectivity from backend
docker exec compliancebot-backend-1 curl http://ollama:11434/api/tags
```

### Model not downloading?
```bash
# SSH into Ollama container
docker exec -it compliancebot-ollama-1 bash

# Manually pull the model
ollama pull mistral:latest

# Check available models
ollama list
```

### Out of memory?
- Allocate more RAM to Docker (Settings → Resources)
- Switch to lighter model: `OLLAMA_MODEL=qwen3.5:2b`
- Use native setup instead: `bash scripts/setup.sh`

### Disk space issues?
```bash
# Clean unused images/containers
docker system prune -a

# Remove all ComplianceBot containers
docker-compose down -v
```

---

## 📦 What's in docker-compose.yml?

```yaml
services:
  ollama:          # LLM inference (mistral:latest auto-pulled)
  chromadb:        # Vector database for RAG
  backend:         # FastAPI with RAG pipeline
  frontend:        # Next.js UI
```

---

## 🚀 Next Steps

1. Run `docker-compose up`
2. Wait for services to be healthy (check `docker-compose ps`)
3. Open http://localhost:3000
4. Type a query: "What is ISO 27001?"
5. Wait for response (first query is slower as RAG indexes)

---

## 📝 Notes

- Models are persisted in `ollama_data` volume
- ChromaDB data is persisted in `chroma_data` volume
- Backend uses `--reload` for development (auto-restart on code changes)
- Frontend uses next dev server (supports hot reload)

---

For detailed setup info, see **SETUP.md** or **QUICKSTART.md**
