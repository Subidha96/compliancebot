FROM ollama/ollama:latest

COPY scripts/ollama-init.sh /ollama-init.sh
RUN chmod +x /ollama-init.sh

ENTRYPOINT []

CMD ["/bin/bash", "-c", "ollama serve & /ollama-init.sh"]
