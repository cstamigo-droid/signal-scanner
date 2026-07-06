# Publicación en Glama + awesome-mcp-servers — signal-scanner
> Listar este server en `punkpeye/awesome-mcp-servers` bajo el proceso 2026: **1 server por PR** + **registro en Glama**.

## ✅ Estado (hecho + verificado 2026-07-06)
- **Dockerfile** creado (`./Dockerfile`, Python 3.11-slim, stdio).
- **Imagen construida OK** (`docker build`).
- **Introspección VERIFICADA**: el contenedor arranca y responde `tools/list` con **1 tool** (`scan`).
  serverInfo `signal-scanner v1.28.1`.
- **`glama.json`** ya existe (maintainer `cstamigo-droid`).
→ Cumple el requisito técnico de Glama ("arrancar y responder a introspección").

Reproducir:
```bash
docker build -t signal-scanner .
printf '%s\n' \
 '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"1"}}}' \
 '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
 '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
 | { cat; sleep 5; } | docker run -i --rm signal-scanner   # devuelve la tool `scan`
```
*(Nota: mantener stdin abierto ~5s para no cortar la respuesta por EOF.)*

## 🙋 Pasos que necesitan TU cuenta (Cristian)
1. **Registrar en Glama:** https://glama.ai/mcp/servers → enlazar `github.com/cstamigo-droid/signal-scanner`.
   Detecta el Dockerfile, corre introspección (ya pasa), asigna **score + ruta Glama** (anotarla).
2. **Abrir UN PR** a `awesome-mcp-servers` con la entrada + badge (abajo).

## 📝 Texto del PR (UNO por server)
**Título:** `Add signal-scanner (rule-based stock/crypto screener with alerts)`

**Entrada para el README** (sección Finance/Stocks o Data/Screeners, orden alfabético):
```
- [cstamigo-droid/signal-scanner](https://github.com/cstamigo-droid/signal-scanner) 🐍 🏠 - Rule-based stock/crypto screener with alerts. Define signals in YAML, scan a watchlist, and get results over console, Telegram, or MCP.
```
*(Leyenda: 🐍 = Python · 🏠 = servicio local/stdio.)*

**Badge de score de Glama** (reemplazar `<GLAMA_PATH>` con la ruta del paso 1):
```
[![signal-scanner MCP server](https://glama.ai/mcp/servers/<GLAMA_PATH>/badges/score.svg)](https://glama.ai/mcp/servers/<GLAMA_PATH>)
```

## Cola restante (misma receta, 1 PR c/u)
`market-data-mcp` · `crypto-intel-mcp` · `rag-starter`.
