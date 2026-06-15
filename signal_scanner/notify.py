"""Delivery — console always, Telegram optionally (degrades gracefully).

Without TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, alerts print to the console only;
the scanner still works. With them set, each scan's signals are pushed to Telegram.
"""
from __future__ import annotations

import os

from .formatting import render_signal_line
from .result import Result


def to_console(result: Result) -> None:
    print(result.summary)
    for s in result.data.get("signals", []):
        print("  " + render_signal_line(s))


def telegram_configured() -> bool:
    return bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"))


def to_telegram(result: Result) -> Result:
    """Send the fired signals to Telegram. No-op (ok=False) if unconfigured."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat):
        return Result.failed("telegram", "TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not set")
    signals = result.data.get("signals", [])
    if not signals:
        return Result(source="telegram", ok=True, summary="no signals to send", data={"sent": 0})

    lines = [render_signal_line(s) for s in signals]
    text = "📡 *signal-scanner*\n" + "\n".join(lines)
    try:
        import requests
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
        resp.raise_for_status()
        return Result(source="telegram", ok=True, summary=f"sent {len(lines)} signal(s)",
                      data={"sent": len(lines)})
    except Exception as e:
        return Result.failed("telegram", str(e))
