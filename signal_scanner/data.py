"""Market data — daily OHLCV history per symbol.

v0.1 backend: yfinance (free, no API key). Works for stocks, ETFs, FX (EURUSD=X)
and crypto (BTC-USD). Cached per symbol so a watchlist scan doesn't refetch.

Finnhub backend is reserved (config.BACKEND='finnhub') for a future version; the
indicator engine needs daily history, which the free Finnhub tier doesn't provide,
so history always comes from yfinance for now.
"""
from __future__ import annotations

import pandas as pd

from . import cache, config

_TTL_S = 600.0  # daily bars don't change intraday materially; 10 min is plenty


def _pull_yf(symbol: str) -> pd.DataFrame:
    import yfinance as yf
    period = f"{max(config.LOOKBACK, 60) + 10}d"
    df = yf.download(symbol, period=period, interval="1d",
                     auto_adjust=True, progress=False)
    if df is None or df.empty:
        return pd.DataFrame()
    # yfinance may return MultiIndex columns for a single ticker — flatten.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)
    keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
    df = df[keep].dropna()
    df.index.name = "datetime"
    return df


def history(symbol: str) -> pd.DataFrame:
    """Daily OHLCV for one symbol (cached). Empty frame if unavailable."""
    sym = symbol.strip().upper()
    if not sym:
        return pd.DataFrame()
    try:
        return cache.get_or_fetch(f"hist:{sym}", _TTL_S, lambda: _pull_yf(sym))
    except Exception:
        return pd.DataFrame()
