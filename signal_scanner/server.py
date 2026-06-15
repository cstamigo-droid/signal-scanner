#!/usr/bin/env python3
"""signal-scanner — rule-based screener over MCP.

Transport: stdio (Claude Desktop / Claude Code / agents).

Tool:
  scan(symbols?, response_format) — evaluate the configured ruleset against the
  given symbols (or the configured watchlist) and return the fired signals.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

from . import scanner
from .formatting import ResponseFormat, render

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

mcp = FastMCP("signal-scanner")


async def _run(fn, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: fn(*args))


class ScanInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    symbols: list[str] = Field(
        default_factory=list,
        description="Symbols to scan (e.g. ['AAPL','BTC-USD']). Empty = use the configured watchlist.",
        max_length=100,
    )
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


@mcp.tool(
    name="scan",
    annotations={"title": "Scan Watchlist", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": True},
)
async def scan(params: ScanInput) -> str:
    """Screen symbols against the ruleset and return which rules fired per symbol.

    Examples:
        - "Run my scanner" -> symbols=[]
        - "Scan AAPL, MSFT and NVDA" -> symbols=['AAPL','MSFT','NVDA']
        - "Any signals on bitcoin?" -> symbols=['BTC-USD']
    """
    result = await _run(scanner.scan_configured, params.symbols or None)
    return render(result, "Signal Scan", params.response_format)


def main() -> None:
    """Console entrypoint — runs the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
