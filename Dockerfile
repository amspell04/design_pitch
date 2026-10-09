FROM python:3.13-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY agents/requirements.txt agents/requirements.txt
RUN pip install --no-cache-dir -r agents/requirements.txt
COPY agents/ agents/

FROM base AS app
ENV OLLAMA_API_BASE=http://host.docker.internal:11434 \
    PITCHY_MODEL=ollama_chat/qwen3.5:2b
WORKDIR /app/agents
EXPOSE 8000
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000", "."]
