FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN npm install --ignore-scripts -g @krayinc/docbase-cli \
    && npm cache clean --force

RUN pip install --no-cache-dir uv==0.9.2

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app
RUN chown appuser:appuser /app

USER appuser

COPY --chown=appuser:appuser pyproject.toml uv.lock README.md ./
COPY --chown=appuser:appuser src ./src

RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:${PATH}" \
    DOCBASE_MCP_TRANSPORT=streamable-http \
    DOCBASE_MCP_HOST=0.0.0.0 \
    DOCBASE_MCP_PORT=8000

EXPOSE 8000

CMD ["docbase-mcp"]
