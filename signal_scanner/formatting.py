"""Render Results as Markdown (human, default) or JSON (machine).

Base render() from mcp-factory; extended to format a list of fired signals.
"""
from __future__ import annotations

import json
from enum import Enum

from .result import Result


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


def _fmt(v: object) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def render(result: Result, title: str, fmt: ResponseFormat) -> str:
    if fmt == ResponseFormat.JSON:
        return json.dumps(result.to_dict(), indent=2, default=str)

    lines = [f"# {title}"]
    if not result.ok:
        lines += ["", f"⚠️ {result.error}"]
        return "\n".join(lines)
    if result.summary:
        lines += ["", result.summary]

    signals = result.data.get("signals") if result.data else None
    if signals is not None:
        if not signals:
            lines += ["", "_No symbols matched any rule._"]
        for s in signals:
            lines += ["", f"## {s['symbol']} — {', '.join(s['rules'])}"]
            ind = s.get("indicators", {})
            for k in ("price", "pct_change", "rsi", "sma_fast", "sma_slow",
                      "vol_ratio", "pct_from_52w_high", "pct_from_52w_low"):
                if k in ind and ind[k] is not None:
                    lines.append(f"- **{k.replace('_', ' ')}:** {_fmt(ind[k])}")
        return "\n".join(lines)

    for k, v in (result.data or {}).items():
        if v is not None:
            lines.append(f"- **{k.replace('_', ' ')}:** {_fmt(v)}")
    return "\n".join(lines)


def render_signal_line(s: dict) -> str:
    """One-line alert string (used by console/Telegram delivery)."""
    ind = s.get("indicators", {})
    price = ind.get("price")
    chg = ind.get("pct_change")
    rsi = ind.get("rsi")
    bits = [f"{s['symbol']}"]
    if price is not None:
        bits.append(f"${price:,.2f}")
    if chg is not None:
        bits.append(f"{chg:+.2f}%")
    if rsi is not None:
        bits.append(f"RSI {rsi:.0f}")
    return f"🔔 {' · '.join(bits)} → {', '.join(s['rules'])}"
