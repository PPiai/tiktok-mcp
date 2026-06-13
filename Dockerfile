# TikTok MCP Server - Docker image (streamable-HTTP, pronto para Easypanel)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    MCP_TRANSPORT=streamable-http

WORKDIR /app

# Metadados + codigo, depois instala o pacote (gera o console script tiktok-mcp)
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --upgrade pip && pip install .

# Usuario nao-root
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

EXPOSE 8000

# Healthcheck: confere se a porta esta aceitando conexoes
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import socket,os; s=socket.socket(); s.settimeout(3); s.connect(('127.0.0.1', int(os.getenv('PORT','8000')))); s.close()" || exit 1

# Inicia o servidor MCP (streamable-HTTP em 0.0.0.0:$PORT)
CMD ["tiktok-mcp"]
