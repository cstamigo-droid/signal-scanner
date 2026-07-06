# signal-scanner — MCP server (stdio transport).
# Cumple el requisito de Glama: la imagen arranca el server y responde a introspección.
FROM python:3.11-slim

WORKDIR /app

# Manifiestos + config (cache de capas)
COPY requirements.txt pyproject.toml README.md rules.yaml watchlist.txt ./
COPY signal_scanner ./signal_scanner

# Deps + instalar el paquete
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --no-deps .

# El server habla por stdio (Claude Desktop / Claude Code / introspección de Glama).
# Se invoca el módulo del server directamente (evita el dispatcher CLI console/telegram/mcp).
ENTRYPOINT ["python", "-m", "signal_scanner.server"]
