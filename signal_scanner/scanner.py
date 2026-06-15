"""Orchestration: watchlist -> data -> indicators -> rules -> signals.

scan() is pure (symbols + rules in, Result out) so it's trivially testable and
reusable from the CLI, the MCP server, or any app.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import config, data, indicators, rules
from .result import Result


def load_watchlist(path: str | Path | None = None) -> list[str]:
    p = Path(path) if path else config.WATCHLIST
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s.split()[0])  # allow "AAPL  # Apple" comments
    return out


def scan(symbols: list[str], ruleset: list[dict[str, Any]]) -> Result:
    """Evaluate every symbol against the ruleset; return fired signals."""
    if not symbols:
        return Result.failed("scanner", "empty watchlist")
    if not ruleset:
        return Result.failed("scanner", "empty ruleset")

    signals = []
    scanned = 0
    errors = []
    for sym in symbols:
        df = data.history(sym)
        if df is None or df.empty:
            errors.append(sym)
            continue
        scanned += 1
        ind = indicators.compute(df)
        fired = rules.evaluate(ind, ruleset)
        if fired:
            signals.append({"symbol": sym.upper(), "rules": fired, "indicators": ind})

    summary = (f"Scanned {scanned}/{len(symbols)} symbols against {len(ruleset)} rule(s): "
               f"{len(signals)} match(es).")
    if errors:
        summary += f" No data for: {', '.join(errors[:10])}."
    return Result(source="scanner", ok=True, summary=summary,
                  data={"signals": signals, "scanned": scanned,
                        "no_data": errors, "rules_count": len(ruleset)})


def scan_configured(symbols: list[str] | None = None) -> Result:
    """Scan using the configured ruleset and (optionally overridden) watchlist."""
    try:
        ruleset = rules.load(config.RULES)
    except Exception as e:
        return Result.failed("scanner", f"ruleset error: {e}")
    syms = symbols if symbols else load_watchlist()
    return scan(syms, ruleset)
