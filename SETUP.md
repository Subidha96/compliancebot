# ComplianceBot+ Setup Guide

Choose your setup method below. **Docker is recommended** for reproducible, isolated environments.

---

## 🐳 Option 1: Docker Setup (Recommended)

**Best for:** Production, CI/CD, consistent dev environments, zero dependency conflicts.

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Quick Start (One Command)

```bash
docker-compose up
```

That's it! This starts:
- **Ollama** (local LLM on port 11434)
- **ChromaDB** (vector database on port 8001)
- **Backend** (FastAPI on port 8002)
- **Frontend** (Next.js on port 3000)

### Accessing the App
- Frontend: http://localhost:3000
- API Docs: http://localhost:8002/docs
- Health Check: http://localhost:8002/api/health

### First Time Setup (Pull Ollama Model)

```bash
# In a new terminal while docker-compose is running
docker exec -it compliancebot-ollama-1 ollama pull mistral:latest
```

### Common Commands

```bash
# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild without cache
docker-compose up --build --no-cache

# Remove all data (fresh start)
docker-compose down -v
```

---

## 💻 Option 2: Native Setup (Local Development)

**Best for:** Fast iteration, debugging, local development without containerization.

### Prerequisites
- Python 3.11+
- Node 18+
- npm/pnpm
- Ollama (optional but recommended)
- Git

### Automated Setup

```bash
bash scripts/setup.sh
```

This script will:
1. ✅ Check prerequisites
2. ✅ Create Python venv for backend
3. ✅ Install Python dependencies
4. ✅ Install Node dependencies
5. ✅ Ingest RAG corpus
6. ✅ Run tests
7. ✅ Print next steps

### Manual Setup

**Backend:**
```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # on macOS/Linux
# or: venv\Scripts\activate  # on Windows

# Install dependencies
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Create .env
cat > .env << 'EOF'
DEBUG=true
USE_OLLAMA=true
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:latest
USE_GPU=false
EOF

# Ingest corpus (one-time)
python scripts/ingest_corpus.py --data-dir ../data/raw

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

**Frontend** (new terminal):
```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (optional)
echo 'NEXT_PUBLIC_API_URL=http://localhost:8002' > .env.local

# Start dev server
npm run dev
```

**Ollama** (new terminal):
```bash
# Start Ollama server
ollama serve

# In another terminal, pull a model
ollama pull mistral:latest
```

### Accessing the App
- Frontend: http://localhost:3000
- API Docs: http://localhost:8002/docs

### Development Commands

```bash
# Backend: Run tests
cd backend && pytest -v

# Backend: Type checking
cd backend && mypy app/

# Backend: Linting
cd backend && flake8 app/

# Frontend: Lint
cd frontend && npm run lint

# Frontend: Type check
cd frontend && npm run typecheck

# Frontend: Build
cd frontend && npm run build
```

---

## 🔧 Troubleshooting

### Backend Hangs / No Response

**Problem:** Request times out or backend seems stuck.

**Solution:**
1. Ensure `.env` has `USE_OLLAMA=true`
2. Ensure Ollama is running: `curl http://localhost:11434/api/tags`
3. Check backend logs for errors
4. If using GPU, ensure CUDA/GPU is available or disable with `USE_GPU=false`

### Frontend Can't Reach Backend

**Problem:** `Failed to fetch` or CORS errors in browser console.

**Solution:**
1. Verify backend is running on port 8002: `curl http://localhost:8002/api/health`
2. Check `.env.local` in frontend has correct `NEXT_PUBLIC_API_URL`
3. Restart frontend after changing API URL

### Dependencies Conflict

**Problem:** `ImportError` or version mismatch.

**Solution:**
- Use Docker (avoids this entirely)
- For native setup, ensure using a **fresh Python 3.11 venv**, not global Python

### Ollama Model Not Found

**Problem:** "connection refused" or model not loading.

**Solution:**
```bash
# Check Ollama is running
ollama serve

# Pull the model
ollama pull mistral:latest

# Verify it's there
curl http://localhost:11434/api/tags
```

---

## 📊 System Requirements

| Component | CPU | RAM | Disk | Notes |
|-----------|-----|-----|------|-------|
| Frontend | 1+ | 512MB | 500MB | Node runtime |
| Backend (CPU) | 2+ | 4GB | 2GB | Python + embeddings |
| Backend (GPU) | N/A | 8GB+ | 20GB+ | CUDA 11.8+ required |
| Ollama (CPU) | 4+ | 8GB | 10GB | mistral:latest |
| Ollama (GPU) | N/A | 6GB | 15GB | NVIDIA GPU required |
| ChromaDB | 1+ | 2GB | 5GB | Vector store |

---

## 🚀 Performance Tips

### Docker
- Use SSD for better I/O
- Allocate enough RAM to Docker daemon (8GB+)
- Use `.dockerignore` to skip unnecessary files

### Native (Local)
- Use `pip install -e .` for editable installs during development
- Use `npm run dev` (dev server) not `npm run build` for faster iteration
- Keep a separate Python venv per project to avoid conflicts

### General
- CPU-based Ollama is 2-5x slower than GPU — use GPU if available
- ChromaDB caching helps subsequent queries — responses improve after warm-up
- Frontend build takes ~30s; use dev server for development

---

## 📝 Next Steps

1. **Choose setup method** (Docker recommended)
2. **Follow the setup** (one-liner or script)
3. **Access the app** on http://localhost:3000
4. **Test with a query** like "What is ISO 27001?"
5. **Read PROGRESS.md** for project status
6. **Check ERRORS_TO_FIX.md** for known issues

---

Questions? Check the backend logs or run: `docker-compose logs -f`
