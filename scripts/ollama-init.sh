#!/bin/bash
# Ollama initialization script — pulls the default model after server starts

set -e

MODEL=${OLLAMA_MODEL:-mistral:latest}
OLLAMA_HOST=${OLLAMA_HOST:-http://localhost:11434}
MAX_RETRIES=30
RETRY_DELAY=2

echo "🚀 Ollama initialization starting..."
echo "   Model: $MODEL"
echo "   Host: $OLLAMA_HOST"

# Wait for Ollama server to be ready
echo "⏳ Waiting for Ollama server to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
  if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama server is ready"
    break
  fi
  if [ $i -eq $MAX_RETRIES ]; then
    echo "❌ Ollama server failed to start after $((MAX_RETRIES * RETRY_DELAY)) seconds"
    exit 1
  fi
  echo "   Attempt $i/$MAX_RETRIES..."
  sleep $RETRY_DELAY
done

# Check if model is already pulled
echo "📦 Checking if $MODEL is already available..."
if curl -s "$OLLAMA_HOST/api/tags" | grep -q "\"$MODEL\""; then
  echo "✅ $MODEL is already available"
  exit 0
fi

# Pull the model
echo "⬇️  Pulling $MODEL (this may take a few minutes on first run)..."
ollama pull $MODEL

echo "✅ Model pull complete!"
