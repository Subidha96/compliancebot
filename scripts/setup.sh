#!/bin/bash

# ComplianceBot+ Setup Script — Full Native Installation
# Platform: Linux/macOS
# Usage: bash scripts/setup.sh

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=====================================\n"
echo -e "ComplianceBot+ Setup Script\n"
echo -e "=====================================\n${NC}"

# ============================================================================
# 1. Check Prerequisites
# ============================================================================
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

for cmd in python3 npm git; do
  if ! command -v $cmd &> /dev/null; then
    echo -e "${RED}❌ $cmd not found. Please install it first.${NC}"
    exit 1
  fi
done

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]; then
  echo -e "${RED}❌ Python 3.11+ required (found $PYTHON_VERSION)${NC}"
  exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}\n"

# ============================================================================
# 2. Backend Setup
# ============================================================================
echo -e "${YELLOW}[2/6] Setting up backend environment...${NC}"

cd backend

# Create Python virtual environment
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo -e "${GREEN}✓ Virtual environment created${NC}"
else
  echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo "Installing Python packages (this may take a few minutes)..."
pip install --default-timeout=1000 -r requirements.txt \
  --extra-index-url https://download.pytorch.org/whl/cpu > /dev/null 2>&1

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Create .env for backend
if [ ! -f ".env" ]; then
  cat > .env << 'EOF'
DEBUG=true
USE_OLLAMA=true
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral:latest
USE_GPU=false
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:3001"]
EOF
  echo -e "${GREEN}✓ Backend .env created${NC}"
else
  echo -e "${GREEN}✓ Backend .env already exists${NC}"
fi

# Ingest corpus (RAG documents)
echo "Ingesting RAG corpus..."
python scripts/ingest_corpus.py --data-dir ../data/raw > /dev/null 2>&1
echo -e "${GREEN}✓ RAG corpus ingested (ChromaDB ready)${NC}"

# Deactivate venv
deactivate

cd ..

echo -e "${GREEN}✓ Backend setup complete\n${NC}"

# ============================================================================
# 3. Frontend Setup
# ============================================================================
echo -e "${YELLOW}[3/6] Setting up frontend environment...${NC}"

cd frontend

# Install Node dependencies
echo "Installing npm packages..."
npm ci > /dev/null 2>&1 || npm install > /dev/null 2>&1
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Create .env.local if needed
if [ ! -f ".env.local" ]; then
  echo 'NEXT_PUBLIC_API_URL=http://localhost:8002' > .env.local
  echo -e "${GREEN}✓ Frontend .env.local created${NC}"
else
  echo -e "${GREEN}✓ Frontend .env.local already exists${NC}"
fi

cd ..

echo -e "${GREEN}✓ Frontend setup complete\n${NC}"

# ============================================================================
# 4. Verify Ollama
# ============================================================================
echo -e "${YELLOW}[4/6] Checking Ollama...${NC}"

if ! command -v ollama &> /dev/null; then
  echo -e "${RED}⚠️  Ollama not found. Install from: https://ollama.ai${NC}"
  echo "    (Or skip if you prefer GPU model loading)"
else
  echo -e "${GREEN}✓ Ollama installed${NC}"

  if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama server is running${NC}"
  else
    echo -e "${YELLOW}⚠️  Ollama not running. Start with: ollama serve${NC}"
    echo "    Then pull a model: ollama pull mistral:latest"
  fi
fi

echo

# ============================================================================
# 5. Run Tests
# ============================================================================
echo -e "${YELLOW}[5/6] Running tests...${NC}"

cd backend
source venv/bin/activate

if pytest -q > /tmp/pytest.log 2>&1; then
  echo -e "${GREEN}✓ All backend tests passed${NC}"
else
  echo -e "${YELLOW}⚠️  Some tests failed (see /tmp/pytest.log)${NC}"
  head -10 /tmp/pytest.log
fi

deactivate
cd ..

echo

# ============================================================================
# 6. Summary & Next Steps
# ============================================================================
echo -e "${YELLOW}[6/6] Setup complete!${NC}\n"

echo -e "${GREEN}=====================================\n"
echo "📋 Next Steps:\n"
echo "1. Start Ollama (if not already running):"
echo "   ${YELLOW}ollama serve${NC}"
echo
echo "2. In a new terminal, start the backend:"
echo "   ${YELLOW}cd backend && source venv/bin/activate && uvicorn app.main:app --port 8002${NC}"
echo
echo "3. In another terminal, start the frontend:"
echo "   ${YELLOW}cd frontend && npm run dev${NC}"
echo
echo "4. Open browser: ${YELLOW}http://localhost:3000${NC}"
echo
echo "🎯 Pro Tips:"
echo "   • Backend logs: ${YELLOW}tail -f /tmp/backend.log${NC}"
echo "   • Run tests: ${YELLOW}cd backend && pytest -v${NC}"
echo "   • Type checker: ${YELLOW}cd backend && mypy app/${NC}"
echo "   • Linting: ${YELLOW}cd backend && flake8 app/; cd ../frontend && npm run lint${NC}"
echo -e "=====================================\n${NC}"
