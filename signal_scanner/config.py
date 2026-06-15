"""Central configuration — a client reskin is this file + the ruleset/watchlist.

Env vars (all optional):
  SCAN_WATCHLIST       path to watchlist file (one symbol per line). Default watchlist.txt
  SCAN_RULES           path to ruleset YAML. Default rules.yaml
  SCAN_BACKEND         'yfinance' (default, no key) | 'finnhub'
  FINNHUB_API_KEY      required only if SCAN_BACKEND=finnhub
  SCAN_LOOKBACK_DAYS   bars of daily history to pull (default 260 ~ 1y for 52w + SMA200)
  SCAN_RSI_PERIOD      default 14
  SCAN_SMA_FAST        default 20
  SCAN_SMA_SLOW        default 50
  SCAN_VOL_WINDOW      avg-volume window (default 20)
  SCAN_INTERVAL_S      poll seconds for --watch mode (default 900 = 15 min)
  TELEGRAM_BOT_TOKEN   optional — enables Telegram delivery
  TELEGRAM_CHAT_ID     optional — target chat for Telegram delivery
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WATCHLIST    = Path(os.getenv("SCAN_WATCHLIST", ROOT / "watchlist.txt"))
RULES        = Path(os.getenv("SCAN_RULES", ROOT / "rules.yaml"))
BACKEND      = os.getenv("SCAN_BACKEND", "yfinance").lower()
LOOKBACK     = int(os.getenv("SCAN_LOOKBACK_DAYS", "260"))
RSI_PERIOD   = int(os.getenv("SCAN_RSI_PERIOD", "14"))
SMA_FAST     = int(os.getenv("SCAN_SMA_FAST", "20"))
SMA_SLOW     = int(os.getenv("SCAN_SMA_SLOW", "50"))
VOL_WINDOW   = int(os.getenv("SCAN_VOL_WINDOW", "20"))
INTERVAL_S   = int(os.getenv("SCAN_INTERVAL_S", "900"))
