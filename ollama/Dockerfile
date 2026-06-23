FROM ollama/ollama:latest

# Copy init script
COPY scripts/ollama-init.sh /ollama-init.sh
RUN chmod +x /ollama-init.sh

# Start Ollama and run the init script in background
# The init script will pull the model once the server is ready
CMD ["/bin/bash", "-c", "ollama serve & /ollama-init.sh"]
