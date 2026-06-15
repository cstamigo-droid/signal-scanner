"""Indicator math — pure pandas/numpy, no TA-Lib dependency.

compute(df) turns a daily OHLCV frame into the flat dict of indicators the rule
engine evaluates. Every value is computed from data known at the last closed bar
(no look-ahead): the scanner reacts to completed bars, not the forming one.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from . import config


def rsi(close: pd.Series, n: int) -> float | None:
    if len(close) < n + 1:
        return None
    delta = close.diff()
    up = delta.clip(lower=0.0)
    down = (-delta).clip(lower=0.0)
    roll_up = up.rolling(n).mean()
    roll_down = down.rolling(n).mean()
    rs = roll_up / roll_down.replace(0.0, np.nan)
    out = 100 - 100 / (1 + rs)
    val = out.iloc[-1]
    return float(val) if pd.notna(val) else None


def sma(close: pd.Series, n: int) -> pd.Series:
    return close.rolling(n).mean()


def _last(s: pd.Series) -> float | None:
    v = s.iloc[-1] if len(s) else np.nan
    return float(v) if pd.notna(v) else None


def compute(df: pd.DataFrame) -> dict[str, Any]:
    """Return a flat dict of indicators for a single symbol's daily OHLCV frame."""
    if df is None or len(df) < 2:
        return {}
    close = df["close"].astype(float)
    vol = df["volume"].astype(float) if "volume" in df else pd.Series(dtype=float)

    price = _last(close)
    prev = float(close.iloc[-2]) if len(close) >= 2 else None
    pct_change = ((price - prev) / prev * 100.0) if (price and prev) else None

    rsi_val = rsi(close, config.RSI_PERIOD)
    sma_f = sma(close, config.SMA_FAST)
    sma_s = sma(close, config.SMA_SLOW)
    sma_fast, sma_slow = _last(sma_f), _last(sma_s)

    sma_cross = None
    if len(sma_f) >= 2 and len(sma_s) >= 2:
        f0, f1 = sma_f.iloc[-2], sma_f.iloc[-1]
        s0, s1 = sma_s.iloc[-2], sma_s.iloc[-1]
        if pd.notna([f0, f1, s0, s1]).all():
            if f1 > s1 and f0 <= s0:
                sma_cross = "golden"
            elif f1 < s1 and f0 >= s0:
                sma_cross = "death"

    vol_ratio = None
    if len(vol) >= config.VOL_WINDOW + 1:
        avg = vol.rolling(config.VOL_WINDOW).mean().iloc[-1]
        last_vol = vol.iloc[-1]
        if pd.notna(avg) and avg > 0:
            vol_ratio = float(last_vol / avg)

    window_52w = close.tail(252)
    hi_52w = float(window_52w.max()) if len(window_52w) else None
    lo_52w = float(window_52w.min()) if len(window_52w) else None
    pct_from_high = ((price - hi_52w) / hi_52w * 100.0) if (price and hi_52w) else None
    pct_from_low = ((price - lo_52w) / lo_52w * 100.0) if (price and lo_52w) else None

    return {
        "price": round(price, 4) if price is not None else None,
        "pct_change": round(pct_change, 2) if pct_change is not None else None,
        "rsi": round(rsi_val, 1) if rsi_val is not None else None,
        "sma_fast": round(sma_fast, 4) if sma_fast is not None else None,
        "sma_slow": round(sma_slow, 4) if sma_slow is not None else None,
        "sma_cross": sma_cross,
        "vol_ratio": round(vol_ratio, 2) if vol_ratio is not None else None,
        "pct_from_52w_high": round(pct_from_high, 2) if pct_from_high is not None else None,
        "pct_from_52w_low": round(pct_from_low, 2) if pct_from_low is not None else None,
    }
