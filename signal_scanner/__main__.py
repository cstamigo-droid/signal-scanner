"""CLI entrypoint.

  python -m signal_scanner                 # scan once, print to console
  python -m signal_scanner --notify        # also send signals to Telegram (if configured)
  python -m signal_scanner --watch         # loop every SCAN_INTERVAL_S
  python -m signal_scanner AAPL MSFT NVDA  # scan ad-hoc symbols instead of the watchlist
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from . import config, notify, scanner  # noqa: E402


def _scan_once(symbols, do_notify):
    result = scanner.scan_configured(symbols or None)
    if not result.ok:
        print(f"⚠️ {result.error}")
        return
    notify.to_console(result)
    if do_notify:
        tg = notify.to_telegram(result)
        print(f"  [telegram] {tg.summary}")


def main() -> None:
    args = [a for a in sys.argv[1:]]
    do_notify = "--notify" in args
    do_watch = "--watch" in args
    symbols = [a.upper() for a in args if not a.startswith("--")]

    if do_watch:
        print(f"watch mode — scanning every {config.INTERVAL_S}s (Ctrl+C to stop)")
        try:
            while True:
                _scan_once(symbols, do_notify)
                time.sleep(config.INTERVAL_S)
        except KeyboardInterrupt:
            print("\nstopped.")
    else:
        _scan_once(symbols, do_notify)


if __name__ == "__main__":
    main()
