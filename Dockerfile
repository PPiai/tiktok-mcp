# TikTok MCP Server - Docker Image
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (playwright needs some)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock* ./

# Install uv and dependencies
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev

# Install playwright browsers
RUN uv run playwright install chromium --with-deps

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=stdio
ENV PLAYWRIGHT_BROWSERS_PATH=/home/mcpuser/.cache/ms-playwright

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import src.tiktok_mcp.server; print('OK')" || exit 1

# Run the MCP server
ENTRYPOINT ["python", "-m", "src.tiktok_mcp.server"]