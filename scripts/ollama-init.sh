#!/bin/bash
set -e

MODEL=${OLLAMA_MODEL:-mistral:latest}
MAX_RETRIES=30
RETRY_DELAY=2

echo "Ollama initialization starting..."
echo "Model: $MODEL"

echo "Starting Ollama..."
ollama serve &
SERVER_PID=$!

echo "Waiting for Ollama server..."

for i in $(seq 1 $MAX_RETRIES); do
    if ollama list >/dev/null 2>&1; then
        echo "Ollama server is ready"
        break
    fi

    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "Failed to start Ollama"
        exit 1
    fi

    sleep $RETRY_DELAY
done

echo "Pulling model..."
ollama pull "$MODEL"

echo "Initialization complete."

# Keep container running
wait $SERVER_PID
